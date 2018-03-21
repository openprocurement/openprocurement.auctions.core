from barbecue import chef
from uuid import uuid4

from openprocurement.api.utils import get_now
from openprocurement.auctions.core.plugins.awarding.v2_1.utils import invalidate_bids_under_threshold


def switch_auction_to_unsuccessful(auction):
    pass


def migrate_awarding_1_0_to_awarding_2_1(auction):
    if (auction['procurementMethodType'] not in ['dgfOtherAssets', 'dgfFinancialAssets']
            or auction['status'] not in ['active.qualification', 'active.awarded']
            or 'awards' not in auction):
        return

    now = get_now().isoformat()
    awards = auction["awards"]
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
        award['paymentPeriod']['endDate'] = now

    awarded_bids = set([a['bid_id'] for a in awards])
    sorted_bids = chef(auction['bids'], auction.get('features'), [], True)
    filtered_bids = [bid for bid in sorted_bids if bid['id'] not in awarded_bids]

    for bid in filtered_bids:
        award = {
            'id': uuid4().hex,
            'bid_id': bid['id'],
            'status': 'pending.waiting',
            'date': award_create_date,
            'value': bid['value'],
            'suppliers': bid['tenderers'],
            'complaintPeriod': {
                'startDate': award_create_date
            }
        }
        awards.append(award)
