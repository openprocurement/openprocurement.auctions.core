from uuid import uuid4
from copy import deepcopy

from openprocurement.api.models import get_now

from openprocurement.auctions.dgf.migration import migrate_data


def migrate_pendingVerification_pending(self):
    auction = self.db.get(self.auction_id)
    now = get_now()

    pending_verification_award = {
        "id": uuid4().hex,
        "date": now.isoformat(),
        "bid_id": auction["bids"][0]["id"],
        "status": "pending.verification",
        "suppliers": auction["bids"][0]["tenderers"],
        'value': auction['value'],
        "complaintPeriod": {
            "startDate": now.isoformat(),
        },
        "paymentPeriod": {
            "startDate": now.isoformat()
        },
        "signingPeriod": {
            "startDate": now.isoformat()
        },
        "verificationPeriod": {
            "startDate": now.isoformat()
        }
    }
    pending_waiting_award = deepcopy(pending_verification_award)
    pending_waiting_award['id'] = uuid4().hex
    pending_waiting_award['status'] = 'pending.waiting'
    pending_waiting_award['complaintPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['paymentPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['signingPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['verificationPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['bid_id'] = auction['bids'][1]['id']

    auction['awards'] = [pending_waiting_award, pending_verification_award]
    auction.update(auction)
    self.db.save(auction)
    migrate_data(self.app.app.registry, 2)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    auction = response.json['data']
    self.assertEqual(auction['status'], u'active.qualification')
    self.assertEqual(auction['awards'][1]['status'], u'pending')
    self.assertEqual(auction['awards'][0]['status'], u'pending.waiting')


def migrate_pendingPayment_active(self):
    auction = self.db.get(self.auction_id)
    now = get_now()

    pending_payment_award = {
        "id": uuid4().hex,
        "date": now.isoformat(),
        "bid_id": auction["bids"][0]["id"],
        "status": "pending.payment",
        "suppliers": auction["bids"][0]["tenderers"],
        'value': auction['value'],
        "complaintPeriod": {
            "startDate": now.isoformat(),
        },
        "paymentPeriod": {
            "startDate": now.isoformat()
        },
        "signingPeriod": {
            "startDate": now.isoformat()
        },
        "verificationPeriod": {
            "startDate": now.isoformat()
        }
    }
    pending_waiting_award = deepcopy(pending_payment_award)
    pending_waiting_award['id'] = uuid4().hex
    pending_waiting_award['status'] = 'pending.waiting'
    pending_waiting_award['complaintPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['paymentPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['signingPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['verificationPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['bid_id'] = auction['bids'][1]['id']

    auction['awards'] = [pending_waiting_award, pending_payment_award]
    auction.update(auction)
    self.db.save(auction)
    migrate_data(self.app.app.registry, 2)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    auction = response.json['data']
    self.assertEqual(auction['awards'][1]['status'], u'active')
    self.assertEqual(auction['awards'][0]['status'], u'pending.waiting')

    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contracts = response.json['data']
    self.assertEqual(len(contracts), 1)
    self.assertEqual(contracts[0]['status'], 'pending')
    self.assertEqual(contracts[0]['signingPeriod'], pending_payment_award['signingPeriod'])


def migrate_contract_cancelled(self):
    auction = self.db.get(self.auction_id)
    now = get_now()

    pending_verification_award = {
        "id": uuid4().hex,
        "date": now.isoformat(),
        "bid_id": auction["bids"][0]["id"],
        "status": "pending.verification",
        "suppliers": auction["bids"][0]["tenderers"],
        'value': auction['value'],
        "complaintPeriod": {
            "startDate": now.isoformat(),
        },
        "paymentPeriod": {
            "startDate": now.isoformat()
        },
        "signingPeriod": {
            "startDate": now.isoformat()
        },
        "verificationPeriod": {
            "startDate": now.isoformat()
        }
    }
    unsuccessful_award = deepcopy(pending_verification_award)
    unsuccessful_award['id'] = uuid4().hex
    unsuccessful_award['status'] = 'unsuccessful'
    unsuccessful_award['complaintPeriod']['endDate'] = now.isoformat()
    unsuccessful_award['paymentPeriod']['endDate'] = now.isoformat()
    unsuccessful_award['signingPeriod']['endDate'] = now.isoformat()
    unsuccessful_award['verificationPeriod']['endDate'] = now.isoformat()
    unsuccessful_award['bid_id'] = auction['bids'][1]['id']

    auction['awards'] = [unsuccessful_award, pending_verification_award]

    auction['contracts'] = [{
        'awardID': unsuccessful_award['id'],
        'suppliers': unsuccessful_award['suppliers'],
        'value': unsuccessful_award['value'],
        'date': now.isoformat(),
        'items': auction['items'],
        'contractID': '{}-11'.format(auction['auctionID']),
        'status': 'cancelled'
    }]

    auction.update(auction)
    self.db.save(auction)
    migrate_data(self.app.app.registry, 2)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    auction = response.json['data']
    self.assertEqual(auction['status'], u'active.qualification')
    self.assertEqual(auction['awards'][1]['status'], u'pending')

    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contracts = response.json['data']
    self.assertEqual(len(contracts), 1)
    self.assertEqual(contracts[0]['status'], 'cancelled')
    self.assertEqual(contracts[0]['signingPeriod'], unsuccessful_award['signingPeriod'])


def migrate_contract_pending(self):
    self.set_status('active.awarded')
    auction = self.db.get(self.auction_id)
    now = get_now()

    active_award = {
        "id": uuid4().hex,
        "date": now.isoformat(),
        "bid_id": auction["bids"][0]["id"],
        "status": "active",
        "suppliers": auction["bids"][0]["tenderers"],
        'value': auction['value'],
        "complaintPeriod": {
            "startDate": now.isoformat(),
        },
        "paymentPeriod": {
            "startDate": now.isoformat()
        },
        "signingPeriod": {
            "startDate": now.isoformat()
        },
        "verificationPeriod": {
            "startDate": now.isoformat()
        }
    }
    pending_waiting_award = deepcopy(active_award)
    pending_waiting_award['id'] = uuid4().hex
    pending_waiting_award['status'] = 'pending.waiting'
    pending_waiting_award['complaintPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['paymentPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['signingPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['verificationPeriod']['endDate'] = now.isoformat()
    pending_waiting_award['bid_id'] = auction['bids'][1]['id']

    auction['awards'] = [active_award, pending_waiting_award]

    auction['contracts'] = [{
        'awardID': active_award['id'],
        'suppliers': active_award['suppliers'],
        'value': active_award['value'],
        'date': now.isoformat(),
        'items': auction['items'],
        'contractID': '{}-11'.format(auction['auctionID']),
        'status': 'pending'
    }]

    auction.update(auction)
    self.db.save(auction)
    migrate_data(self.app.app.registry, 2)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    auction = response.json['data']
    self.assertEqual(auction['status'], u'active.awarded')
    self.assertEqual(auction['awards'][0]['status'], u'active')
    self.assertEqual(auction['awards'][1]['status'], u'pending.waiting')

    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contracts = response.json['data']
    self.assertEqual(len(contracts), 1)
    self.assertEqual(contracts[0]['status'], 'pending')
    self.assertEqual(contracts[0]['signingPeriod'], active_award['signingPeriod'])
