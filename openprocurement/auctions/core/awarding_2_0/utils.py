from openprocurement.api.utils import get_now
from openprocurement.api.models import TZ


def switch_to_next_award(request):
    auction = request.validated['auction']
    now = get_now()
    waiting_awards = [i for i in auction.awards if i['status'] == 'pending.waiting']
    if waiting_awards:
        award = waiting_awards[0]
        award.status = 'pending.verification'
        award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': now}
        award = award.serialize()
        request.response.headers['Location'] = request.route_url('{}:Auction Awards'.format(auction.procurementMethodType), auction_id=auction.id, award_id=award['id'])

    elif all([award.status in ['cancelled', 'unsuccessful'] for award in auction.awards]):
        auction.awardPeriod.endDate = now
        auction.status = 'unsuccessful'


def check_auction_protocol(award):
    if award.documents:
        for document in award.documents:
            if document['documentType'] == 'auctionProtocol' and document['author'] == 'auction_owner':
                return True
    return False


def next_check_awarding(auction, checks):
    if not auction.lots and auction.status == 'active.qualification':
        for award in auction.awards:
            if award.status == 'pending.verification':
                checks.append(award.verificationPeriod.endDate.astimezone(TZ))
            elif award.status == 'pending.payment':
                checks.append(award.paymentPeriod.endDate.astimezone(TZ))
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
        for award in auction.awards:
            if award.status == 'active':
                checks.append(award.signingPeriod.endDate.astimezone(TZ))

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
            if not pending_complaints and not pending_awards_complaints and standStillEnds and last_award_status == 'unsuccessful':
                checks.append(max(standStillEnds))
    return checks
