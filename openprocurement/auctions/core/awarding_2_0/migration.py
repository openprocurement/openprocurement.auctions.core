from barbecue import chef
from uuid import uuid4

from openprocurement.api.utils import get_now
from openprocurement.auctions.dgf.utils import invalidate_bids_under_threshold


def switch_auction_to_unsuccessful(auction):
    if auction.get('suspended'):
        return
    actual_award = [a for a in auction["awards"] if a['status'] in ['active', 'pending']][0]
    if auction['status'] == 'active.awarded':
        for i in auction['contracts']:
            if i['awardID'] == actual_award['id']:
                i['status'] = 'cancelled'
    actual_award['status'] = 'unsuccessful'
    auction['awardPeriod']['endDate'] = actual_award['complaintPeriod']['endDate'] = get_now().isoformat()
    auction['status'] = 'unsuccessful'


def migrate_awarding_1_0_to_awarding_2_0(auction):
    if auction['procurementMethodType'] not in ['dgfOtherAssets', 'dgfFinancialAssets'] \
                or auction['status'] not in ['active.qualification', 'active.awarded'] \
                or 'awards' not in auction:
        return
    now = get_now().isoformat()
    awards = auction["awards"]
    unique_awards = len(set([a['bid_id'] for a in awards]))

    if unique_awards > 2:
        switch_auction_to_unsuccessful(auction)
    else:
        invalidate_bids_under_threshold(auction)
        award = [a for a in awards if a['status'] in ['active', 'pending']][0]
        for bid in auction['bids']:
            if bid['id'] == award['bid_id'] and bid['status'] == 'invalid':
                switch_auction_to_unsuccessful(auction)

    if auction['status'] != 'unsuccessful':
        award = [a for a in awards if a['status'] in ['active', 'pending']][0]

        award_create_date = award['complaintPeriod']['startDate']

        award.update({
            'verificationPeriod': {
                'startDate': award_create_date,
                'endDate': award_create_date
            },
            'paymentPeriod': {
                'startDate': award_create_date,
            },
            'signingPeriod': {
                'startDate': award_create_date,
            }
        })

        if award['status'] == 'pending':
            award['status'] = 'pending.payment'

        elif award['status'] == 'active':
            award['verificationPeriod']['endDate'] = award['paymentPeriod']['endDate'] = now

        if unique_awards == 1:
            bid = chef(auction['bids'], auction.get('features'), [], True)[1]

            award = {
                'id': uuid4().hex,
                'bid_id': bid['id'],
                'status': 'pending.waiting',
                'date': awards[0]['date'],
                'value': bid['value'],
                'suppliers': bid['tenderers'],
                'complaintPeriod': {
                    'startDate': awards[0]['date']
                }
            }
            if bid['status'] == 'invalid':
                award['status'] = 'unsuccessful'
                award['complaintPeriod']['endDate'] = now

            awards.append(award)
