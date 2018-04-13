# -*- coding: utf-8 -*-
import unittest
import uuid
import munch
from openprocurement.auctions.core.plugins.contracting.base.predicates import (
    not_active_lots_predicate
)


class Test(unittest.TestCase):

    def test_not_active_lots_predicate(self):
        lot_id = uuid.uuid4().hex
        award_id = uuid.uuid4().hex
        differ_award_id = uuid.uuid4().hex
        lot_id = uuid.uuid4().hex
        differ_lot_id = uuid.uuid4().hex
        lot_status = 'lot_status'

        award = munch.Munch({'id': award_id,
                             'lotID': lot_id})

        lot = munch.Munch({'id': lot_id,
                           'status': lot_status})
        contract = munch.Munch({'awardID': award_id})

        auction = munch.Munch({'awards': [award],
                               'lots': [lot]})

        request = munch.Munch({'validated': {'auction': auction,
                                             'contract': contract}})
        result = not_active_lots_predicate(request)
        self.assertTrue(result)

        lot.id = differ_lot_id
        result = not_active_lots_predicate(request)
        self.assertTrue(not result)

        lot.id = lot_id
        award.id = differ_award_id
        result = not_active_lots_predicate(request)
        self.assertTrue(not result)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(Test))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
