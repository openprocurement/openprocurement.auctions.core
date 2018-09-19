# -*- coding: utf-8 -*-
from openprocurement.api.constants import TZ
from openprocurement.auctions.core.plugins.awarding.base.constants import (
    NUMBER_OF_BIDS_TO_BE_QUALIFIED
)


def check_document_existence(award, document_type):
    if award.documents:
        for document in award.documents:
            if (
                document['documentType'] == document_type
                and document['author'] == 'auction_owner'
            ):
                return True
    return False


def invalidate_bids_under_threshold(auction):
    value_threshold = auction['value']['amount'] + auction['minimalStep']['amount']
    for bid in auction['bids']:
        if bid['value']['amount'] < value_threshold:
            bid['status'] = 'invalid'


def make_award(request, auction, bid, status, now, lot_id=None, parent=None):
    data = {}
    if parent:
        data['__parent__'] = request.context
    data['bid_id'] = bid['id']
    data['status'] = status
    data['date'] = now
    data['value'] = bid['value']
    data['suppliers'] = bid['tenderers']
    data['complaintPeriod'] = {'startDate': now.isoformat()}
    if lot_id:
        data['lotID'] = lot_id
    award = type(auction).awards.model_class(data)
    return award


def check_pending_awards_complaints(auction, lot_awards):
    for complain in auction.complaints:
        if complain['status'] in auction.block_complaint_status:
            if complain.relatedLot == lot_awards.id:
                return True


def check_pending_complaints(auction, lot_awards):
    for award in lot_awards:
        for item in award.complaints:
            if item.status in auction.block_complaint_status:
                return True


def set_stand_still_ends(awards):
    stand_still_ends = []
    for award in awards:
        if award.complaintPeriod.endDate:
            stand_still_ends.append(award.complaintPeriod.endDate.astimezone(TZ))
    return stand_still_ends


def check_lots_awarding(auction):
    checks = []
    for lot in auction.lots:
        if lot['status'] != 'active':
            continue
        lot_awards = [i for i in auction.awards if i.lotID == lot.id]
        pending_complaints = check_pending_complaints(auction, lot_awards)
        pending_awards_complaints = check_pending_awards_complaints(auction, lot_awards)
        stand_still_ends = set_stand_still_ends(lot_awards)
        last_award_status = lot_awards[-1].status if lot_awards else ''
        if (
            not pending_complaints
            and not pending_awards_complaints
            and stand_still_ends
            and last_award_status == 'unsuccessful'
        ):
            checks.append(max(stand_still_ends))
    return checks


def set_award_status_unsuccessful(award, now):
    award.status = 'unsuccessful'
    award.complaintPeriod.endDate = now


def set_unsuccessful_award(request, auction, award, now):
    if award.status == 'active':
        auction.awardPeriod.endDate = None
        auction.status = 'active.qualification'
        for contract in auction.contracts:
            if contract.awardID == award.id:
                contract.status = 'cancelled'
    set_award_status_unsuccessful(award, now)
    request.content_configurator.back_to_awarding()


def add_award_route_url(request, auction, award, awarding_type):
    default_route_name = 'Auction Awards'
    try:
        custom_route_name = '{}:{}'.format(awarding_type, default_route_name)
        route_url = request.route_url(custom_route_name, auction_id=auction.id, award_id=award['id'])
    except KeyError:
        route_url = request.route_url(default_route_name, auction_id=auction.id, award_id=award['id'])
    request.response.headers['Location'] = route_url
    return True


def get_bids_to_qualify(bids):
    len_bids = len(bids)
    if len_bids > NUMBER_OF_BIDS_TO_BE_QUALIFIED:
        return NUMBER_OF_BIDS_TO_BE_QUALIFIED
    return len_bids
