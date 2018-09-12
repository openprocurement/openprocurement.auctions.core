# -*- coding: utf-8 -*-
import unittest

from mock import Mock

from openprocurement.auctions.core.utils import (
    pendify_auction,
)


class PendifyAuctionTest(unittest.TestCase):

    def setUp(self):
        self.auction = Mock()
        self.auction.__class__ = Mock()
        self.auction.__class__.status.choices = (
            'pending.complete',
            'complete',
        )

    def test_terminalize_with_merchandising_object(self):
        pendify_auction(self.auction, 'complete')
        self.assertEqual(self.auction.status, 'pending.complete')

    def test_terminalize_without_merchandising_object(self):
        self.auction.__class__.status.choices = (
            'complete',
        )
        pendify_auction(self.auction, 'complete')
        self.assertEqual(self.auction.status, 'complete')
