# -*- coding: utf-8 -*-
from openprocurement.api.models import TZ


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
