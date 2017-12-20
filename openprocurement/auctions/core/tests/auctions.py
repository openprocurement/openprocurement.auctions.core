# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import BaseWebTest, snitch
from .blanks.tender_blanks import empty_listing


class AuctionResourceTest(BaseWebTest):

    test_empty_listing = snitch(empty_listing)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
