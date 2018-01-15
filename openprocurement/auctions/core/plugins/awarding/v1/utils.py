# -*- coding: utf-8 -*-
from openprocurement.api.models import TZ
from barbecue import chef
from openprocurement.api.models import get_now


def next_check_awarding(auction, checks):
    '''
        Awarding part of generating next_check field
    '''
    auction_complaints_status = any([i.status in auction.block_complaint_status for i in auction.complaints])
    auction_award_complaints_status = any([i.status in auction.block_complaint_status for a in auction.awards for i in a.complaints])
    auction_complaint_and_relatedLot = any([i.status in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints])
    if not auction.lots and auction.status == 'active.awarded' and not auction_complaints_status and not auction_award_complaints_status:
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        last_award_status = auction.awards[-1].status if auction.awards else ''
        if standStillEnds and last_award_status == 'unsuccessful':
            checks.append(max(standStillEnds))
    elif auction.lots and auction.status in ['active.qualification', 'active.awarded'] and not auction_complaint_and_relatedLot:
        for lot in auction.lots:
            if lot['status'] != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            pending_complaints = any([i['status'] in auction.block_complaint_status and i.relatedLot == lot.id for i in auction.complaints])
            pending_awards_complaints = any([i.status in auction.block_complaint_status for a in lot_awards for i in a.complaints])
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if a.complaintPeriod.endDate
            ]
            last_award_status = lot_awards[-1].status if lot_awards else ''
            if not pending_complaints and not pending_awards_complaints and standStillEnds and last_award_status == 'unsuccessful':
                checks.append(max(standStillEnds))
    return checks


def add_next_award(request):
    auction = request.validated['auction']
    now = get_now()
    if not auction.awardPeriod:
        auction.awardPeriod = type(auction).awardPeriod({})
    if not auction.awardPeriod.startDate:
        auction.awardPeriod.startDate = now
    if auction.lots:
        statuses = set()
        for lot in auction.lots:
            if lot.status != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            if lot_awards and lot_awards[-1].status in ['pending', 'active']:
                statuses.add(lot_awards[-1].status if lot_awards else 'unsuccessful')
                continue
            lot_items = [i.id for i in auction.items if i.relatedLot == lot.id]
            features = [
                i
                for i in (auction.features or [])
                if i.featureOf == 'tenderer' or i.featureOf == 'lot' and i.relatedItem == lot.id or i.featureOf == 'item' and i.relatedItem in lot_items
            ]
            codes = [i.code for i in features]
            bids = [
                {
                    'id': bid.id,
                    'value': [i for i in bid.lotValues if lot.id == i.relatedLot][0].value,
                    'tenderers': bid.tenderers,
                    'parameters': [i for i in bid.parameters if i.code in codes],
                    'date': [i for i in bid.lotValues if lot.id == i.relatedLot][0].date
                }
                for bid in auction.bids
                if lot.id in [i.relatedLot for i in bid.lotValues]
            ]
            if not bids:
                lot.status = 'unsuccessful'
                statuses.add('unsuccessful')
                continue
            unsuccessful_awards = [i.bid_id for i in lot_awards if i.status == 'unsuccessful']
            bids = chef(bids, features, unsuccessful_awards, True)
            if bids:
                bid = bids[0]
                award = type(auction).awards.model_class({
                    'bid_id': bid['id'],
                    'lotID': lot.id,
                    'status': 'pending',
                    'value': bid['value'],
                    'date': get_now(),
                    'suppliers': bid['tenderers'],
                    'complaintPeriod': {
                        'startDate': now.isoformat()
                    }
                })
                auction.awards.append(award)
                request.response.headers['Location'] = request.route_url('{}:Auction Awards'.format(auction.procurementMethodType), auction_id=auction.id, award_id=award['id'])
                statuses.add('pending')
            else:
                statuses.add('unsuccessful')
        if statuses.difference(set(['unsuccessful', 'active'])):
            auction.awardPeriod.endDate = None
            auction.status = 'active.qualification'
        else:
            auction.awardPeriod.endDate = now
            auction.status = 'active.awarded'
    else:
        if not auction.awards or auction.awards[-1].status not in ['pending', 'active']:
            unsuccessful_awards = [i.bid_id for i in auction.awards if i.status == 'unsuccessful']
            bids = chef(auction.bids, auction.features or [], unsuccessful_awards, True)
            if bids:
                bid = bids[0].serialize()
                award = type(auction).awards.model_class({
                    'bid_id': bid['id'],
                    'status': 'pending',
                    'date': get_now(),
                    'value': bid['value'],
                    'suppliers': bid['tenderers'],
                    'complaintPeriod': {
                        'startDate': get_now().isoformat()
                    }
                })
                auction.awards.append(award)
                request.response.headers['Location'] = request.route_url('{}:Auction Awards'.format(auction.procurementMethodType), auction_id=auction.id, award_id=award['id'])
        if auction.awards[-1].status == 'pending':
            auction.awardPeriod.endDate = None
            auction.status = 'active.qualification'
        else:
            auction.awardPeriod.endDate = now
            auction.status = 'active.awarded'