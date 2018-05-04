from uuid import uuid4
from copy import deepcopy

from isodate import parse_datetime

from openprocurement.api.utils import get_now, set_specific_hour

from openprocurement.auctions.core.plugins.awarding.v2.tests.award import (
    award_fixture
)
from openprocurement.auctions.core.plugins.contracting.v3.constants import (
    CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
)


def migrate_pendingVerification_pending(self):
    auction = self.db.get(self.auction_id)

    pending_verification_award = award_fixture(auction, 'pending.verification', 0)
    pending_waiting_award = award_fixture(auction, 'pending.waiting', 1)

    auction['awards'] = [pending_waiting_award, pending_verification_award]
    auction.update(auction)
    self.db.save(auction)
    self.migrate_data(self.app.app.registry)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    auction = response.json['data']
    self.assertEqual(auction['status'], u'active.qualification')
    self.assertEqual(auction['awards'][1]['status'], u'pending')
    self.assertEqual(auction['awards'][0]['status'], u'pending.waiting')


def migrate_pendingPayment_active(self):
    auction = self.db.get(self.auction_id)

    pending_payment_award = award_fixture(auction, 'pending.payment', 0)
    pending_waiting_award = award_fixture(auction, 'pending.waiting', 1)

    auction['awards'] = [pending_waiting_award, pending_payment_award]
    auction.update(auction)
    self.db.save(auction)
    self.migrate_data(self.app.app.registry)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    auction = response.json['data']
    self.assertEqual(auction['status'], u'active.awarded')
    self.assertEqual(auction['awards'][1]['status'], u'active')
    self.assertEqual(auction['awards'][0]['status'], u'pending.waiting')

    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contracts = response.json['data']
    self.assertEqual(len(contracts), 1)
    self.assertEqual(contracts[0]['status'], 'pending')
    signing_period_end_date = set_specific_hour(
        parse_datetime(pending_payment_award['signingPeriod']['endDate']),
        CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
    )
    pending_payment_award['signingPeriod']['endDate'] = signing_period_end_date.isoformat()
    self.assertEqual(contracts[0]['signingPeriod'], pending_payment_award['signingPeriod'])


def migrate_contract_cancelled(self):
    auction = self.db.get(self.auction_id)
    now = get_now()

    pending_verification_award = award_fixture(auction, 'pending.verification', 0)
    unsuccessful_award = award_fixture(auction, 'unsuccessful', 1)

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
    self.migrate_data(self.app.app.registry)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    auction = response.json['data']
    self.assertEqual(auction['status'], u'active.qualification')
    self.assertEqual(auction['awards'][1]['status'], u'pending')

    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contracts = response.json['data']
    self.assertEqual(len(contracts), 1)
    self.assertEqual(contracts[0]['status'], 'cancelled')
    signing_period_end_date = set_specific_hour(
        parse_datetime(unsuccessful_award['signingPeriod']['endDate']),
        CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
    )
    unsuccessful_award['signingPeriod']['endDate'] = signing_period_end_date.isoformat()
    self.assertEqual(contracts[0]['signingPeriod'], unsuccessful_award['signingPeriod'])


def migrate_contract_pending(self):
    self.set_status('active.awarded')
    auction = self.db.get(self.auction_id)
    now = get_now()

    active_award = award_fixture(auction, 'active', 0)
    pending_waiting_award = award_fixture(auction, 'pending.waiting', 1)

    auction['awards'] = [active_award, pending_waiting_award]

    auction['contracts'] = [{
        'awardID': active_award['id'],
        'suppliers': active_award['suppliers'],
        'value': active_award['value'],
        'date': now.isoformat(),
        'items': auction['items'],
        'contractID': '{}-11'.format(auction['auctionID']),
        'status': 'pending',
        'signingPeriod': active_award['signingPeriod'],
    }]

    auction.update(auction)
    self.db.save(auction)
    self.migrate_data(self.app.app.registry)

    response = self.app.get('/auctions/{}'.format(self.auction_id))
    auction = response.json['data']
    self.assertEqual(auction['status'], u'active.awarded')
    self.assertEqual(auction['awards'][0]['status'], u'active')
    self.assertEqual(auction['awards'][1]['status'], u'pending.waiting')

    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contracts = response.json['data']
    self.assertEqual(len(contracts), 1)
    self.assertEqual(contracts[0]['status'], 'pending')
    signing_period_end_date = set_specific_hour(
        parse_datetime(active_award['signingPeriod']['endDate']),
        CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
    )
    active_award['signingPeriod']['endDate'] = signing_period_end_date.isoformat()
    self.assertEqual(contracts[0]['signingPeriod'], active_award['signingPeriod'])
