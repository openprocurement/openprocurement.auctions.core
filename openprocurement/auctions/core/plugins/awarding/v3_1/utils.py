# -*- coding: utf-8 -*-
from openprocurement.api.constants import TZ
from openprocurement.api.utils import (
    get_now,
    calculate_business_date
)

from openprocurement.auctions.core.interfaces import IAuctionManager
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    check_lots_awarding,
    add_award_route_url,
    set_unsuccessful_award,
)

from openprocurement.auctions.core.plugins.awarding.base.predicates import (
    awarded_and_lots_predicate,
    admission_overdue_predicate
)


def switch_to_next_award(request):
    auction = request.validated['auction']
    adapter = request.registry.getAdapter(auction, IAuctionManager)
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
        adapter.pendify_auction_status('unsuccessful')


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
