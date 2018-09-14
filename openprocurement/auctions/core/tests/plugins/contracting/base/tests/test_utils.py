# -*- coding: utf-8 -*-
import unittest
import mock
import munch
import uuid
from openprocurement.auctions.core.plugins.contracting.base.utils import (
    check_auction_status
)
from openprocurement.auctions.core.adapters import AuctionManagerAdapter


BASE_UTILS_PATH = 'openprocurement.auctions.core.plugins.contracting.base.utils'


@mock.patch('{}.{}'.format(BASE_UTILS_PATH, 'LOGGER'))
@mock.patch('{}.{}'.format(BASE_UTILS_PATH, 'context_unpack'))
class Test(unittest.TestCase):

    def test_check_auction_status(self, context_unpack, mock_logger):
        auction_id = uuid.uuid4().hex
        contract_not_active_status = 'not_active'
        contract = munch.Munch({'status': contract_not_active_status})
        award = munch.Munch({'status': 'unsuccessful'})
        auction = munch.Munch({
            'awards': (award,),
            'contracts': (contract,),
            'status': None,
            'id': auction_id})
        adapter = AuctionManagerAdapter(auction)
        request = munch.munchify({
            'validated': {'auction': auction},
            'registry': {'getAdapter': mock.Mock(return_value=adapter)}
        })

        check_auction_status(request)
        self.assertEqual(auction.status, 'unsuccessful')

    def test_check_auction_status_complete(self, context_unpack, mock_logger):
        auction_id = uuid.uuid4().hex
        contract = munch.Munch({'status': 'active'})
        award = munch.Munch({'status': 'not_ended'})
        auction = munch.Munch({
            'awards': (award,),
            'contracts': (contract,),
            'status': None,
            'id': auction_id})
        adapter = AuctionManagerAdapter(auction)
        request = munch.munchify({
            'validated': {'auction': auction},
            'registry': {'getAdapter': mock.Mock(return_value=adapter)}
        })

        check_auction_status(request)
        self.assertEqual(auction.status, 'complete')


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(Test))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
