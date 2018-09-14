# -*- coding: utf-8 -*-
import unittest

from mock import Mock

from openprocurement.auctions.core.adapters import (
    AuctionManagerAdapter,
)


class AuctionManagerAdapterTest(unittest.TestCase):

    def setUp(self):
        self.auction = Mock()
        self.adapter = AuctionManagerAdapter(self.auction)
        self.adapter.allow_pre_terminal_statuses = True

    def test_terminalize_with_merchandising_object(self):
        self.auction.merchandisingObject = '1' * 32
        self.adapter.pendify_auction_status('complete')
        self.assertEqual(self.auction.status, 'pending.complete')

    def test_terminalize_without_merchandising_object(self):
        del self.auction.merchandisingObject
        self.adapter.pendify_auction_status('complete')
        self.assertEqual(self.auction.status, 'complete')
