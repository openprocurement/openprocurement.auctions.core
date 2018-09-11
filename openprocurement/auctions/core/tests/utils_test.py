# -*- coding: utf-8 -*-
import unittest

from mock import Mock

from openprocurement.auctions.core.utils import (
    pendify_auction,
)


class PendifyAuctionTest(unittest.TestCase):

    def setUp(self):
        self.auction = Mock()

    def test_terminalize_with_merchandising_object(self):
        self.auction.merchandisingObject = '1' * 32
        pendify_auction(self.auction, 'complete')
        self.assertEqual(self.auction.status, 'pending.complete')

    def test_terminalize_without_merchandising_object(self):
        del self.auction.merchandisingObject
        pendify_auction(self.auction, 'complete')
        self.assertEqual(self.auction.status, 'complete')
