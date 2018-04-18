# -*- coding: utf-8 -*-
import unittest
import mock
import munch
import uuid
from openprocurement.auctions.core.plugins.contracting.base.utils import (
    check_auction_status
)


BASE_UTILS_PATH = 'openprocurement.auctions.core.plugins.contracting.base.utils'


class Test(unittest.TestCase):

    @mock.patch('{}.{}'.format(BASE_UTILS_PATH, 'LOGGER'))
    @mock.patch('{}.{}'.format(BASE_UTILS_PATH, 'context_unpack'))
    def test_check_auction_status(self, context_unpack, mock_logger):
        auction_id = uuid.uuid4().hex
        contract_not_active_status = 'not_active'
        end_award_statuses = ('unsuccessful', 'cancelled')
        contract = munch.Munch({'status': contract_not_active_status})
        award = munch.Munch({'status': end_award_statuses[0]})
        auction = munch.Munch({'awards': (award,),
                               'contracts': (contract,),
                               'status': None,
                               'id': auction_id})
        request = munch.Munch({'validated': {'auction': auction}})

        check_auction_status(request)
        self.assertEqual(auction.status, 'unsuccessful')

        auction.status = None
        award.status = 'not_ended'
        contract.status = 'active'
        check_auction_status(request)
        self.assertEqual(auction.status, 'complete')


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(Test))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
