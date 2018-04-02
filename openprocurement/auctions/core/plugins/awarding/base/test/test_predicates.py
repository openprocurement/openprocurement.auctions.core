# -*- coding: utf-8 -*-
import unittest
import munch
from datetime import timedelta
from openprocurement.api.models import get_now
from openprocurement.auctions.core.plugins.awarding.base.predicates import (
    awarded_predicate,
    awarded_and_lots_predicate,
    contract_overdue_predicate,
    protocol_overdue_predicate,
)


class Test(unittest.TestCase):

    def test_awarded_predicate(self):
        blck_com_status = 'blck_com_status'
        auction_com_status = 'auction_com_status'
        award_com_status = 'award_com_status'

        auction_complaints = munch.Munch({'status': auction_com_status})
        award_complaints = munch.Munch({'status': award_com_status})

        award = munch.Munch({'status': award_com_status,
                             'complaints': [award_complaints]})
        auction = munch.Munch({'lots': None,
                               'status': 'active.awarded',
                               'block_complaint_status': blck_com_status,
                               'awards': [award],
                               'complaints': [auction_complaints]})

        result = awarded_predicate(auction)
        self.assertEqual(result, True)

        auction.block_complaint_status = auction_com_status
        result = awarded_predicate(auction)
        self.assertEqual(result, False)

        auction.block_complaint_status = award_com_status
        result = awarded_predicate(auction)
        self.assertEqual(result, False)

        auction.block_complaint_status = blck_com_status
        auction.status = 'not_active.awarded'
        result = awarded_predicate(auction)
        self.assertEqual(result, False)

    def test_awarded_and_lots_predicate(self):
        blck_com_status = 'blck_com_status'
        auction_statuses = ['active.qualification', 'active.awarded']
        auction_com_status = 'auction_com_status'
        auction_complaints = munch.Munch({'status': auction_com_status,
                                          'relatedLot': None})
        auction = munch.Munch({'lots': True,
                               'status': auction_statuses[0],
                               'block_complaint_status': blck_com_status,
                               'complaints': [auction_complaints]})

        result = awarded_and_lots_predicate(auction)
        self.assertEqual(result, True)

        auction.lots = None
        result = awarded_and_lots_predicate(auction)
        self.assertEqual(result, None)

        auction.lots = True
        auction.status = auction_statuses[1]
        result = awarded_and_lots_predicate(auction)
        self.assertEqual(result, True)

        auction.status = 'not_active'
        result = awarded_and_lots_predicate(auction)
        self.assertEqual(result, False)

        auction.status = auction_statuses[1]
        auction.block_complaint_status = auction_com_status
        result = awarded_and_lots_predicate(auction)
        self.assertEqual(result, False)

    def test_contract_overdue_predicate(self):
        need_status = 'need_status'
        end_data = get_now()
        item_end_data = get_now() - timedelta(days=1)
        item = munch.Munch({'status': need_status,
                           'signingPeriod': {'endDate': item_end_data}})

        result = contract_overdue_predicate(item, need_status, end_data)
        self.assertEqual(result, True)

        item.status = 'differ_status'
        result = contract_overdue_predicate(item, need_status, end_data)
        self.assertEqual(result, False)

        item.status = 'need_status'
        item.signingPeriod['endDate'] = end_data + timedelta(days=1)
        result = contract_overdue_predicate(item, need_status, end_data)
        self.assertEqual(result, False)

    def test_protocol_overdue_predicate(self):
        need_status = 'need_status'
        end_data = get_now()
        item_end_data = get_now() - timedelta(days=1)
        item = munch.Munch({'status': need_status,
                           'verificationPeriod': {'endDate': item_end_data}})

        result = protocol_overdue_predicate(item, need_status, end_data)
        self.assertEqual(result, True)

        item.status = 'differ_status'
        result = protocol_overdue_predicate(item, need_status, end_data)
        self.assertEqual(result, False)

        item.status = 'need_status'
        item.verificationPeriod['endDate'] = end_data + timedelta(days=1)
        result = protocol_overdue_predicate(item, need_status, end_data)
        self.assertEqual(result, False)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(Test))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
