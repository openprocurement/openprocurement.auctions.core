# -*- coding: utf-8 -*-
from itertools import izip_longest
from barbecue import chef

from openprocurement.api.constants import TZ
from openprocurement.api.utils import (
    get_now,
    calculate_business_date
)

from openprocurement.auctions.core.plugins.awarding.base.utils import (
    make_award,
    check_lots_awarding,
    add_award_route_url,
    set_unsuccessful_award,
    set_award_status_unsuccessful,
    get_bids_to_qualify
)

from openprocurement.auctions.core.plugins.awarding.v3_1.constants import (
    AWARDING_PERIODS_END_DATE_HOUR,
    VERIFY_ADMISSION_PROTOCOL_TIME
)
from openprocurement.auctions.core.plugins.awarding.base.predicates import (
    awarded_predicate,
    awarded_and_lots_predicate,
    admission_overdue_predicate
)


def create_awards(request):
    """
        Function create NUMBER_OF_BIDS_TO_BE_QUALIFIED awards objects
        First award always in pending.verification status
        others in pending.waiting status
        In case that only one bid was applied, award object
        in pending.admission status will be created for that bid
    """
    auction = request.validated['auction']
    auction.status = 'active.qualification'
    now = get_now()
    auction.awardPeriod = type(auction).awardPeriod({'startDate': now})
    awarding_type = request.content_configurator.awarding_type
    valid_bids = [bid for bid in auction.bids if bid['value'] is not None]
    if len(valid_bids) == 1:
        bid = valid_bids[0].serialize()
        award = make_award(request, auction, bid, 'pending.admission', now, parent=True)
        if bid['status'] == 'invalid':
            set_award_status_unsuccessful(award, now)
        if award.status == 'pending.admission':
            award.admissionPeriod = {
                'startDate': now,
                'endDate': calculate_business_date(
                    now, VERIFY_ADMISSION_PROTOCOL_TIME, auction,
                    True, AWARDING_PERIODS_END_DATE_HOUR
                )
            }
            add_award_route_url(request, auction, award, awarding_type)
        auction.awards.append(award)
    else:
        bids = chef(valid_bids, auction.features or [], [], True)
        bids_to_qualify = get_bids_to_qualify(bids)
        for bid, status in izip_longest(bids[:bids_to_qualify], ['pending'], fillvalue='pending.waiting'):
            bid = bid.serialize()
            award = make_award(request, auction, bid, status, now, parent=True)
            if bid['status'] == 'invalid':
                set_award_status_unsuccessful(award, now)
            if award.status == 'pending':
                award.signingPeriod = award.verificationPeriod = {'startDate': now}
                add_award_route_url(request, auction, award, awarding_type)
            auction.awards.append(award)


def switch_to_next_award(request):
    auction = request.validated['auction']
    now = get_now()
    awarding_type = request.content_configurator.awarding_type
    waiting_awards = [i for i in auction.awards if i['status'] == 'pending.waiting']

    if waiting_awards:
        award = waiting_awards[0]
        award.status = 'pending'
        award.signingPeriod = award.verificationPeriod = {'startDate': now}
        award = award.serialize()
        add_award_route_url(request, auction, award, awarding_type)
    elif all([award.status in ['cancelled', 'unsuccessful'] for award in auction.awards]):
        auction.awardPeriod.endDate = now
        auction.status = 'unsuccessful'


def next_check_awarding(auction):
    checks = []
    if not auction.lots and auction.status == 'active.qualification':
        for award in auction.awards:
            if award.status == 'pending.admission':
                checks.append(award.admissionPeriod.endDate.astimezone(TZ))
    elif awarded_and_lots_predicate(auction):
        checks = check_lots_awarding(auction)
    return min(checks) if checks else None


def check_award_status(request, award, now):
    """Checking admission protocol loading by the owner in time."""
    auction = request.validated['auction']
    admission_protocol_overdue = admission_overdue_predicate(award, 'pending.admission', now)

    if admission_protocol_overdue:
        set_unsuccessful_award(request, auction, award, now)
