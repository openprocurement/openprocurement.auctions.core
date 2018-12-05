# -*- coding: utf-8 -*-
from .models import Award
from .utils import (
    switch_to_next_award,
    next_check_awarding,
    check_award_status
)

from datetime import timedelta
from openprocurement.auctions.core.adapters import (
    AuctionAwardingNextCheckAdapter
)
from openprocurement.auctions.core.plugins.awarding.base.adapters import (
    BaseAwardManagerAdapter
)
from openprocurement.api.utils import (
    get_now,
    error_handler,
    validate_with
)
from openprocurement.auctions.core.utils import (
    apply_patch,
)
from openprocurement.auctions.core.validation import (
    validate_award_data_post_common,
    validate_patch_award_data,
    validate_patch_award_data_patch_common,
)
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    check_document_existence
)
from openprocurement.auctions.core.plugins.awarding.base.adapters import (
    BaseAwardingMixin
)


class AwardingV3_1ConfiguratorMixin(BaseAwardingMixin):
    """Brings methods that are needed for the process of Awarding

        start_awarding - call after auction ends in auction view
        back_to_awarding - call when participant was disqualified
    """
    award_model = Award
    awarding_type = 'awarding_3_1'
    pending_admission_for_one_bid = True
    AWARDING_PERIODS_END_DATE_HOUR = 18
    VERIFY_ADMISSION_PROTOCOL_TIME = timedelta(days=5)
    NUMBER_OF_BIDS_TO_BE_QUALIFIED = 2

    def back_to_awarding(self):
        """
            Call when we need to qualify another bidder
        """
        return switch_to_next_award(self.request)

    def check_award_status(self, request, award, now):
        """Checking protocol and contract loading by the owner in time."""
        return check_award_status(request, award, now)


class AwardingNextCheckV3_1(AuctionAwardingNextCheckAdapter):
    """Use next_check_awarding from V3 awarding"""
    def add_awarding_checks(self, auction):
        return next_check_awarding(auction)


class AwardManagerV3_1Adapter(BaseAwardManagerAdapter):

    name = 'Award v-3_1 adapter'

    create_validators = (
        validate_award_data_post_common,
    )

    change_validators = (
        validate_patch_award_data,
        validate_patch_award_data_patch_common,
    )

    @validate_with(create_validators)
    def create_award(self, request, **kwargs):
        award = request.validated['award']
        award.complaintPeriod = award.signingPeriod = award.verificationPeriod = {
            'startDate': get_now()
        }
        request.validated['auction'].awards.append(award)

    @validate_with(change_validators)
    def change_award(self, request, **kwargs):
        auction = request.validated['auction']
        award = request.context
        current_award_status = award.status
        server_id = kwargs['server_id']

        now = get_now()
        if current_award_status in ['unsuccessful', 'cancelled', 'active']:
            request.errors.add(
                'body',
                'data',
                'Can\'t update award in current ({}) status'.format(current_award_status)
            )
            request.errors.status = 403
            raise error_handler(request)

        apply_patch(request, save=False, src=request.context.serialize())
        new_award_status = award.status

        if current_award_status == 'pending.waiting' and new_award_status == 'cancelled':
            if request.authenticated_role == 'bid_owner':
                award.complaintPeriod.endDate = now
            else:
                request.errors.add(
                    'body',
                    'data',
                    'Only bid owner may cancel award in current ({}) status'.format(current_award_status)
                )
                request.errors.status = 403
                raise error_handler(request)

        elif current_award_status == 'pending.admission' and new_award_status == 'pending':
            if check_document_existence(award, 'admissionProtocol'):
                award.admissionPeriod.endDate = now
                award.signingPeriod = award.verificationPeriod = {'startDate': now}
            else:
                request.errors.add(
                    'body',
                    'data',
                    'Can\'t switch award status to (pending) before'
                    ' auction owner load admission protocol'
                )
                request.errors.status = 403
                raise error_handler(request)

        elif current_award_status == 'pending' and new_award_status == 'active':
            if check_document_existence(award, 'auctionProtocol'):
                award.verificationPeriod.endDate = now
            else:
                request.errors.add(
                    'body',
                    'data',
                    'Can\'t switch award status to (active) before'
                    ' auction owner load auction protocol'
                )
                request.errors.status = 403
                raise error_handler(request)

            award.complaintPeriod.endDate = now
            new_contract_data = {
                'awardID': award.id,
                'suppliers': award.suppliers,
                'date': now,
                'items': auction.items,
                'contractID': '{}-{}{}'.format(
                    auction.auctionID,
                    server_id,
                    len(auction.contracts) + 1
                ),
                'signingPeriod': award.signingPeriod,
            }
            if self.COPY_AWARD_VALUE_TO_CONTRACT:
                new_contract_data['value'] = award.value

            auction.contracts.append(type(auction).contracts.model_class(new_contract_data))
            auction.status = 'active.awarded'
            auction.awardPeriod.endDate = now

        elif current_award_status != 'pending.waiting' and new_award_status == 'unsuccessful':
            if not (check_document_existence(award, 'rejectionProtocol') or
                    check_document_existence(award, 'act')):
                request.errors.add(
                    'body',
                    'data',
                    'Can\'t switch award status to (unsuccessful) before'
                    ' auction owner load reject protocol or act'
                )
                request.errors.status = 403
                raise error_handler(request)
            if current_award_status == 'pending.admission':
                award.admissionPeriod.endDate = now
            elif current_award_status == 'pending':
                award.verificationPeriod.endDate = now
            award.complaintPeriod.endDate = now
            request.content_configurator.back_to_awarding()

        elif current_award_status != new_award_status:
            request.errors.add(
                'body',
                'data',
                'Can\'t switch award ({0}) status to ({1}) status'.format(
                    current_award_status,
                    new_award_status
                )
            )
            request.errors.status = 403
            raise error_handler(request)
