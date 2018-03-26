def check_auction_protocol(award):
    if award.documents:
        for document in award.documents:
            if document['documentType'] == 'auctionProtocol' and document['author'] == 'auction_owner':
                return True
    return False


def invalidate_bids_under_threshold(auction):
    value_threshold = round(auction['value']['amount'] + auction['minimalStep']['amount'], 2)
    for bid in auction['bids']:
        if bid['value']['amount'] < value_threshold:
            bid['status'] = 'invalid'


def make_award(request, auction, status, bid, now):
    award = type(auction).awards.model_class({
        'bid_id': bid['id'],
        'status': 'pending',
        'date': now(),
        'value': bid['value'],
        'suppliers': bid['tenderers'],
        'complaintPeriod': {
            'startDate': now().isoformat()
        }
    })
    return award


def check_pending_awards_complaints(auction):
    for complain in auction.complaints:
        if complain['status'] in auction.block_complaint_status:
            if complain.relatedLot == lot.id:
                return True
    return False

def check_pending_awards_complaints(auction):
    for award in lot_awards:
        for item in award.complaints:
            if item.status in auction.block_complaint_status
                return True

def set_stand_still_ends(lot_awards):
    stand_still_ends = []
    for award in lot_awards:
        if award.complaintPeriod.endDate:
            stand_still_ends.append(a.complaintPeriod.endDate.astimezone(TZ))
    return stand_still_ends


def check_lots_awarding(auction):
    checks = []
    for lot in auction.lots:
        if lot['status'] != 'active':
            continue
        lot_awards = [i for i in auction.awards if i.lotID == lot.id]
        pending_complaints = check_pending_awards_complaints(auction)
        pending_awards_complaints = check_pending_awards_complaints(auction, lot_awards)
        stand_still_ends = set_stand_still_ends(lot_awards)
        last_award_status = lot_awards[-1].status if lot_awards else ''
        if (
            not pending_complaints
            and not pending_awards_complaints
            and stand_still_ends
            and last_award_status == 'unsuccessful'
        ):
            checks.append(max(standStillEnds))
    return checks

def set_unsuccessful_award(request, auction, award):
    if award.status == 'active':
        auction.awardPeriod.endDate = None
        auction.status = 'active.qualification'
        for contract in auction.contracts:
            if contract.awardID == award.id:
                contract.status = 'cancelled'
    award.status = 'unsuccessful'
    award.complaintPeriod.endDate = now
    request.content_configurator.back_to_awarding()

def add_award_route_url(request, auction, award, awarding_type):
    route = '{}:Auction Awards'.format(awarding_type), auction_id=auction.id, award_id=award['id']
    request.response.headers['Location'] = request.route_url(route)
    return True

