from datetime import timedelta


from openprocurement.api.models import get_now


def contract_signing_period_switch_to_qualification(self):
    auction = self.db.get(self.auction_id)
    contract = auction['contracts'][0]
    start_date = get_now() - timedelta(days=7)
    start_date = start_date.isoformat()
    end_date = get_now() - timedelta(days=5)
    end_date = end_date.isoformat()

    # set signingPeriod to past
    contract['signingPeriod']['startDate'] = start_date
    contract['signingPeriod']['endDate'] = end_date

    self.assertEqual(
        auction['status'],
        'active.awarded'
    )

    self.db.save(auction)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json(
        '/auctions/{}'.format(self.auction_id),
        {'data': {'id': self.auction_id}}
    )
    status = response.json['data']['status']
    self.assertEqual(
        status,
        'active.qualification'
    )
    self.assertEqual(
        response.json['data']['contracts'][0]['status'],
        'cancelled'
    )
    auction = self.db.get(self.auction_id)
    self.assertEqual(
        response.json['data']['awards'][1]['status'],
        'pending',
        'awars status is wrong'
    )

def contract_signing_period_switch_to_complete(self):
    auction = self.db.get(self.auction_id)
    contract = auction['contracts'][0]
    start_date = get_now() - timedelta(days=3)
    start_date = start_date.isoformat()
    end_date = get_now() + timedelta(days=3)
    end_date = end_date.isoformat()

    # set signingPeriod to present
    contract['signingPeriod']['startDate'] = start_date
    contract['signingPeriod']['endDate'] = end_date

    contract['status'] = 'active'

    self.assertEqual(
        auction['status'],
        'active.awarded'
    )

    self.db.save(auction)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json(
        '/auctions/{}'.format(self.auction_id),
        {'data': {'id': self.auction_id}}
    )
    status = response.json['data']['status']
    self.assertEqual(
        status,
        'complete'
    )
