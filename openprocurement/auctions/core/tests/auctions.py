# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import BaseWebTest, snitch
from openprocurement.auctions.core.tests.blanks.tender_blanks import empty_listing
from openprocurement.auctions.core.tests.blanks.auction_blanks import (
    # AuctionAuctionResourceTest
    get_auction_auction_not_found,
    get_auction_auction,
    patch_auction_auction,
    post_auction_auction_document,
    # AuctionLotAuctionResourceTest
    get_auction_auction_lot,
    patch_auction_auction_lot,
    post_auction_auction_document_lot,
    # AuctionMultipleLotAuctionResourceTest
    get_auction_auction_2_lots,
    patch_auction_auction_2_lots,
    post_auction_auction_document_2_lots,
)


class AuctionResourceTest(BaseWebTest):

    test_empty_listing = snitch(empty_listing)


class AuctionAuctionResourceTestMixin(object):
    test_get_auction_auction_not_found = snitch(get_auction_auction_not_found)

    test_get_auction_auction = snitch(get_auction_auction)
    test_patch_auction_auction = snitch(patch_auction_auction)
    test_post_auction_auction_document = snitch(post_auction_auction_document)


class AuctionLotAuctionResourceTestMixin(object):
    test_get_auction_auction_not_found = snitch(get_auction_auction_not_found)

    test_get_auction_auction_lots = snitch(get_auction_auction_lot)
    test_patch_auction_auction_lots = snitch(patch_auction_auction_lot)
    test_post_auction_auction_document_lots = snitch(post_auction_auction_document_lot)


class AuctionMultipleLotAuctionResourceTestMixin(object):
    test_post_auction_auction_document = snitch(get_auction_auction_not_found)
    test_get_auction_auction_multiple_lot = snitch(get_auction_auction_2_lots)
    test_patch_auction_auction_multiple_lot = snitch(patch_auction_auction_2_lots)
    test_post_auction_auction_document_multiple_lot = snitch(post_auction_auction_document_2_lots)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(AuctionResourceTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
