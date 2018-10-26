# -*- coding: utf-8 -*-
from itertools import izip_longest
from barbecue import chef
from openprocurement.api.utils import (
    get_now,
    calculate_business_date
)
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    make_award,
    add_award_route_url,
    set_award_status_unsuccessful
)


class BaseAwardManagerAdapter(object):
    name = 'Award Manager'

    def __init__(self, context):
        self.context = context


class BaseAwardingMixin(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context

    def get_bids_to_qualify(self, bids):
        len_bids = len(bids)
        if len_bids > self.NUMBER_OF_BIDS_TO_BE_QUALIFIED:
            return self.NUMBER_OF_BIDS_TO_BE_QUALIFIED
        return len_bids

    def start_awarding(self):
        auction = self.context
        auction.status = 'active.qualification'
        now = get_now()
        self._start_awarding = now

        auction.awardPeriod = type(auction).awardPeriod({'startDate': now})
        awarding_type = self.awarding_type
        valid_bids = [bid for bid in auction.bids if bid['value'] is not None]

        award_status = 'pending.admission' if len(valid_bids) == 1 and self.pending_admission_for_one_bid else 'pending'

        bids = chef(valid_bids, auction.features or [], [], True)
        bids_to_qualify = self.get_bids_to_qualify(bids)
        for bid, status in izip_longest(bids[:bids_to_qualify], [award_status], fillvalue='pending.waiting'):
            bid = bid.serialize()
            award = make_award(self.request, auction, bid, status, now, parent=True)

            if bid['status'] == 'invalid':
                set_award_status_unsuccessful(award, now)
            if award.status == 'pending':
                if getattr(self, 'verificationPeriod', None):
                    award.verificationPeriod = self.verificationPeriod
                else:
                    award.verificationPeriod = {'startDate': now}
                if getattr(self, 'signingPeriod', None):
                    award.signingPeriod = self.signingPeriod
                else:
                    award.signingPeriod = {'startDate': now}
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
