from itertools import izip_longest
from barbecue import chef

from openprocurement.api.models import TZ
from openprocurement.api.utils import (
    get_now,
    get_awarding_type_by_procurement_method_type
)

from openprocurement.auctions.core.utils import get_related_contract_of_award
from openprocurement.auctions.core.plugins.awarding.v2.constants import (
    NUMBER_OF_BIDS_TO_BE_QUALIFIED
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
    awarding_type = get_awarding_type_by_procurement_method_type(
        auction.procurementMethodType
    )
    valid_bids = [bid for bid in auction.bids if bid['value'] is not None]
    bids = chef(valid_bids, auction.features or [], [], True)
    bids_to_qualify = NUMBER_OF_BIDS_TO_BE_QUALIFIED if (len(bids) > NUMBER_OF_BIDS_TO_BE_QUALIFIED) else len(bids)

    for bid, status in izip_longest(bids[:bids_to_qualify],
                                    ['pending'],
                                    fillvalue='pending.waiting'):
        bid = bid.serialize()
        award = type(auction).awards.model_class({
            '__parent__': request.context,
            'bid_id': bid['id'],
            'status': status,
            'date': now,
            'value': bid['value'],
            'suppliers': bid['tenderers'],
            'complaintPeriod': {'startDate': now}
        })
        if bid['status'] == 'invalid':
            award.status = 'unsuccessful'
            award.complaintPeriod.endDate = now
        if award.status == 'pending':
            award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': now}
            request.response.headers['Location'] = request.route_url(
                '{}:Auction Awards'.format(awarding_type),
                auction_id=auction.id, award_id=award['id']
            )
        auction.awards.append(award)


def switch_to_next_award(request):
    auction = request.validated['auction']
    now = get_now()
    awarding_type = get_awarding_type_by_procurement_method_type(
        auction.procurementMethodType
    )
    waiting_awards = [i for i in auction.awards if i['status'] == 'pending.waiting']
    if waiting_awards:
        award = waiting_awards[0]
        award.status = 'pending'
        award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': now}
        award = award.serialize()
        request.response.headers['Location'] = request.route_url(
            '{}:Auction Awards'.format(awarding_type),
            auction_id=auction.id,
            award_id=award['id']
        )

    elif all([award.status in ['cancelled', 'unsuccessful'] for award in auction.awards]):
        auction.awardPeriod.endDate = now
        auction.status = 'unsuccessful'


def check_auction_protocol(award):
    if award.documents:
        for document in award.documents:
            if document['documentType'] == 'auctionProtocol' and document['author'] == 'auction_owner':
                return True
    return False


def next_check_awarding(auction):
    checks = []
    if not auction.lots and auction.status == 'active.qualification':
        for award in auction.awards:
            if award.status == 'pending':
                checks.append(award.verificationPeriod.endDate.astimezone(TZ))
    elif not auction.lots and auction.status == 'active.awarded' and not any([
            i.status in auction.block_complaint_status
            for i in auction.complaints
        ]) and not any([
            i.status in auction.block_complaint_status
            for a in auction.awards
            for i in a.complaints]):
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        for contract in auction.contracts:
            if contract.status == 'pending':
                checks.append(contract.signingPeriod.endDate.astimezone(TZ))

        last_award_status = auction.awards[-1].status if auction.awards else ''
        if standStillEnds and last_award_status == 'unsuccessful':
            checks.append(max(standStillEnds))
    elif auction.lots and auction.status in ['active.qualification', 'active.awarded'] and not any([
            i.status in auction.block_complaint_status and i.relatedLot is None
            for i in auction.complaints]):
        for lot in auction.lots:
            if lot['status'] != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            pending_complaints = any([
                i['status'] in auction.block_complaint_status and i.relatedLot == lot.id
                for i in auction.complaints
            ])
            pending_awards_complaints = any([
                i.status in auction.block_complaint_status
                for a in lot_awards
                for i in a.complaints
            ])
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if a.complaintPeriod.endDate
            ]
            last_award_status = lot_awards[-1].status if lot_awards else ''
            if (
                not pending_complaints
                and not pending_awards_complaints
                and standStillEnds
                and last_award_status == 'unsuccessful'
            ):
                checks.append(max(standStillEnds))
    return min(checks) if checks else None


def invalidate_bids_under_threshold(auction):
    value_threshold = round(auction['value']['amount'] + auction['minimalStep']['amount'], 2)
    for bid in auction['bids']:
        if bid['value']['amount'] < value_threshold:
            bid['status'] = 'invalid'

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

    contract_overdue = check_contract_overdue(
        related_contract, 
        now
    ) if related_contract else None # award could have not a contract

    if protocol_overdue or contract_overdue:
        if award.status == 'active':
            auction.awardPeriod.endDate = None
            auction.status = 'active.qualification'
            for contract in auction.contracts:
                if contract.awardID == award.id:
                    contract.status = 'cancelled'
        award.status = 'unsuccessful'
        award.complaintPeriod.endDate = now
        request.content_configurator.back_to_awarding()
