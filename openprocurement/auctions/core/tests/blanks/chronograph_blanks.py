# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.api.models import get_now


# AuctionSwitchAuctionResourceTest


def switch_to_auction(self):
    response = self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.auction")

# AuctionSwitchUnsuccessfulResourceTest


def switch_to_unsuccessful(self):
    response = self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")
    if self.initial_lots:
        self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(["unsuccessful"]))

# AuctionAwardSwitchResourceTest


def switch_verification_to_unsuccessful(self):
    auction = self.db.get(self.auction_id)
    auction['awards'][0]['verificationPeriod']['endDate'] = auction['awards'][0]['verificationPeriod']['startDate']
    self.db.save(auction)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
    self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
    self.assertEqual(auction['status'], 'active.qualification')
    self.assertNotIn('endDate', auction['awardPeriod'])


def switch_payment_to_unsuccessful(self):
    bid_token = self.initial_bids_tokens[self.award['bid_id']]
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id,
                                                                  self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "pending.payment"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "pending.payment")

    auction = self.db.get(self.auction_id)
    auction['awards'][0]['paymentPeriod']['endDate'] = auction['awards'][0]['paymentPeriod']['startDate']
    self.db.save(auction)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
    self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
    self.assertEqual(auction['status'], 'active.qualification')
    self.assertNotIn('endDate', auction['awardPeriod'])


def switch_active_to_unsuccessful(self):
    bid_token = self.initial_bids_tokens[self.award['bid_id']]
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id,
                                                                  self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "pending.payment"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "pending.payment")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    auction = self.db.get(self.auction_id)
    auction['awards'][0]['signingPeriod']['endDate'] = auction['awards'][0]['signingPeriod']['startDate']
    self.db.save(auction)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
    self.assertEqual(auction['contracts'][0]['status'], 'cancelled')
    self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
    self.assertEqual(auction['status'], 'active.qualification')
    self.assertNotIn('endDate', auction['awardPeriod'])

# AuctionComplaintSwitchResourceTest


def switch_to_pending(self):
    response = self.app.post_json('/auctions/{}/complaints'.format(self.auction_id), {'data': {
        'title': 'complaint title',
        'description': 'complaint description',
        'author': self.initial_organization,
        'status': 'claim'
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'claim')

    auction = self.db.get(self.auction_id)
    auction['complaints'][0]['dateSubmitted'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in auction else 4)).isoformat()
    self.db.save(auction)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["complaints"][0]['status'], 'pending')


def switch_to_complaint(self):
    for status in ['invalid', 'resolved', 'declined']:
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/auctions/{}/complaints'.format(self.auction_id), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': self.initial_organization,
            'status': 'claim'
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'claim')
        complaint = response.json['data']

        response = self.app.patch_json(
            '/auctions/{}/complaints/{}?acc_token={}'.format(self.auction_id, complaint['id'], self.auction_token),
            {"data": {
                "status": "answered",
                "resolution": status * 4,
                "resolutionType": status
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "answered")
        self.assertEqual(response.json['data']["resolutionType"], status)

        auction = self.db.get(self.auction_id)
        auction['complaints'][-1]['dateAnswered'] = (
                get_now() - timedelta(days=1 if 'procurementMethodDetails' in auction else 4)).isoformat()
        self.db.save(auction)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["complaints"][-1]['status'], status)

# AuctionAwardComplaintSwitchResourceTest


def switch_to_pending_award(self):
    response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(self.auction_id, self.award_id),
                                  {'data': {
                                      'title': 'complaint title',
                                      'description': 'complaint description',
                                      'author': self.initial_organization,
                                      'status': 'claim'
                                  }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.json['data']['status'], 'claim')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    auction = self.db.get(self.auction_id)
    auction['awards'][0]['complaints'][0]['dateSubmitted'] = (
            get_now() - timedelta(days=1 if 'procurementMethodDetails' in auction else 4)).isoformat()
    self.db.save(auction)

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['awards'][0]["complaints"][0]['status'], 'pending')


def switch_to_complaint_award(self):
    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    for status in ['invalid', 'resolved', 'declined']:
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(self.auction_id, self.award_id),
                                      {'data': {
                                          'title': 'complaint title',
                                          'description': 'complaint description',
                                          'author': self.initial_organization,
                                          'status': 'claim'
                                      }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'claim')
        complaint = response.json['data']

        response = self.app.patch_json(
            '/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'],
                                                                       self.auction_token), {"data": {
                "status": "answered",
                "resolution": status * 4,
                "resolutionType": status
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "answered")
        self.assertEqual(response.json['data']["resolutionType"], status)

        auction = self.db.get(self.auction_id)
        auction['awards'][0]['complaints'][-1]['dateAnswered'] = (
                get_now() - timedelta(days=1 if 'procurementMethodDetails' in auction else 4)).isoformat()
        self.db.save(auction)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['awards'][0]["complaints"][-1]['status'], status)

# AuctionDontSwitchSuspendedAuction2ResourceTest


def switch_suspended_auction_to_auction(self):
    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'suspended': True}})
    response = self.set_status('active.auction', {'status': self.initial_status})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']["status"], "active.auction")

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'suspended': False}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active.auction")

# AuctionDontSwitchSuspendedAuctionResourceTest


def switch_suspended_verification_to_unsuccessful(self):
    auction = self.db.get(self.auction_id)
    auction['awards'][0]['verificationPeriod']['endDate'] = auction['awards'][0]['verificationPeriod']['startDate']
    self.db.save(auction)

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'suspended': True}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'pending.verification')
    self.assertEqual(auction['awards'][1]['status'], 'pending.waiting')

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'suspended': False}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
    self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
    self.assertEqual(auction['status'], 'active.qualification')
    self.assertNotIn('endDate', auction['awardPeriod'])


def switch_suspended_payment_to_unsuccessful(self):
    bid_token = self.initial_bids_tokens[self.award['bid_id']]
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id,
                                                                  self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "pending.payment"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "pending.payment")

    auction = self.db.get(self.auction_id)
    auction['awards'][0]['paymentPeriod']['endDate'] = auction['awards'][0]['paymentPeriod']['startDate']
    self.db.save(auction)

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'suspended': True}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'pending.payment')
    self.assertEqual(auction['awards'][1]['status'], 'pending.waiting')

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'suspended': False}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
    self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
    self.assertEqual(auction['status'], 'active.qualification')
    self.assertNotIn('endDate', auction['awardPeriod'])


def switch_suspended_active_to_unsuccessful(self):
    bid_token = self.initial_bids_tokens[self.award['bid_id']]
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id,
                                                                  self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "pending.payment"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "pending.payment")

    response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id),
                                   {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    auction = self.db.get(self.auction_id)
    auction['awards'][0]['signingPeriod']['endDate'] = auction['awards'][0]['signingPeriod']['startDate']
    self.db.save(auction)

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'suspended': True}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'active')
    self.assertEqual(auction['contracts'][0]['status'], 'pending')
    self.assertEqual(auction['awards'][1]['status'], 'pending.waiting')
    self.assertEqual(auction['status'], 'active.awarded')
    self.assertIn('endDate', auction['awardPeriod'])

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'suspended': False}})

    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    auction = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
    self.assertEqual(auction['contracts'][0]['status'], 'cancelled')
    self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
    self.assertEqual(auction['status'], 'active.qualification')
    self.assertNotIn('endDate', auction['awardPeriod'])
