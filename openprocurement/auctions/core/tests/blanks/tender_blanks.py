# -*- coding: utf-8 -*-
import unittest

from datetime import timedelta
from copy import deepcopy
from uuid import uuid4

from openprocurement.api.utils import get_now
from openprocurement.api.utils import ROUTE_PREFIX


def create_auction_draft_with_registry(self):
    data = self.initial_data.copy()
    items = data.pop('items')
    dgf_id = data.pop('dgfID')
    data.update({'status': 'draft', 'merchandisingObject': uuid4().hex})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'draft')

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'value': {'amount': 100}}},
                                   status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"Can't update auction in current (draft) status", u'location': u'body', u'name': u'data'}
    ])

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'pending.verification'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'pending.verification')

    self.app.authorization = ('Basic', ('convoy', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction['id']),
                                   {'data': {'items': items, 'dgfID': dgf_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']['items']), len(items))
    self.assertEqual(response.json['data']['dgfID'], dgf_id)

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'active.tendering')

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'active.tendering')


def convoy_change_status(self):
    # Check auctions list count
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    # Create auction without merchandisingObject
    data = self.initial_data.copy()
    data.update({'status': 'draft'})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner
    # without merchandisingObject
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'pending.verification'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': u"Can't switch auction to status (pending.verification) without merchandisingObject", u'location': u'body', u'name': u'data'}])

    # Create auction with items
    data.update({'merchandisingObject': uuid4().hex})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner
    # with items
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token),
                                   {'data': {'status': 'pending.verification'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"This field is not required.",
         u'location': u'body', u'name': u'items'}])


    # Create auction with merchandisingObject and without items and without dgfID
    data = self.initial_data.copy()
    data.update({'status': 'draft', 'merchandisingObject': uuid4().hex})
    items = data.pop('items')
    dgf_id = data.pop('dgfID')
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'pending.verification'}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'pending.verification')

    self.app.authorization = ('Basic', ('convoy', ''))

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'pending.verification' -> 'active.tendering' via convoy without items and dgfID
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"This field is required."],
         u'location': u'body', u'name': u'items'},
        {u'description': [u"This field is required."],
         u'location': u'body', u'name': u'dgfID'}])

    # Add items and dgfID via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'items': items, 'dgfID': dgf_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']['items']), len(items))
    self.assertEqual(response.json['data']['dgfID'], dgf_id)

    # Switch auction status 'pending.verification' -> 'active.tendering' via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'active.tendering')

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'active.tendering' -> 'invalid' via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'invalid'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': u"Can't update auction in current (active.tendering) status", u'location': u'body', u'name': u'data'}])

    # Create auction with merchandisingObject
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'pending.verification'}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'pending.verification')

    self.app.authorization = ('Basic', ('convoy', ''))
    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'pending.verification' -> 'invalid' via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'invalid'}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'invalid')

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'invalid' -> 'active.tendering' via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': u"Can't update auction in current (invalid) status", u'location': u'body', u'name': u'data'}])

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Create auction with merchandisingObject and without items and with dgfID
    self.app.authorization = ('Basic', ('broker', ''))
    data = self.initial_data.copy()
    data.update({'status': 'draft', 'merchandisingObject': uuid4().hex})
    data.pop('items')
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner with dgfID
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'pending.verification'}},
                                   status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"This field is not required.",
         u'location': u'body', u'name': u'dgfID'}])

# AuctionTest


def simple_add_auction(self):
    u = self.auction(self.initial_data)
    u.auctionID = "UA-EA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.auctionID == fromdb['auctionID']
    assert u.doc_type == "Auction"

    u.delete_instance(self.db)

# AuctionResourceTest


def empty_listing(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertNotIn('{\n    "', response.body)
    self.assertNotIn('callback({', response.body)
    self.assertEqual(response.json['next_page']['offset'], '')
    self.assertNotIn('prev_page', response.json)

    response = self.app.get('/auctions?opt_jsonp=callback')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertNotIn('{\n    "', response.body)
    self.assertIn('callback({', response.body)

    response = self.app.get('/auctions?opt_pretty=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)
    self.assertNotIn('callback({', response.body)

    response = self.app.get('/auctions?opt_jsonp=callback&opt_pretty=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('{\n    "', response.body)
    self.assertIn('callback({', response.body)

    response = self.app.get('/auctions?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertIn('descending=1', response.json['next_page']['uri'])
    self.assertIn('limit=10', response.json['next_page']['uri'])
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertIn('limit=10', response.json['prev_page']['uri'])

    response = self.app.get('/auctions?feed=changes')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertEqual(response.json['next_page']['offset'], '')
    self.assertNotIn('prev_page', response.json)

    response = self.app.get('/auctions?feed=changes&offset=0', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Offset expired/invalid', u'location': u'querystring', u'name': u'offset'}
    ])

    response = self.app.get('/auctions?feed=changes&descending=1&limit=10')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertIn('descending=1', response.json['next_page']['uri'])
    self.assertIn('limit=10', response.json['next_page']['uri'])
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertIn('limit=10', response.json['prev_page']['uri'])


def listing(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    auctions = []

    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auctions.append(response.json['data'])

    ids = ','.join([i['id'] for i in auctions])

    while True:
        response = self.app.get('/auctions')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                     set([i['dateModified'] for i in auctions]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in auctions]))

    while True:
        response = self.app.get('/auctions?offset={}'.format(offset))
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/auctions?limit=2')
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('prev_page', response.json)
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.get('/auctions', params=[('opt_fields', 'status')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
    self.assertIn('opt_fields=status', response.json['next_page']['uri'])

    response = self.app.get('/auctions', params=[('opt_fields', 'status,enquiryPeriod')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status', u'enquiryPeriod']))
    self.assertIn('opt_fields=status%2CenquiryPeriod', response.json['next_page']['uri'])

    response = self.app.get('/auctions?descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
    self.assertEqual([i['dateModified'] for i in response.json['data']],
                     sorted([i['dateModified'] for i in auctions], reverse=True))

    response = self.app.get('/auctions?descending=1&limit=2')
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 0)

    test_auction_data2 = self.initial_data.copy()
    test_auction_data2['mode'] = 'test'
    response = self.app.post_json('/auctions', {'data': test_auction_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    while True:
        response = self.app.get('/auctions?mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/auctions?mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)


def listing_changes(self):
    response = self.app.get('/auctions?feed=changes')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    auctions = []

    for i in range(3):
        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auctions.append(response.json['data'])

    ids = ','.join([i['id'] for i in auctions])

    while True:
        response = self.app.get('/auctions?feed=changes')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(','.join([i['id'] for i in response.json['data']]), ids)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                     set([i['dateModified'] for i in auctions]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in auctions]))

    response = self.app.get('/auctions?feed=changes&limit=2')
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('prev_page', response.json)
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.get('/auctions?feed=changes', params=[('opt_fields', 'status')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
    self.assertIn('opt_fields=status', response.json['next_page']['uri'])

    response = self.app.get('/auctions?feed=changes', params=[('opt_fields', 'status,enquiryPeriod')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status', u'enquiryPeriod']))
    self.assertIn('opt_fields=status%2CenquiryPeriod', response.json['next_page']['uri'])

    response = self.app.get('/auctions?feed=changes&descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
    self.assertEqual([i['dateModified'] for i in response.json['data']],
                     sorted([i['dateModified'] for i in auctions], reverse=True))

    response = self.app.get('/auctions?feed=changes&descending=1&limit=2')
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 0)

    test_auction_data2 = self.initial_data.copy()
    test_auction_data2['mode'] = 'test'
    response = self.app.post_json('/auctions', {'data': test_auction_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    while True:
        response = self.app.get('/auctions?feed=changes&mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/auctions?feed=changes&mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)


def listing_draft(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    auctions = []
    data = self.initial_data.copy()
    data.update({'status': 'draft'})

    for i in range(3):
        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auctions.append(response.json['data'])
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

    ids = ','.join([i['id'] for i in auctions])

    while True:
        response = self.app.get('/auctions')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]),
                     set([i['dateModified'] for i in auctions]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in auctions]))


def create_auction_draft(self):
    data = self.initial_data.copy()
    data.update({'status': 'draft'})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'draft')

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'value': {'amount': 100}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"Can't update auction in current (draft) status", u'location': u'body', u'name': u'data'}
    ])

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': self.initial_status}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], self.initial_status)

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], self.initial_status)


def get_auction(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    response = self.app.get('/auctions/{}?opt_jsonp=callback'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get('/auctions/{}?opt_pretty=1'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "data": {\n        "', response.body)


@unittest.skip("this test requires fixed version of jsonpatch library")
def patch_tender_jsonpatch(self):
    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    tender = response.json['data']

    import random
    response = self.app.patch_json('/auctions/{}'.format(tender['id']),
                                   {'data': {'items': [{"additionalClassifications": [
                                       {
                                           "scheme": "ДКПП",
                                           "id": "{}".format(i),
                                           "description": "description #{}".format(i)
                                       }
                                       for i in random.sample(range(30), 25)
                                   ]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}'.format(tender['id']),
                                   {'data': {'items': [{"additionalClassifications": [
                                       {
                                           "scheme": "ДКПП",
                                           "id": "{}".format(i),
                                           "description": "description #{}".format(i)
                                       }
                                       for i in random.sample(range(30), 20)
                                   ]}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')


def auction_features_invalid(self):
    data = self.initial_data.copy()
    item = data['items'][0].copy()
    item['id'] = "1"
    data['items'] = [item, item.copy()]
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Item id should be uniq for all items'], u'location': u'body', u'name': u'items'}
    ])
    data['items'][0]["id"] = "0"
    data['features'] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "lot",
            "title": u"Потужність всмоктування",
            "enum": [
                {
                    "value": 0.1,
                    "title": u"До 1000 Вт"
                },
                {
                    "value": 0.15,
                    "title": u"Більше 1000 Вт"
                }
            ]
        }
    ]
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedItem': [u'This field is required.']}], u'location': u'body', u'name': u'features'}
    ])
    data['features'][0]["relatedItem"] = "2"
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedItem': [u'relatedItem should be one of lots']}], u'location': u'body',
         u'name': u'features'}
    ])
    data['features'][0]["featureOf"] = "item"
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedItem': [u'relatedItem should be one of items']}], u'location': u'body',
         u'name': u'features'}
    ])
    data['features'][0]["relatedItem"] = "1"
    data['features'][0]["enum"][0]["value"] = 0.5
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'enum': [{u'value': [u'Float value should be less than 0.3.']}]}], u'location': u'body',
         u'name': u'features'}
    ])
    data['features'][0]["enum"][0]["value"] = 0.15
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'enum': [u'Feature value should be uniq for feature']}], u'location': u'body',
         u'name': u'features'}
    ])
    data['features'][0]["enum"][0]["value"] = 0.1
    data['features'].append(data['features'][0].copy())
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Feature code should be uniq for all features'], u'location': u'body', u'name': u'features'}
    ])
    data['features'][1]["code"] = u"OCDS-123454-YEARS"
    data['features'][1]["enum"][0]["value"] = 0.2
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Sum of max value of all features should be less then or equal to 30%'],
         u'location': u'body', u'name': u'features'}
    ])


def auction_features(self):
    data = self.initial_data.copy()
    item = data['items'][0].copy()
    item['id'] = "1"
    data['items'] = [item]
    data['features'] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": u"Потужність всмоктування",
            "title_en": u"Air Intake",
            "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [
                {
                    "value": 0.05,
                    "title": u"До 1000 Вт"
                },
                {
                    "value": 0.1,
                    "title": u"Більше 1000 Вт"
                }
            ]
        },
        {
            "code": "OCDS-123454-YEARS",
            "featureOf": "tenderer",
            "title": u"Років на ринку",
            "title_en": u"Years trading",
            "description": u"Кількість років, які організація учасник працює на ринку",
            "enum": [
                {
                    "value": 0.05,
                    "title": u"До 3 років"
                },
                {
                    "value": 0.1,
                    "title": u"Більше 3 років"
                }
            ]
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "title_en": u"Postponement of payment",
            "description": u"Термін відстрочки платежу",
            "enum": [
                {
                    "value": 0.05,
                    "title": u"До 90 днів"
                },
                {
                    "value": 0.1,
                    "title": u"Більше 90 днів"
                }
            ]
        }
    ]
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['features'], data['features'])

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'features': [{
        "featureOf": "tenderer",
        "relatedItem": None
    }, {}, {}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('features', response.json['data'])
    self.assertNotIn('relatedItem', response.json['data']['features'][0])

    response = self.app.patch_json('/auctions/{}'.format(auction['id']),
                                   {'data': {'tenderPeriod': {'startDate': None}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('features', response.json['data'])

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'features': []}})
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('features', response.json['data'])


def patch_auction(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']
    dateModified = auction.pop('dateModified')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token),
                                   {'data': {'status': 'cancelled'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['status'], 'cancelled')

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'cancelled'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['status'], 'cancelled')

    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token),
                                   {'data': {'procuringEntity': {'kind': 'defense'}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('kind', response.json['data']['procuringEntity'])

    # response = self.app.patch_json('/auctions/{}'.format(
    # auction['id']), {'data': {'tenderPeriod': {'startDate': None}}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertNotIn('startDate', response.json['data']['tenderPeriod'])

    # response = self.app.patch_json('/auctions/{}'.format(
    # auction['id']), {'data': {'tenderPeriod': {'startDate': auction['enquiryPeriod']['endDate']}}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('startDate', response.json['data']['tenderPeriod'])

    response = self.app.patch_json('/auctions/{}'.format(
        auction['id']), {'data': {'procurementMethodRationale': 'Open'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_auction = response.json['data']
    new_dateModified = new_auction.pop('dateModified')
    # auction['procurementMethodRationale'] = 'Open'
    self.assertEqual(auction, new_auction)
    self.assertEqual(dateModified, new_dateModified)

    response = self.app.patch_json('/auctions/{}'.format(
        auction['id']), {'data': {'dateModified': new_dateModified}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_auction2 = response.json['data']
    new_dateModified2 = new_auction2.pop('dateModified')
    self.assertEqual(new_auction, new_auction2)
    self.assertEqual(new_dateModified, new_dateModified2)

    revisions = self.db.get(auction['id']).get('revisions')
    self.assertEqual(revisions[-1][u'changes'][0]['op'], u'remove')
    self.assertEqual(revisions[-1][u'changes'][0]['path'], u'/procurementMethod')

    response = self.app.patch_json('/auctions/{}'.format(
        auction['id']), {'data': {'items': [self.initial_data['items'][0]]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    # response = self.app.patch_json('/auctions/{}'.format(
    # auction['id']), {'data': {'items': [{}, self.initial_data['items'][0]]}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # item0 = response.json['data']['items'][0]
    # item1 = response.json['data']['items'][1]
    # self.assertNotEqual(item0.pop('id'), item1.pop('id'))
    # self.assertEqual(item0, item1)

    # response = self.app.patch_json('/auctions/{}'.format(
    # auction['id']), {'data': {'items': [{}]}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(len(response.json['data']['items']), 1)

    # response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'items': [{"classification": {
    # "scheme": u"CAV",
    # "id": u"04000000-8",
    # "description": u"Нерухоме майно"
    # }}]}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')

    # response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'items': [{"additionalClassifications": [auction['items'][0]["classification"]]}]}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/auctions/{}'.format(
        auction['id']), {'data': {'enquiryPeriod': {'endDate': new_dateModified2}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    new_auction = response.json['data']
    self.assertIn('startDate', new_auction['enquiryPeriod'])

    # response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {"data": {"guarantee": {"amount": 12, "valueAddedTaxIncluded": True}}}, status=422)
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.json['errors'][0], {u'description': {u'valueAddedTaxIncluded': u'Rogue field'}, u'location': u'body', u'name': u'guarantee'})

    # response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {"data": {"guarantee": {"amount": 12}}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertIn('guarantee', response.json['data'])
    # self.assertEqual(response.json['data']['guarantee']['amount'], 12)
    # self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

    # response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {"data": {"guarantee": {"currency": "USD"}}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

    # response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.auction'}})
    # self.assertEqual(response.status, '200 OK')

    # response = self.app.get('/auctions/{}'.format(auction['id']))
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('auctionUrl', response.json['data'])

    auction_data = self.db.get(auction['id'])
    auction_data['status'] = 'complete'
    self.db.save(auction_data)

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.auction'}},
                                   status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update auction in current (complete) status")


def dateModified_auction(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    dateModified = auction['dateModified']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['dateModified'], dateModified)

    response = self.app.patch_json('/auctions/{}'.format(
        auction['id']), {'data': {'procurementMethodRationale': 'Open'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['dateModified'], dateModified)
    auction = response.json['data']
    dateModified = auction['dateModified']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)
    self.assertEqual(response.json['data']['dateModified'], dateModified)


def auction_not_found(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.get('/auctions/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'auction_id'}
    ])

    response = self.app.patch_json(
        '/auctions/some_id', {'data': {}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'auction_id'}
    ])

    # put custom document object into database to check tender construction on non-Tender data
    data = {'contract': 'test', '_id': uuid4().hex}
    self.db.save(data)

    response = self.app.get('/auctions/{}'.format(data['_id']), status=404)
    self.assertEqual(response.status, '404 Not Found')


def guarantee(self):
    data = deepcopy(self.initial_data)
    data['guarantee'] = {"amount": 100, "currency": "UAH"}
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertIn('guarantee', response.json['data'])
    self.assertEqual(response.json['data']['guarantee']['amount'], 100)
    self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')


def auction_Administrator_change(self):
    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']

    response = self.app.post_json('/auctions/{}/questions'.format(auction['id']), {
        'data': {'title': 'question title', 'description': 'question description',
                 'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction['id']),
                                   {'data': {'mode': u'test', 'procuringEntity': {"identifier": {"id": "00000000"}}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['mode'], u'test')
    self.assertEqual(response.json['data']["procuringEntity"]["identifier"]["id"], "00000000")

    response = self.app.patch_json('/auctions/{}/questions/{}'.format(auction['id'], question['id']),
                                   {"data": {"answer": "answer"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {"location": "url", "name": "role", "description": "Forbidden"}
    ])
    self.app.authorization = authorization

    response = self.app.post_json('/auctions', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']

    response = self.app.post_json('/auctions/{}/cancellations'.format(auction['id']),
                                  {'data': {'reason': 'cancellation reason', 'status': 'active'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'mode': u'test'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['mode'], u'test')

# AuctionProcessTest


def invalid_auction_conditions(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty auctions listing
    response = self.app.get('/auctions')
    self.assertEqual(response.json['data'], [])
    # create auction
    response = self.app.post_json('/auctions',
                                  {"data": self.initial_data})
    auction_id = self.auction_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')
    # create compaint
    response = self.app.post_json('/auctions/{}/complaints'.format(auction_id),
                                  {'data': {'title': 'invalid conditions', 'description': 'description',
                                            'author': self.initial_organization, 'status': 'claim'}})
    complaint_id = response.json['data']['id']
    complaint_owner_token = response.json['access']['token']
    # answering claim
    self.app.patch_json('/auctions/{}/complaints/{}?acc_token={}'.format(auction_id, complaint_id, owner_token),
                        {"data": {
                            "status": "answered",
                            "resolutionType": "resolved",
                            "resolution": "I will cancel the auction"
                        }})
    # satisfying resolution
    self.app.patch_json(
        '/auctions/{}/complaints/{}?acc_token={}'.format(auction_id, complaint_id, complaint_owner_token),
        {"data": {
            "satisfied": True,
            "status": "resolved"
        }})
    # cancellation
    self.app.post_json('/auctions/{}/cancellations?acc_token={}'.format(auction_id, owner_token), {'data': {
        'reason': 'invalid conditions',
        'status': 'active'
    }})
    # check status
    response = self.app.get('/auctions/{}'.format(auction_id))
    self.assertEqual(response.json['data']['status'], 'cancelled')


def one_valid_bid_auction(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty auctions listing
    response = self.app.get('/auctions')
    self.assertEqual(response.json['data'], [])
    # create auction
    response = self.app.post_json('/auctions',
                                  {"data": self.initial_data})
    auction_id = self.auction_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    response = self.set_status('active.tendering', {"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}})
    self.assertIn("auctionPeriod", response.json['data'])
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == self.test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
    # switch to active.qualification
    self.set_status('active.auction', {'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"id": auction_id}})
    self.assertNotIn('auctionPeriod', response.json['data'])
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    award_date = [i['date'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as active
    response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token), {"data": {"status": "active"}})
    self.assertNotEqual(response.json['data']['date'], award_date)

    # get contract id
    response = self.app.get('/auctions/{}'.format(auction_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    auction = self.db.get(auction_id)
    for i in auction.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(auction)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(auction_id, contract_id, owner_token), {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}'.format(auction_id))
    self.assertEqual(response.json['data']['status'], 'complete')


def one_invalid_bid_auction(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty auctions listing
    response = self.app.get('/auctions')
    self.assertEqual(response.json['data'], [])
    # create auction
    response = self.app.post_json('/auctions',
                                  {"data": self.initial_data})
    auction_id = self.auction_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == self.test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True}})
    # switch to active.qualification
    self.set_status('active.auction', {"auctionPeriod": {"startDate": None}, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"id": auction_id}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    # set award as unsuccessful
    response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                                   {"data": {"status": "unsuccessful"}})
    # time travel
    auction = self.db.get(auction_id)
    for i in auction.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(auction)
    # set auction status after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"id": auction_id}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}'.format(auction_id))
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
