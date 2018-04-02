from itertools import izip_longest
from barbecue import chef

from openprocurement.api.models import TZ
from openprocurement.api.utils import (
    get_now
)

from openprocurement.auctions.core.utils import get_related_contract_of_award
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    check_auction_protocol,
    invalidate_bids_under_threshold,
    make_award,
    check_lots_awarding,
    add_award_route_url,
    set_stand_still_ends,
    set_unsuccessful_award,
    get_bids_to_qualify,
    set_award_status_unsuccessful,
    set_auction_status_unsuccessful
)

from openprocurement.auctions.core.plugins.awarding.base.predicates import (
    awarded_predicate,
    awarded_and_lots_predicate,
    contract_overdue_predicate,
    protocol_overdue_predicate
)


def create_awards(request):
    """
        Function create NUMBER_OF_BIDS_TO_BE_QUALIFIED awards objects
        First award always in pending.verification status
        others in pending.waiting status
    """
    auction = request.validated['auction']
    auction.status = 'active.qualification'
    now = get_now()
    auction.awardPeriod = type(auction).awardPeriod({'startDate': now})
    awarding_type = request.content_configurator.awarding_type
    valid_bids = [bid for bid in auction.bids if bid['value'] is not None]
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
        set_auction_status_unsuccessful(auction)

def next_check_awarding(auction):
    checks = []
    if awarded_predicate(auction):
        stand_still_ends = set_stand_still_ends(auction.awards)
        for contract in auction.contracts:
            if contract.status == 'pending':
                checks.append(contract.signingPeriod.endDate.astimezone(TZ))
        last_award_status = auction.awards[-1].status if auction.awards else ''
        if stand_still_ends and last_award_status == 'unsuccessful':
            checks.append(max(stand_still_ends))
    elif not auction.lots and auction.status == 'active.qualification':
        for award in auction.awards:
            if award.status == 'pending':
                checks.append(award.verificationPeriod.endDate.astimezone(TZ))
    elif awarded_and_lots_predicate(auction):
        checks = check_lots_awarding(auction)
    return min(checks) if checks else None


def check_award_status(request, award, now):
    """Checking protocol and contract loading by the owner in time."""
    auction = request.validated['auction']
    protocol_overdue = protocol_overdue_predicate(award, 'pending', now)
    # seek for contract overdue
    related_contract = get_related_contract_of_award(award['id'], auction)
    contract_overdue = contract_overdue_predicate(related_contract,'pending', now) if related_contract else None

    if protocol_overdue or contract_overdue:
        set_unsuccessful_award(request, auction, award, now)
