from itertools import izip_longest
from barbecue import chef

from openprocurement.api.models import TZ
from openprocurement.api.utils import (
    get_now
)

from openprocurement.auctions.core.plugins.awarding.base.constants import (
    NUMBER_OF_BIDS_TO_BE_QUALIFIED
)
from openprocurement.auctions.core.utils import get_related_contract_of_award
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    check_auction_protocol,
    invalidate_bids_under_threshold,
    make_award,
    check_lots_awarding,
    set_unsuccessful_award,
    add_award_route_url
)

from openprocurement.auctions.core.plugins.awarding.base.predicates import (
    awarded_predicate,
    awarded_and_lots_predicate
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
    bids_to_qualify = NUMBER_OF_BIDS_TO_BE_QUALIFIED if (len(bids) > NUMBER_OF_BIDS_TO_BE_QUALIFIED) else len(bids)

    for bid, status in izip_longest(bids[:bids_to_qualify],
                                    ['pending'],
                                    fillvalue='pending.waiting'):
        bid = bid.serialize()
        award = make_award(request, auction, status, bid, now)
        if bid['status'] == 'invalid':
            award.status = 'unsuccessful'
            award.complaintPeriod.endDate = now
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
    if awarded_predicate(auction):
        standStillEnds = [a.complaintPeriod.endDate.astimezone(TZ) for a in auction.awards if a.complaintPeriod.endDate]
        for contract in auction.contracts:
            if contract.status == 'pending':
                checks.append(contract.signingPeriod.endDate.astimezone(TZ))
        last_award_status = auction.awards[-1].status if auction.awards else ''
        if standStillEnds and last_award_status == 'unsuccessful':
            checks.append(max(standStillEnds))
    elif not auction.lots and auction.status == 'active.qualification':
        for award in auction.awards:
            if award.status == 'pending':
                checks.append(award.verificationPeriod.endDate.astimezone(TZ))
    elif awarded_and_lots_predicate(auction):
        checks = check_lots_awarding(auction)
    return min(checks) if checks else None


def check_contract_overdue(contract, now):
    return (
        contract.status == 'pending' and
        contract['signingPeriod']['endDate'] < now
    )

def check_protocol_overdue(award, now):
    return (
        award.status == 'pending' and
        award['verificationPeriod']['endDate'] < now
    )

def check_award_status(request, award, now):
    """Checking protocol and contract loading by the owner in time."""
    auction = request.validated['auction']

    protocol_overdue = check_protocol_overdue(award, now)

    # seek for contract overdue
    related_contract = get_related_contract_of_award(award['id'], auction)

    contract_overdue = check_contract_overdue(related_contract, now) if related_contract else None

    if protocol_overdue or contract_overdue:
        set_unsuccessful_award(request, auction, award)
