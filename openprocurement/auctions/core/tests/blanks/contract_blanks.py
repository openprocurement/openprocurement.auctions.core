# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.api.models import get_now

# AuctionContractResourceTest


def create_auction_contract_invalid(self):
    response = self.app.post_json('/auctions/some_id/contracts', {
        'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}},
                                  status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'auction_id'}
    ])

    request_path = '/auctions/{}/contracts'.format(self.auction_id)

    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
             u"Content-Type header should be one of ['application/json']", u'location': u'header',
         u'name': u'Content-Type'}
    ])

    response = self.app.post(
        request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Expecting value: line 1 column 1 (char 0)',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(
        request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {
        'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {'data': {'awardID': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'awardID should be one of awards'], u'location': u'body', u'name': u'awardID'}
    ])


def create_auction_contract(self):
    auction = self.db.get(self.auction_id)
    contract = auction['contracts'][0]
    self.assertIn('id', contract)
    self.assertIn('value', contract)
    self.assertIn('suppliers', contract)

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


def patch_auction_contract(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn("Can't sign contract before stand-still period end (", response.json['errors'][0]["description"])

    self.set_status('complete', {'status': 'active.awarded'})

    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(self.auction_id, self.award_id), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': self.initial_organization,
        'status': 'claim'
    }})
    self.assertEqual(response.status, '201 Created')
    complaint = response.json['data']
    owner_token = response.json['access']['token']

    auction = self.db.get(self.auction_id)
    for i in auction.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(auction)

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"], "Cant\'t sign contract without document")

    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, contract['id']), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']))
    self.assertEqual(response.json['data']['contractID'], contract['contractID'])
    self.assertEqual(response.json['data']['items'], contract['items'])
    self.assertEqual(response.json['data']['suppliers'], contract['suppliers'])

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"value": {"currency": "USD"}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"], "Can\'t update currency for contract value")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"value": {"valueAddedTaxIncluded": False}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can\'t update valueAddedTaxIncluded for contract value")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"value": {"amount": 99}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Value amount should be greater or equal to awarded amount ({})".format(self.award_value['amount']))

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"value": {"amount": 500}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['value']['amount'], 500)

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"dateSigned": one_hour_in_furure}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Contract signature date can't be in the future"], u'location': u'body',
         u'name': u'dateSigned'}])

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"dateSigned": custom_signature_date}})
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"value": {"amount": 232}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"contractID": "myselfID"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"items": [{"description": "New Description"}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"suppliers": [{"name": "New Name"}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/some_id'.format(self.auction_id),
                                   {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.patch_json('/auctions/some_id/contracts/some_id', {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertEqual(response.json['data']["value"]['amount'], 500)
    self.assertEqual(response.json['data']['contractID'], contract['contractID'])
    self.assertEqual(response.json['data']['items'], contract['items'])
    self.assertEqual(response.json['data']['suppliers'], contract['suppliers'])
    self.assertEqual(response.json['data']['dateSigned'], custom_signature_date)


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
    patch_contract_response = self.app.patch_json(
        '/auctions/{0}/contracts/{1}'.format(self.auction_id, contract['id']),
        {'data': {
            'signingPeriod': {
                'startDate': '2010-02-02T12:04:15+02:00',
                'endDate': '2010-02-03T12:04:16+02:00'
            }
        }},
        status=200
    )
    after_patch_contract_response = self.app.get('/auctions/{0}/contracts/{1}' \
        .format(self.auction_id, contract['id']))

    # responses before & after patch are equal
    self.assertEqual(
        pre_patch_contract_response.json,
        after_patch_contract_response.json
    )


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
    date_paid_iso_str = '2018-01-01T12:04:15+02:00'
    pre_patch_contract_response = self.app.get('/auctions/{0}/contracts/{1}' \
        .format(self.auction_id, contract['id']))
    self.assertIsNone(pre_patch_contract_response.json['data'].get('datePaid'))

    patch_contract_response = self.app.patch_json(
        '/auctions/{0}/contracts/{1}'.format(self.auction_id, contract['id']),
        {'data': {'datePaid': date_paid_iso_str}},
        status=200
    )

    after_patch_contract_response = self.app.get('/auctions/{0}/contracts/{1}' \
        .format(self.auction_id, contract['id']))
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


def get_auction_contracts(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('id', response.json['data'][0])

    response = self.app.get('/auctions/some_id/contracts', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

# Auction2LotContractResourceTest


def patch_auction_contract_2_lots(self):
    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn("Can't sign contract before stand-still period end (", response.json['errors'][0]["description"])

    self.set_status('complete', {'status': 'active.awarded'})

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})

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
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can update contract only in active lot status"
    )

# AuctionContractDocumentResourceTest


def not_found(self):
    response = self.app.post('/auctions/some_id/contracts/some_id/documents', status=404, upload_files=[
                             ('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.post('/auctions/{}/contracts/some_id/documents'.format(self.auction_id), status=404, upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(self.auction_id, self.contract_id), status=404, upload_files=[
                             ('invalid_value', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.get('/auctions/some_id/contracts/some_id/documents', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/contracts/some_id/documents'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.get('/auctions/some_id/contracts/some_id/documents/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/contracts/some_id/documents/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.get('/auctions/{}/contracts/{}/documents/some_id'.format(self.auction_id, self.contract_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'document_id'}
    ])

    response = self.app.put('/auctions/some_id/contracts/some_id/documents/some_id', status=404,
                            upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.put('/auctions/{}/contracts/some_id/documents/some_id'.format(self.auction_id), status=404, upload_files=[
                            ('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.put('/auctions/{}/contracts/{}/documents/some_id'.format(
        self.auction_id, self.contract_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
    ])


def create_auction_contract_document(self):
    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/contracts/{}/documents'.format(self.auction_id, self.contract_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/contracts/{}/documents?all=true'.format(self.auction_id, self.contract_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/contracts/{}/documents/{}?download=some_id'.format(
        self.auction_id, self.contract_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/contracts/{}/documents/{}?{}'.format(
        self.auction_id, self.contract_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "cancelled"
    self.db.save(auction)

    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current contract status")

    self.set_status('unsuccessful')

    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (unsuccessful) auction status")


def put_auction_contract_document(self):
    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}'.format(self.auction_id, self.contract_id, doc_id),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/contracts/{}/documents/{}?{}'.format(
        self.auction_id, self.contract_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/contracts/{}/documents/{}?{}'.format(
        self.auction_id, self.contract_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "cancelled"
    self.db.save(auction)

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current contract status")

    self.set_status('unsuccessful')

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (unsuccessful) auction status")


def patch_auction_contract_document(self):
    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/auctions/{}/contracts/{}/documents/{}'.format(self.auction_id, self.contract_id, doc_id), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "cancelled"
    self.db.save(auction)

    response = self.app.patch_json('/auctions/{}/contracts/{}/documents/{}'.format(self.auction_id, self.contract_id, doc_id), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current contract status")

    self.set_status('unsuccessful')

    response = self.app.patch_json('/auctions/{}/contracts/{}/documents/{}'.format(self.auction_id, self.contract_id, doc_id), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (unsuccessful) auction status")

# Auction2LotContractDocumentResourceTest


def create_auction_2_lot_contract_document(self):
    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})

    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add document only in active lot status")


def put_auction_2_lot_contract_document(self):
    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}'.format(self.auction_id, self.contract_id, doc_id),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})

    response = self.app.put('/auctions/{}/contracts/{}/documents/{}'.format(
        self.auction_id, self.contract_id, doc_id), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only in active lot status")


def patch_auction_2_lot_contract_document(self):
    response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
        self.auction_id, self.contract_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json(
        '/auctions/{}/contracts/{}/documents/{}'.format(self.auction_id, self.contract_id, doc_id),
        {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})

    response = self.app.patch_json(
        '/auctions/{}/contracts/{}/documents/{}'.format(self.auction_id, self.contract_id, doc_id),
        {"data": {"description": "new document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only in active lot status")
