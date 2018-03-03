# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now, Period
from openprocurement.api.utils import calculate_business_date

from openprocurement.auctions.core.utils import get_related_contract_of_award
from openprocurement.auctions.core.plugins.awarding.v3.constants import (
    VERIFY_AUCTION_PROTOCOL_TIME
)
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

def award_activation_creates_contract(self):
    # Create Award
    request_path = '/auctions/{0}/awards'.format(self.auction_id)
    response = self.app.post_json(
        request_path,
        {'data': {
            'suppliers': [self.initial_organization],
            'bid_id': self.initial_bids[0]['id']
        }}
    )
    award = response.json['data']

    # Check that Auction hasn't any contracts for now
    pre_award_activation_auction_response = self.app.get(
        '/auctions/{0}'.format(
            self.auction_id
        )
    )
    pre_award_activation_auction = pre_award_activation_auction_response.json['data']
    self.assertEqual(pre_award_activation_auction.get('contracts'), None)

    # Load auction protocol into Award to make it's activation possible
    response = self.app.post(
        '/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id,
            award['id'],
            self.auction_token
        ),
        upload_files=[(
            'file',
            'auction_protocol.pdf',
            'content'
        )]
    )
    doc_id = response.json["data"]['id']
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.auction_id,
            award['id'],
            doc_id,
            self.auction_token
        ),
        {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }}
    )

    # Actuallly activate Award
    response = self.app.patch_json(
        '/auctions/{}/awards/{}'.format(
            self.auction_id,
            award['id']
        ),
        {"data": {
            "status": "active"
        }}
    )
    self.assertEqual(response.json['data']['status'], u'active')

    # Check that contracts have been created
    post_award_activation_auction_response = self.app.get(
        '/auctions/{0}'.format(
            self.auction_id
        )
    )
    post_award_activation_auction = post_award_activation_auction_response.json['data']
    contract = post_award_activation_auction.get('contracts')[0]
    self.assertEqual(
        contract['signingPeriod'],
        award['signingPeriod']
    )
    self.assertEqual(
        contract['status'],
        'pending'
    )

# AuctionAwardProcessTest


def patch_auction_award_participant_disqualification(self):
    self.upload_auction_protocol(self.first_award)

    # set award status "active"
    url = '/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id)
    json_data = {'data': {'status': 'active'}}
    response = self.app.patch_json(url, json_data)
    self.assertEqual(response.status, '200 OK')

    # get auction
    url = '/auctions/{}'.format(self.auction_id)
    response = self.app.get(url)
    self.assertEqual(response.status, '200 OK')

    # upload contract into Contract
    data = response.json
    contract = data['data']['contracts'][0]
    url = '/auctions/{}/contracts/{}/documents'.format(self.auction_id,
                                                       contract['id'])
    json_data = {
        'data': {
            'url': self.generate_docservice_url(),
            'title': 'informative title',
            'hash': 'md5:00000000000000000000000000000000',
            'format': 'application/msword'
        }
    }
    response = self.app.post_json(url, json_data)
    self.assertEqual(response.status, '201 Created')

    # set dateSigned to contract
    json_data = {'data': {'dateSigned': get_now().isoformat()}}
    url = '/auctions/{}/contracts/{}'.format(self.auction_id, contract['id'])
    response = self.app.patch_json(url, json_data)
    self.assertEqual(response.status, '200 OK')
    # try participant_disqualification
    url = '/auctions/{}/awards/{}'.format(self.auction_id, self.first_award_id)
    json_data = {
        'data': {
            'status': 'unsuccessful',
            'description': 'Candidate is strange',
            'title': 'Disqualified'
        }
    }
    response = self.app.patch_json(url, json_data,  status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     'You cannot disqualify the bidder whose'
                     ' contract has already been activated.')


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


def created_award_have_periods_set(self):
    awards = [self.first_award,]
    periods = ['signingPeriod', 'verificationPeriod']
    dates = ['startDate', 'endDate']

    for count, award in enumerate(awards):
        for period in periods:
            for date in dates:
                self.assertNotEqual(
                    award.get(period, {}).get(date),
                    None,
                    'Date not set in {0} award '
                    '{1}.{2}'.format(
                        count,
                        period,
                        date
                    )
                )


def created_awards_statuses(self):
    self.assertEqual(
        self.first_award['status'],
        'pending'
    )
    self.assertEqual(
        self.second_award['status'],
        'pending.waiting'
    )

def verification_period_length(self):
    auction = self.db.get(self.auction_id)
    period = Period(self.first_award['verificationPeriod'])
    actual_period_length = period.endDate - period.startDate

    target_end_date = calculate_business_date(period.startDate, VERIFY_AUCTION_PROTOCOL_TIME, auction, True)
    round_to_18_hour_delta = period.endDate.replace(hour=18, minute=0, second=0) - period.endDate
    target_end_date = calculate_business_date(period.endDate, round_to_18_hour_delta, auction, False)
    target_period_length = target_end_date - period.startDate

    self.assertLessEqual(
        actual_period_length.days,
        target_period_length.days
    )
