# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now


# CreateAuctionAwardTest


def create_auction_award_invalid(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)
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

    response = self.app.post_json(request_path, {
        'data': {'suppliers': [{'identifier': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'identifier': [
            u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body',
            u'name': u'suppliers'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'suppliers': [{'identifier': {'id': 0}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            {u'contactPoint': [u'This field is required.'], u'identifier': {u'scheme': [u'This field is required.']},
             u'name': [u'This field is required.'], u'address': [u'This field is required.']}], u'location': u'body',
            u'name': u'suppliers'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'bid_id'}
    ])

    response = self.app.post_json(request_path, {'data': {'suppliers': [
        {'name': 'name', 'identifier': {'uri': 'invalid_value'}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'contactPoint': [u'This field is required.'],
                           u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.'],
                                           u'uri': [u'Not a well formed URL.']},
                           u'address': [u'This field is required.']}], u'location': u'body', u'name': u'suppliers'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'bid_id'}
    ])

    response = self.app.post_json(request_path, {'data': {
        'suppliers': [self.initial_organization],
        'status': 'pending',
        'bid_id': self.initial_bids[0]['id'],
        'lotID': '0' * 32
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'lotID should be one of lots'], u'location': u'body', u'name': u'lotID'}
    ])

    response = self.app.post_json('/auctions/some_id/awards', {'data': {
        'suppliers': [self.initial_organization], 'bid_id': self.initial_bids[0]['id']}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/some_id/awards', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    self.set_status('complete')

    response = self.app.post_json('/auctions/{}/awards'.format(
        self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending',
                                    'bid_id': self.initial_bids[0]['id']}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't create award in current (complete) auction status")


def create_auction_award(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)
    now = get_now()
    response = self.app.post_json(request_path, {
        'data': {'suppliers': [self.initial_organization], 'bid_id': self.initial_bids[0]['id']}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    award = response.json['data']
    self.assertEqual(award['suppliers'][0]['name'], self.initial_organization['name'])
    self.assertIn('id', award)
    self.assertIn(award['id'], response.headers['Location'])

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][-1], award)

    bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, award['id'], bid_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award['id'], doc_id, bid_token),
        {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("documentType", response.json["data"])
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

    response = self.app.get('/auctions/{}/awards/{}/documents/{}'.format(self.auction_id, award['id'], doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('auctionProtocol', response.json["data"]["documentType"])
    self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
    self.assertEqual('bid_owner', response.json["data"]["author"])

    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, award['id'], self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award['id'], doc_id,
                                                                  self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("documentType", response.json["data"])
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

    response = self.app.get('/auctions/{}/awards/{}/documents/{}'.format(self.auction_id, award['id'], doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('auctionProtocol', response.json["data"]["documentType"])
    self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
    self.assertEqual('auction_owner', response.json["data"]["author"])

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active.awarded')

# AuctionLotAwardResourceTest


def create_auction_award_lot(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)
    response = self.app.post_json(request_path, {
        'data': {'suppliers': [self.initial_organization], 'status': 'pending',
                 'bid_id': self.initial_bids[0]['id']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {"location": "body", "name": "lotID", "description": ["This field is required."]}
    ])

    response = self.app.post_json(request_path, {
        'data': {'suppliers': [self.initial_organization], 'status': 'pending',
                 'bid_id': self.initial_bids[0]['id'], 'lotID': self.initial_lots[0]['id']}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    award = response.json['data']
    self.assertEqual(award['suppliers'][0]['name'], self.initial_organization['name'])
    self.assertEqual(award['lotID'], self.initial_lots[0]['id'])
    self.assertIn('id', award)
    self.assertIn(award['id'], response.headers['Location'])

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][-1], award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active.awarded')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'cancelled')
    self.assertIn('Location', response.headers)


def patch_auction_award_lot(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)
    response = self.app.post_json(request_path, {
        'data': {'suppliers': [self.initial_organization], 'status': u'pending', 'bid_id': self.initial_bids[0]['id'],
                 'lotID': self.initial_lots[0]['id'], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    award = response.json['data']

    response = self.app.patch_json('/auctions/{}/awards/some_id'.format(self.auction_id),
                                   {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.patch_json('/auctions/some_id/awards/some_id', {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"awardStatus": "unsuccessful"}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {"location": "body", "name": "awardStatus", "description": "Rogue field"}
    ])

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (unsuccessful) status")

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)
    self.assertIn(response.json['data'][-1]['id'], new_award_location)
    new_award_id = response.json['data'][-1]['id']

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, new_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, new_award_id),
                                   {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)

    self.set_status('complete')

    response = self.app.get('/auctions/{}/awards/{}'.format(self.auction_id, award['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], 500)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update award in current (complete) auction status")


def patch_auction_award_unsuccessful_lot(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)
    response = self.app.post_json(request_path, {
        'data': {'suppliers': [self.initial_organization], 'status': u'pending', 'bid_id': self.initial_bids[0]['id'],
                 'lotID': self.initial_lots[0]['id'], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    award = response.json['data']

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-82:], {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('Location', response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(self.auction_id, award['id']), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': self.initial_organization,
        'status': 'claim'
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.post_json('{}/complaints'.format(new_award_location[-82:]), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': self.initial_organization
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']),
                                   {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-82:], {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-82:], {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('Location', response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 4)

# Auction2LotAwardResourceTest


def create_auction_award_2_lots(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)
    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.post_json(request_path, {'data': {
        'suppliers': [self.initial_organization],
        'status': 'pending',
        'bid_id': self.initial_bids[0]['id'],
        'lotID': self.initial_lots[0]['id']
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can create award only in active lot status")

    response = self.app.post_json(request_path, {'data': {
        'suppliers': [self.initial_organization],
        'status': 'pending',
        'bid_id': self.initial_bids[0]['id'],
        'lotID': self.initial_lots[1]['id']
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    award = response.json['data']
    self.assertEqual(award['suppliers'][0]['name'], self.initial_organization['name'])
    self.assertEqual(award['lotID'], self.initial_lots[1]['id'])
    self.assertIn('id', award)
    self.assertIn(award['id'], response.headers['Location'])

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][-1], award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active.awarded')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']), {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'cancelled')
    self.assertIn('Location', response.headers)


def patch_auction_award_2_lots(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)
    response = self.app.post_json(request_path, {'data': {'suppliers': [self.initial_organization], 'status': u'pending', 'bid_id': self.initial_bids[0]['id'], 'lotID': self.initial_lots[0]['id'], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    award = response.json['data']

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, award['id']), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)
    new_award = response.json['data'][-1]
    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, new_award['id']), {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update award only in active lot status")

# AuctionAwardProcessTest


def invalid_patch_auction_award(self):
    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "pending.waiting"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending) status to (pending.waiting) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award status to (active) before auction owner load auction protocol")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "cancelled"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending) status to (cancelled) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (unsuccessful) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (pending) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (active) status")

    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "pending.waiting"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending) status to (pending.waiting) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "cancelled"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending) status to (cancelled) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (unsuccessful) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (pending) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (active) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (unsuccessful) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (pending) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (active) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], "active")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "cancelled"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (active) status to (cancelled) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "pending.waiting"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (active) status to (pending.waiting) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (active) status to (pending) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (unsuccessful) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (pending) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't switch award (pending.waiting) status to (active) status")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], "unsuccessful")
    self.assertIn('Location', response.headers)
    self.assertIn(self.second_award_id, response.headers['Location'])

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update award in current (unsuccessful) status")

    self.upload_auction_protocol(self.second_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')


def patch_auction_award(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.patch_json('/auctions/{}/awards/some_id'.format(self.auction_id),
                                   {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.patch_json('/auctions/some_id/awards/some_id', {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"awardStatus": "unsuccessful"}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {"location": "body", "name": "awardStatus", "description": "Rogue field"}
    ])

    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']
    self.assertIn(self.second_award_id, new_award_location)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (unsuccessful) status")

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)
    self.assertIn(response.json['data'][1]['id'], new_award_location)

    response = self.app.patch_json(
        '/auctions/{}/awards/{}?acc_token={}'.format(self.auction_id, self.second_award_id, self.auction_token),
        {"data": {"title": "title", "description": "description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['title'], 'title')
    self.assertEqual(response.json['data']['description'], 'description')

    self.upload_auction_protocol(self.second_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')

    response = self.app.get('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], self.second_award['value']['amount'])

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update award in current (complete) auction status")


def patch_auction_award_admin(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)

    authorization = self.app.authorization

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {
                                       "verificationPeriod": {
                                           'endDate': self.first_award['verificationPeriod']['startDate']},
                                       "signingPeriod": {'endDate': self.first_award['signingPeriod']['startDate']}}
                                   })
    self.assertEqual(response.status, '200 OK')
    first_award = response.json['data']
    self.assertEqual(first_award['verificationPeriod']['startDate'], first_award['verificationPeriod']['endDate'])
    self.assertEqual(first_award['signingPeriod']['startDate'], first_award['signingPeriod']['endDate'])

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {
                                       "status": 'active',
                                       "verificationPeriod": {'endDate': None},
                                       "signingPeriod": {'endDate': None}}
                                   })
    self.assertEqual(response.status, '200 OK')
    first_award = response.json['data']
    self.assertNotEqual(first_award['status'], 'active')
    self.assertNotEqual(first_award['verificationPeriod']['startDate'], first_award['verificationPeriod']['endDate'])
    self.assertEqual(first_award['verificationPeriod']['endDate'], self.first_award['verificationPeriod']['endDate'])
    self.assertNotEqual(first_award['signingPeriod']['startDate'], first_award['signingPeriod']['endDate'])
    self.assertEqual(first_award['signingPeriod']['endDate'], self.first_award['signingPeriod']['endDate'])

    self.app.authorization = authorization

    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'complete')


def complate_auction_with_second_award1(self):
    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    self.assertIn(self.second_award_id, response.headers['Location'])

    self.upload_auction_protocol(self.second_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')

    response = self.app.get('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], self.second_award['value']['amount'])

    response = self.app.get(
        '/auctions/{0}'.format(
            self.auction_id,
        )
    )
    # find new contract instance
    for contract in response.json['data']['contracts']:
        if contract['awardID'] == self.second_award['id']:
            auto_created_contract = contract
    # find updated award instance
    for award in response.json['data']['awards']:
        if award['id'] == self.second_award['id']:
            updated_award = award

    # check if signingPeriod is copied from award
    self.assertEqual(
        auto_created_contract['signingPeriod'],
        updated_award['signingPeriod']
    )


def complate_auction_with_second_award2(self):
    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    self.assertIn(self.second_award_id, response.headers['Location'])

    self.upload_auction_protocol(self.second_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')

    response = self.app.get('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], self.second_award['value']['amount'])


def complate_auction_with_second_award3(self):
    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    self.assertIn(self.second_award_id, response.headers['Location'])

    self.upload_auction_protocol(self.second_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')

    response = self.app.get('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], self.second_award['value']['amount'])


def successful_second_auction_award(self):
    request_path = '/auctions/{}/awards'.format(self.auction_id)
    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)
    self.assertIn(response.json['data'][1]['id'], new_award_location)
    new_award = response.json['data'][-1]

    self.upload_auction_protocol(self.second_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')

    response = self.app.get('/auctions/{}/awards/{}'.format(self.auction_id, self.second_award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], self.second_award['value']['amount'])


def unsuccessful_auction1(self):
    response = self.app.patch_json('/auctions/{}/awards/{}?acc_token=1'.format(self.auction_id, self.second_award_id),
                                   {"data": {"status": "cancelled"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Only bid owner may cancel award in current (pending.waiting) status', u'location':
            u'body', u'name': u'data'}
    ])

    bid_token = self.initial_bids_tokens[self.first_award['bid_id']]
    response = self.app.patch_json(
        '/auctions/{}/awards/{}?acc_token={}'.format(self.auction_id, self.second_award_id, bid_token),
        {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def unsuccessful_auction2(self):
    bid_token = self.initial_bids_tokens[self.first_award['bid_id']]
    response = self.app.patch_json(
        '/auctions/{}/awards/{}?acc_token={}'.format(self.auction_id, self.second_award_id, bid_token),
        {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def unsuccessful_auction3(self):
    bid_token = self.initial_bids_tokens[self.first_award['bid_id']]
    response = self.app.patch_json(
        '/auctions/{}/awards/{}?acc_token={}'.format(self.auction_id, self.second_award_id, bid_token),
        {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def unsuccessful_auction4(self):
    self.upload_auction_protocol(self.first_award)

    bid_token = self.initial_bids_tokens[self.first_award['bid_id']]
    response = self.app.patch_json(
        '/auctions/{}/awards/{}?acc_token={}'.format(self.auction_id, self.second_award_id, bid_token),
        {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def unsuccessful_auction5(self):
    self.upload_auction_protocol(self.first_award)

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    bid_token = self.initial_bids_tokens[self.first_award['bid_id']]
    response = self.app.patch_json(
        '/auctions/{}/awards/{}?acc_token={}'.format(self.auction_id, self.second_award_id, bid_token),
        {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'unsuccessful')


def get_auction_awards(self):
    response = self.app.get('/auctions/{}/awards'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)
    fist_award = response.json['data'][0]
    second_award = response.json['data'][1]

    response = self.app.get('/auctions/{}/awards/{}'.format(self.auction_id, fist_award['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'pending')
    self.assertIn('verificationPeriod', response.json['data'])

    response = self.app.get('/auctions/{}/awards/{}'.format(self.auction_id, second_award['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'pending.waiting')

    response = self.app.get('/auctions/{}/awards/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.get('/auctions/some_id/awards/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

# InsiderAuctionAwardDocumentResourceTest


def not_found(self):
    response = self.app.post('/auctions/some_id/awards/some_id/documents', status=404, upload_files=[
                             ('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.post('/auctions/{}/awards/some_id/documents'.format(self.auction_id), status=404, upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.post('/auctions/{}/awards/{}/documents'.format(self.auction_id, self.first_award_id), status=404, upload_files=[
                             ('invalid_value', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.get('/auctions/some_id/awards/some_id/documents', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/awards/some_id/documents'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.get('/auctions/some_id/awards/some_id/documents/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/awards/some_id/documents/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.get('/auctions/{}/awards/{}/documents/some_id'.format(self.auction_id, self.first_award_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'document_id'}
    ])

    response = self.app.put('/auctions/some_id/awards/some_id/documents/some_id', status=404,
                            upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.put('/auctions/{}/awards/some_id/documents/some_id'.format(self.auction_id), status=404,
                            upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.put('/auctions/{}/awards/{}/documents/some_id'.format(
        self.auction_id, self.first_award_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
    ])


def create_auction_award_document(self):
    response = self.app.post('/auctions/{}/awards/{}/documents'.format(
        self.auction_id, self.first_award_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/documents'.format(self.auction_id, self.first_award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/awards/{}/documents?all=true'.format(self.auction_id, self.first_award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/awards/{}/documents/{}?download=some_id'.format(
        self.auction_id, self.first_award_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/awards/{}/documents/{}?{}'.format(
        self.auction_id, self.first_award_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.first_award_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    self.set_status('complete')

    response = self.app.post('/auctions/{}/awards/{}/documents'.format(
        self.auction_id, self.first_award_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) auction status")


def put_auction_award_document(self):
    response = self.app.post('/auctions/{}/awards/{}/documents'.format(
        self.auction_id, self.first_award_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/auctions/{}/awards/{}/documents/{}'.format(self.auction_id, self.first_award_id, doc_id),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.first_award_id, doc_id), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/documents/{}?{}'.format(
        self.auction_id, self.first_award_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.first_award_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.first_award_id, doc_id), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/documents/{}?{}'.format(
        self.auction_id, self.first_award_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    self.set_status('complete')

    response = self.app.put('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.first_award_id, doc_id), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) auction status")


def patch_auction_award_document(self):
    response = self.app.post('/auctions/{}/awards/{}/documents'.format(
        self.auction_id, self.first_award_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}'.format(self.auction_id, self.first_award_id, doc_id), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.first_award_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    self.set_status('complete')

    response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}'.format(self.auction_id, self.first_award_id, doc_id), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) auction status")

# AuctionLotAwardComplaintResourceTest


def create_auction_award_complaint(self):
    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {
        'data': {'title': 'complaint title', 'description': 'complaint description',
                 'author': self.initial_organization, 'status': 'claim'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    self.assertEqual(complaint['author']['name'], self.initial_organization['name'])
    self.assertIn('id', complaint)
    self.assertIn(complaint['id'], response.headers['Location'])

    self.set_status('active.awarded')

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   self.auction_token), {"data": {
            "status": "answered",
            "resolutionType": "invalid",
            "resolution": "spam 100% " * 3
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "answered")
    self.assertEqual(response.json['data']["resolutionType"], "invalid")
    self.assertEqual(response.json['data']["resolution"], "spam 100% " * 3)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.awarded')

    self.set_status('unsuccessful')

    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {
        'data': {'title': 'complaint title', 'description': 'complaint description',
                 'author': self.initial_organization}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add complaint in current (unsuccessful) auction status")


def patch_auction_award_complaint(self):
    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description',
                                                   'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id, complaint['id']),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   owner_token), {"data": {
            "status": "claim"
        }})

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   self.auction_token), {"data": {
            "status": "answered",
            "resolutionType": "resolved",
            "resolution": "resolution text " * 2
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "answered")
    self.assertEqual(response.json['data']["resolutionType"], "resolved")
    self.assertEqual(response.json['data']["resolution"], "resolution text " * 2)

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   owner_token), {"data": {
            "satisfied": False,
            "status": "pending",
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "pending")

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   owner_token),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "cancelled")
    self.assertEqual(response.json['data']["cancellationReason"], "reason")

    response = self.app.patch_json('/auctions/{}/awards/{}/complaints/some_id'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "resolved", "resolution": "resolution text"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'complaint_id'}
    ])

    response = self.app.patch_json('/auctions/some_id/awards/some_id/complaints/some_id',
                                   {"data": {"status": "resolved", "resolution": "resolution text"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   owner_token), {"data": {
            "status": "cancelled",
            "cancellationReason": "reason"
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update complaint in current (cancelled) status")

    response = self.app.patch_json('/auctions/{}/awards/some_id/complaints/some_id'.format(self.auction_id),
                                   {"data": {"status": "resolved", "resolution": "resolution text"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.get(
        '/auctions/{}/awards/{}/complaints/{}'.format(self.auction_id, self.award_id, complaint['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "cancelled")
    self.assertEqual(response.json['data']["cancellationReason"], "reason")
    self.assertEqual(response.json['data']["resolutionType"], "resolved")
    self.assertEqual(response.json['data']["resolution"], "resolution text " * 2)

    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description',
                                                   'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    owner_token = response.json['access']['token']

    self.set_status('complete')

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   owner_token), {"data": {
            "status": "claim",
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update complaint in current (complete) auction status")


def get_auction_award_complaint(self):
    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description',
                                                   'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']

    response = self.app.get(
        '/auctions/{}/awards/{}/complaints/{}'.format(self.auction_id, self.award_id, complaint['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], complaint)

    response = self.app.get('/auctions/{}/awards/{}/complaints/some_id'.format(self.auction_id, self.award_id),
                            status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'complaint_id'}
    ])

    response = self.app.get('/auctions/some_id/awards/some_id/complaints/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])


def get_auction_award_complaints(self):
    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description',
                                                   'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']

    response = self.app.get('/auctions/{}/awards/{}/complaints'.format(self.auction_id, self.award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][0], complaint)

    response = self.app.get('/auctions/some_id/awards/some_id/complaints', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    auction = self.db.get(self.auction_id)
    for i in auction.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(auction)

    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description',
                                                   'author': self.initial_organization}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add complaint only in complaintPeriod")

# Auction2LotAwardComplaintResourceTest


def create_auction_award_complaint_2_lots(self):
    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {
        'data': {'title': 'complaint title', 'description': 'complaint description',
                 'author': self.initial_organization, 'status': 'claim'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    self.assertEqual(complaint['author']['name'], self.initial_organization['name'])
    self.assertIn('id', complaint)
    self.assertIn(complaint['id'], response.headers['Location'])

    self.set_status('active.awarded')

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   self.auction_token), {"data": {
            "status": "answered",
            "resolutionType": "invalid",
            "resolution": "spam 100% " * 3
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "answered")
    self.assertEqual(response.json['data']["resolutionType"], "invalid")
    self.assertEqual(response.json['data']["resolution"], "spam 100% " * 3)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.awarded')

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {
        'data': {'title': 'complaint title', 'description': 'complaint description',
                 'author': self.initial_organization}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add complaint only in active lot status")


def patch_auction_award_complaint_2_lots(self):
    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")

    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
        self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description',
                                                   'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   owner_token), {"data": {
            "status": "claim"
        }})

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   self.auction_token), {"data": {
            "status": "answered",
            "resolutionType": "resolved",
            "resolution": "resolution text " * 2
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "answered")
    self.assertEqual(response.json['data']["resolutionType"], "resolved")
    self.assertEqual(response.json['data']["resolution"], "resolution text " * 2)

    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(self.auction_id, self.award_id), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': self.initial_organization,
        'status': 'claim'
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    complaint = response.json['data']

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                   self.auction_token), {"data": {
            "status": "answered",
            "resolutionType": "resolved",
            "resolution": "resolution text"
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update complaint only in active lot status")

# AuctionAwardComplaintDocumentResourceTest


def not_found_award_complaint_documen(self):
    response = self.app.post('/auctions/some_id/awards/some_id/complaints/some_id/documents', status=404, upload_files=[
                             ('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.post('/auctions/{}/awards/some_id/complaints/some_id/documents'.format(self.auction_id), status=404, upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.post('/auctions/{}/awards/{}/complaints/some_id/documents'.format(self.auction_id, self.award_id), status=404, upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'complaint_id'}
    ])

    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents'.format(self.auction_id, self.award_id, self.complaint_id), status=404, upload_files=[
                             ('invalid_value', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.get('/auctions/some_id/awards/some_id/complaints/some_id/documents', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/awards/some_id/complaints/some_id/documents'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.get('/auctions/{}/awards/{}/complaints/some_id/documents'.format(self.auction_id, self.award_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'complaint_id'}
    ])

    response = self.app.get('/auctions/some_id/awards/some_id/complaints/some_id/documents/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/awards/some_id/complaints/some_id/documents/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.get('/auctions/{}/awards/{}/complaints/some_id/documents/some_id'.format(self.auction_id, self.award_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'complaint_id'}
    ])

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/some_id'.format(self.auction_id, self.award_id, self.complaint_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'document_id'}
    ])

    response = self.app.put('/auctions/some_id/awards/some_id/complaints/some_id/documents/some_id', status=404,
                            upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.put('/auctions/{}/awards/some_id/complaints/some_id/documents/some_id'.format(self.auction_id), status=404,
                            upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.put('/auctions/{}/awards/{}/complaints/some_id/documents/some_id'.format(self.auction_id, self.award_id), status=404, upload_files=[
                            ('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'complaint_id'}
    ])

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/some_id'.format(
        self.auction_id, self.award_id, self.complaint_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
    ])


def create_auction_award_complaint_document(self):
    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents'.format(
        self.auction_id, self.award_id, self.complaint_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (draft) complaint status")

    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents'.format(self.auction_id, self.award_id, self.complaint_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents?all=true'.format(self.auction_id, self.award_id, self.complaint_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}?download=some_id'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    self.set_status('complete')

    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents'.format(
        self.auction_id, self.award_id, self.complaint_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) auction status")


def put_auction_award_complaint_document(self):
    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id), upload_files=[('file', 'name.doc', 'content2')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    self.set_status('complete')

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) auction status")


def patch_auction_award_complaint_document(self):
    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

    response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), {"data": {
        "status": "claim",
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "claim")

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content', content_type='application/msword', status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (claim) complaint status")

    self.set_status('complete')

    response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) auction status")

# Auction2LotAwardComplaintDocumentResourceTest


def create_auction_award_2_lot_complaint_document(self):
    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents'.format(
        self.auction_id, self.award_id, self.complaint_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (draft) complaint status")

    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents'.format(self.auction_id, self.award_id, self.complaint_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents?all=true'.format(self.auction_id, self.award_id, self.complaint_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}?download=some_id'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents'.format(
        self.auction_id, self.award_id, self.complaint_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add document only in active lot status")


def put_auction_award_2_lot_complaint_document(self):
    response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id), upload_files=[('file', 'name.doc', 'content2')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), {"data": {
        "status": "claim",
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "claim")

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content', content_type='application/msword', status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (claim) complaint status")

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.put('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only in active lot status")


def patch_auction_award_2_lot_complaint_document(self):
        response = self.app.post('/auctions/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

        response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/auctions/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.auction_id, self.award_id, self.complaint_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, self.complaint_owner_token), {"data": {
            "status": "claim",
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], "claim")

        response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (claim) complaint status")

        response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
            'reason': 'cancellation reason',
            'status': 'active',
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update document only in active lot status")

# Auction2LotAwardDocumentResourceTest


def create_auction_2_lot_award_document(self):
    response = self.app.post('/auctions/{}/awards/{}/documents'.format(
        self.auction_id, self.award_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/documents'.format(self.auction_id, self.award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/awards/{}/documents?all=true'.format(self.auction_id, self.award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/awards/{}/documents/{}?download=some_id'.format(
        self.auction_id, self.award_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/awards/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.award_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.post('/auctions/{}/awards/{}/documents'.format(
        self.auction_id, self.award_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add document only in active lot status")


def put_auction_2_lot_award_document(self):
    response = self.app.post('/auctions/{}/awards/{}/documents'.format(
        self.auction_id, self.award_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/auctions/{}/awards/{}/documents/{}'.format(self.auction_id, self.award_id, doc_id),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.award_id, doc_id), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.award_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.award_id, doc_id), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/awards/{}/documents/{}?{}'.format(
        self.auction_id, self.award_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.put('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.award_id, doc_id), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only in active lot status")


def patch_auction_2_lot_award_document(self):
    response = self.app.post('/auctions/{}/awards/{}/documents'.format(
        self.auction_id, self.award_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}'.format(self.auction_id, self.award_id, doc_id), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/auctions/{}/awards/{}/documents/{}'.format(
        self.auction_id, self.award_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}'.format(self.auction_id, self.award_id, doc_id), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only in active lot status")
