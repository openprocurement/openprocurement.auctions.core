# -*- coding: utf-8 -*-
from itertools import izip_longest
from barbecue import chef

from openprocurement.auctions.core.plugins.awarding.v3_1.models import Award
from openprocurement.auctions.core.plugins.awarding.v3_1.utils import (
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
    validate_with,
    calculate_business_date
)
from openprocurement.auctions.core.utils import (
    apply_patch,
)
from openprocurement.auctions.core.validation import (
    validate_award_data_post_common,
    validate_patch_award_data,
    validate_patch_award_access,
    validate_patch_award_data_patch_common,
)
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    check_document_existence,
    make_award,
    add_award_route_url,
    set_award_status_unsuccessful
)


class AwardingV3_1ConfiguratorMixin(object):
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

    def start_awarding(self):
        self._start_awarding()

    def get_bids_to_qualify(self, bids):
        len_bids = len(bids)
        if len_bids > self.NUMBER_OF_BIDS_TO_BE_QUALIFIED:
            return self.NUMBER_OF_BIDS_TO_BE_QUALIFIED
        return len_bids

    def back_to_awarding(self):
        """
            Call when we need to qualify another bidder
        """
        return switch_to_next_award(self.request)

    def check_award_status(self, request, award, now):
        """Checking protocol and contract loading by the owner in time."""
        return check_award_status(request, award, now)

    def verificationPeriod(self):
        return {'startDate': get_now()}

    def signingPeriod(self):
        return {'startDate': get_now()}

    def is_bid_valid(self, bid):
        """
        Check if bid is suitable for awarding
        :param bid:
        :rtype: bool
        :return True if bid is valid, otherwise False
        """
        return bid['value'] is not None

    def _start_awarding(self):
        """
            Function create NUMBER_OF_BIDS_TO_BE_QUALIFIED awards objects
            First award always in pending.verification status
            others in pending.waiting status
            In case that only one bid was applied, award object
            in pending.admission status will be created for that bid
        """

        auction = self.context
        auction.status = 'active.qualification'
        now = get_now()

        auction.awardPeriod = type(auction).awardPeriod({'startDate': now})
        awarding_type = self.awarding_type
        valid_bids = [bid for bid in auction.bids if self.is_bid_valid(bid)]

        award_status = 'pending.admission' if len(valid_bids) == 1 and self.pending_admission_for_one_bid else 'pending'

        bids = chef(valid_bids, auction.features or [], [], True)
        bids_to_qualify = self.get_bids_to_qualify(bids)
        for bid, status in izip_longest(bids[:bids_to_qualify], [award_status], fillvalue='pending.waiting'):
            bid = bid.serialize()
            award = make_award(self.request, auction, bid, status, now, parent=True)

            if bid['status'] == 'invalid':
                set_award_status_unsuccessful(award, now)
            if award.status == 'pending':
                award.verificationPeriod = self.verificationPeriod()
                award.signingPeriod = self.signingPeriod()
                add_award_route_url(self.request, auction, award, awarding_type)
            if award.status == 'pending.admission':
                award.admissionPeriod = {
                    'startDate': now,
                    'endDate': calculate_business_date(
                        now, self.VERIFY_ADMISSION_PROTOCOL_TIME, auction,
                        True, self.AWARDING_PERIODS_END_DATE_HOUR
                    )
                }
                add_award_route_url(self.request, auction, award, awarding_type)
            auction.awards.append(award)
        return True


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
        validate_patch_award_access,
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
            auction.contracts.append(type(auction).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'value': award.value,
                'date': get_now(),
                'items': auction.items,
                'contractID': '{}-{}{}'.format(
                    auction.auctionID,
                    server_id,
                    len(auction.contracts) + 1
                ),
                'signingPeriod': award.signingPeriod,
            }))
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
