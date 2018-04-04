from openprocurement.api.utils import get_now
from openprocurement.auctions.core.utils import get_related_award_of_contract


def create_auction_contract(self):
    auction = self.db.get(self.auction_id)
    # Contract was created on setUp stage
    contract = auction['contracts'][0]
    self.assertIn('id', contract)
    self.assertIn('value', contract)
    self.assertIn('suppliers', contract)

    award = get_related_award_of_contract(contract, auction)
    self.assertEqual(
        award['signingPeriod'],
        contract['signingPeriod'],
        'signingPeriod wasn\'t copied'
    )

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
    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "terminated"
    self.db.save(auction)

    self.set_status('complete')

    response = self.app.post_json(
        '/auctions/{}/contracts'.format(
        self.auction_id
        ),
        {'data': {
            'title': 'contract title',
            'description': 'contract description',
            'awardID': self.award_id
        }},
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add contract in current (complete) auction status")

    response = self.app.patch_json(
        '/auctions/{}/contracts/{}'.format(
            self.auction_id,
            self.award_contract_id
        ),
       {"data": {"status": "active"}},
       status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")


def patch_signing_period(self):
    """Check unavailability of patching `signingPeriod` of `Contract` model

        Response's status code `200` is OK. It just doesn't save the patch.
    """
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, contract['id']), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    # check that signingPeriod can't be patched
    pre_patch_contract_response = self.app.get('/auctions/{0}/contracts/{1}' \
        .format(self.auction_id, contract['id']))
    self.app.patch_json(
        '/auctions/{0}/contracts/{1}'.format(self.auction_id, contract['id']),
        {'data': {
            'signingPeriod': {
                'startDate': '2010-02-02T12:04:15+02:00',
                'endDate': '2010-02-03T12:04:16+02:00'
            }
        }},
        status=200
    )
    after_patch_contract_response = self.app.get(
        '/auctions/{0}/contracts/{1}'.format(self.auction_id, contract['id'])
    )

    # responses before & after patch are equal
    self.assertEqual(pre_patch_contract_response.json, after_patch_contract_response.json)


def patch_date_paid(self):
    """Check availability of patching `datePaid` of `Contract` model
    """
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, contract['id']), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    # check that datepaid can be patched
    date_paid_iso_str = get_now().isoformat()
    pre_patch_contract_response = self.app.get('/auctions/{0}/contracts/{1}' \
        .format(self.auction_id, contract['id']))
    self.assertIsNone(pre_patch_contract_response.json['data'].get('datePaid'))

    self.app.patch_json(
        '/auctions/{0}/contracts/{1}'.format(self.auction_id, contract['id']),
        {'data': {'datePaid': date_paid_iso_str}},
        status=200
    )

    after_patch_contract_response = self.app.get(
        '/auctions/{0}/contracts/{1}'.format(self.auction_id, contract['id'])
    )
    # check if datePaid has appeared
    self.assertEqual(
        after_patch_contract_response.json['data'].get('datePaid'),
        date_paid_iso_str
    )


def get_auction_contract(self):
    response = self.app.get(
        '/auctions/{}/contracts/{}'.format(
            self.auction_id,
            self.award_contract_id
        )
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

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
