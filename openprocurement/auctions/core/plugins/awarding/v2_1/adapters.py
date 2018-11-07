# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    validate_with,
    error_handler,
    get_now,
)

from .models import Award
from .utils import (
    create_awards,
    next_check_awarding,
    switch_to_next_award,
)

from openprocurement.auctions.core.adapters import (
    AuctionAwardingNextCheckAdapter,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
)
from openprocurement.auctions.core.validation import (
    validate_patch_award_data,
)
from openprocurement.auctions.core.plugins.awarding.v2_1.validators import (
    validate_award_patch
)
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    check_document_existence
)
from openprocurement.auctions.core.plugins.awarding.base.adapters import (
    BaseAwardManagerAdapter,
)


class AwardingV2_1ConfiguratorMixin(object):
    """ Brings methods that are needed for the process of Awarding

        start_awarding - call after auction ends in auction view
        back_to_awarding - call when participant was disqualified
    """
    award_model = Award
    awarding_type = 'awarding_2_1'

    def start_awarding(self):
        """
            Call create_awards method, that create 2 awards for 2 bidders
        """
        return create_awards(self.request)

    def back_to_awarding(self):
        """
            Call when we need to qualify another biddder
        """
        return switch_to_next_award(self.request)


class AwardingNextCheckV2_1(AuctionAwardingNextCheckAdapter):
    """Use next_check_awarding from V2 awarding"""
    def add_awarding_checks(self, auction):
        return next_check_awarding(auction)


class AwardManagerV2_1Adapter(BaseAwardManagerAdapter):

    name = "Award v-2_1 adapter"

    change_validators = (
        validate_patch_award_data,
        validate_award_patch,
    )

    def create_award(self, request, **kwargs):
        auction = request.validated['auction']
        award = request.validated['award']

        if auction.status != 'active.qualification':
            request.errors.add(
                'body',
                'data',
                'Can\'t create award in current ({}) auction status'.format(auction.status)
            )
            request.errors.status = 403
            raise error_handler(request)
        if any([i.status != 'active' for i in auction.lots if i.id == award.lotID]):
            request.errors.add('body', 'data', 'Can create award only in active lot status')
            request.errors.status = 403
            raise error_handler(request)
        now = get_now()
        award.verificationPeriod = award.paymentPeriod = award.signingPeriod = {'startDate': now}
        award.complaintPeriod = award.signingPeriod
        auction.awards.append(award)

    @validate_with(change_validators)
    def change_award(self, request, **kwargs):
        auction = request.validated['auction']
        award = request.context
        server_id = kwargs['server_id']

        current_award_status = award.status
        apply_patch(request, save=False, src=request.context.serialize())
        now = get_now()
        if current_award_status == 'pending.waiting' and award.status == 'cancelled':
            if request.authenticated_role == 'bid_owner':
                award.complaintPeriod.endDate = now
            else:
                request.errors.add(
                    'body',
                    'data',
                    'Only bid owner may cancel award in current ({}) status'.format(current_award_status))
                request.errors.status = 403
                raise error_handler(request)
        elif current_award_status == 'pending.verification' and award.status == 'pending.payment':
            if check_document_existence(award, 'auctionProtocol'):
                award.verificationPeriod.endDate = now
            else:
                request.errors.add(
                    'body',
                    'data',
                    'Can\'t switch award status to (pending.payment) before auction owner load auction protocol')
                request.errors.status = 403
                raise error_handler(request)
        elif current_award_status == 'pending.payment' and award.status == 'active':
            award.complaintPeriod.endDate = award.paymentPeriod.endDate = now
            auction.contracts.append(type(auction).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'date': now,
                'items': [i for i in auction.items if i.relatedLot == award.lotID],
                'contractID': '{}-{}{}'.format(
                    auction.auctionID,
                    server_id,
                    len(auction.contracts) + 1
                )
            }))
            auction.status = 'active.awarded'
            auction.awardPeriod.endDate = now
        elif current_award_status != 'pending.waiting' and award.status == 'unsuccessful':
            if current_award_status == 'pending.verification':
                award.verificationPeriod.endDate = \
                    award.complaintPeriod.endDate = \
                    award.paymentPeriod.endDate = \
                    award.signingPeriod.endDate = \
                    now
            elif current_award_status == 'pending.payment':
                award.paymentPeriod.endDate = now
            elif current_award_status == 'active':
                award.signingPeriod.endDate = now
                auction.awardPeriod.endDate = None
                auction.status = 'active.qualification'
                for i in auction.contracts:
                    if i.awardID == award.id:
                        i.status = 'cancelled'
            award.complaintPeriod.endDate = now
            request.content_configurator.back_to_awarding()
        elif current_award_status != award.status:
            request.errors.add(
                'body',
                'data',
                'Can\'t switch award ({}) status to ({}) status'.format(
                    current_award_status,
                    award.status
                )
            )
            request.errors.status = 403
            raise error_handler(request)
