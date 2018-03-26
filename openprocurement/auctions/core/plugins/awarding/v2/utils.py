from barbecue import chef

from openprocurement.api.models import TZ
from openprocurement.api.utils import (
    get_now
)

from openprocurement.auctions.core.plugins.awarding.base.constants import (
    NUMBER_OF_BIDS_TO_BE_QUALIFIED
)

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
    for i in xrange(0, bids_to_qualify):
        status = 'pending.waiting'
        if i == 0:
            status = 'pending.verification'
        bid = bids[i].serialize()
        award = make_award(request, auction, status, bid, now)
        if bid['status'] == 'invalid':
            award.status = 'unsuccessful'
            award.complaintPeriod.endDate = now
        if award.status == 'pending.verification':
            award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': now}
            add_award_route_url(request, auction, award, awarding_type)
        auction.awards.append(award)


def switch_to_next_award(request):
    auction = request.validated['auction']
    now = get_now()
    awarding_type = request.content_configurator.awarding_type
    waiting_awards = [i for i in auction.awards if i['status'] == 'pending.waiting']

    if waiting_awards:
        award = waiting_awards[0]
        award.status = 'pending.verification'
        award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': now}
        award = award.serialize()
        add_award_route_url(request, auction, award, awarding_type)
    elif all([award.status in ['cancelled', 'unsuccessful'] for award in auction.awards]):
        auction.awardPeriod.endDate = now
        auction.status = 'unsuccessful'


def next_check_awarding(auction):
    checks = []
    if awarded_predicate(auction):
        standStillEnds = [a.complaintPeriod.endDate.astimezone(TZ) for a in auction.awards if a.complaintPeriod.endDate]
        for award in auction.awards:
            if award.status == 'active':
                checks.append(award.signingPeriod.endDate.astimezone(TZ))

        last_award_status = auction.awards[-1].status if auction.awards else ''
        if standStillEnds and last_award_status == 'unsuccessful':
            checks.append(max(standStillEnds))
    elif not auction.lots and auction.status == 'active.qualification':
        for award in auction.awards:
            if award.status == 'pending.verification':
                checks.append(award.verificationPeriod.endDate.astimezone(TZ))
            elif award.status == 'pending.payment':
                checks.append(award.paymentPeriod.endDate.astimezone(TZ))
    elif awarded_and_lots_predicate(auction):
        checks = check_lots_awarding(auction)
    return min(checks) if checks else None


def check_award_status(request, award, now):
    """Checking required documents loading and payment recieving in time."""
    auction = request.validated['auction']
    protocol_overdue = (award.status == 'pending.verification' and
                        award['verificationPeriod']['endDate'] < now)
    contract_overdue = (award.status == 'active' and
                        award['signingPeriod']['endDate'] < now)
    payment_overdue = (award.status == 'pending.payment' and
                       award['paymentPeriod']['endDate'] < now)
    if protocol_overdue or contract_overdue or payment_overdue:
        set_unsuccessful_award(request, auction, award)
