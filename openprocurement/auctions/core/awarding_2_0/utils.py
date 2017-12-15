from openprocurement.api.utils import get_now 


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
