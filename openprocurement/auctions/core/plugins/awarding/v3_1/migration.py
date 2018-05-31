from datetime import time
from uuid import uuid4

from isodate import parse_datetime

from openprocurement.api.utils import get_now, set_specific_hour

from openprocurement.auctions.core.plugins.contracting.v3.constants import CONTRACT_SIGNING_PERIOD_END_DATE_HOUR


def migrate_awarding2_to_awarding3(auction,
                                   server_id,
                                   procurementMethodTypes):
    """Migrate util from awarding v2 to awarding v3_1

       1. Rename pending.verification to pending.
       2. Remove pending.payment status with contract creation
       3. Adding signingPeriod to contract from award object
    """
    changed = False
    if auction['procurementMethodType'] not in procurementMethodTypes\
                or auction['status'] not in ['active.qualification', 'active.awarded'] \
                or 'awards' not in auction:
        return changed
    now = get_now().isoformat()

    for award in auction['awards']:
        if award['status'] == 'pending.verification':
            # Rename pending.verification to pending status
            award['status'] = 'pending'
            changed = True
        elif award['status'] == 'pending.payment':
            # Remove pending.payment status
            award['status'] = 'active'
            auction['status'] = 'active.awarded'
            # Create contract for award in pending.payment
            contract = {
               'id': uuid4().hex,
               'awardID': award['id'],
               'suppliers': award['suppliers'],
               'value': award['value'],
               'date': now,
               'items': auction['items'],
               'contractID': '{}-{}{}'.format(
                    auction['auctionID'],
                    server_id,
                    len(auction.get('contracts', [])) + 1
                ),
               'signingPeriod': award['signingPeriod']
            }
            contracts = auction.get('contracts', [])
            contracts.append(contract)
            auction['contracts'] = contracts
            changed = True
        # Migrate signingPeriod from Award to Contract
        for contract in auction.get('contracts', ''):
            award = [x for x in auction['awards'] if x['id'] == contract['awardID']][0]
            if not contract.get('signingPeriod', False):
                contract.update({'signingPeriod': award['signingPeriod']})
                changed = True
            # Set specific hour to signingPeriod.endDate of Contract
            if contract['signingPeriod'].get('endDate'):
                contract_signing_period_end_date = parse_datetime(contract['signingPeriod']['endDate'])
                if contract_signing_period_end_date.time() != time(CONTRACT_SIGNING_PERIOD_END_DATE_HOUR):
                    contract['signingPeriod']['endDate'] = set_specific_hour(
                        contract_signing_period_end_date,
                        CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
                    ).isoformat()
                    changed = True
    return changed
