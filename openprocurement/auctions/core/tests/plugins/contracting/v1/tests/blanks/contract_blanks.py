def create_auction_contract(self):
    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id), {
        'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id,
                 'value': self.award_value, 'suppliers': self.award_suppliers}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    contract = response.json['data']
    self.assertIn('id', contract)
    self.assertIn('value', contract)
    self.assertIn('suppliers', contract)
    self.assertIn(contract['id'], response.headers['Location'])

    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "terminated"
    self.db.save(auction)

    self.set_status('unsuccessful')

    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}},
        status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add contract in current (unsuccessful) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
"Can't update contract in current (unsuccessful) auction status")


def create_auction_contract_in_complete_status(self):
    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    contract = response.json['data']
    self.assertIn('id', contract)
    self.assertIn(contract['id'], response.headers['Location'])

    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "terminated"
    self.db.save(auction)

    self.set_status('complete')

    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}},
        status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
"Can't update contract in current (complete) auction status")


def get_auction_contract(self):

    response = self.app.get('/auctions/{}/contracts/{}'.format(self.auction_id, self.contract_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], self.contract)

    response = self.app.get('/auctions/{}/contracts/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.get('/auctions/some_id/contracts/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
])
