# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.award_blanks import (
    # AuctionLotAwardResourceTest
    create_auction_award_lot,
    patch_auction_award_lot,
    patch_auction_award_unsuccessful_lot,
    # Auction2LotAwardResourceTest
    create_auction_award_2_lots,
    patch_auction_award_2_lots,
    not_found, create_auction_award_document,
    put_auction_award_document,
    patch_auction_award_document,
    # AuctionLotAwardComplaintResourceTest
    create_auction_award_complaint,
    patch_auction_award_complaint,
    get_auction_award_complaint,
    get_auction_award_complaints,
    # Auction2LotAwardComplaintResourceTest
    create_auction_award_complaint_2_lots,
    patch_auction_award_complaint_2_lots,
    # AuctionAwardComplaintDocumentResourceTest
    not_found_award_complaint_documen,
    create_auction_award_complaint_document,
    put_auction_award_complaint_document,
    patch_auction_award_complaint_document,
    create_auction_award_2_lot_complaint_document,
    put_auction_award_2_lot_complaint_document,
    patch_auction_award_2_lot_complaint_document,
    create_auction_2_lot_award_document,
    put_auction_2_lot_award_document,
    patch_auction_2_lot_award_document
)


class AuctionLotAwardResourceTestMixin(object):
    test_create_auction_award_lot = unittest.skip('option not available')(
        snitch(create_auction_award_lot)
    )
    test_patch_auction_award_lot = snitch(patch_auction_award_lot)
    test_patch_auction_award_unsuccessful_lot = snitch(patch_auction_award_unsuccessful_lot)


class Auction2LotAwardResourceTestMixin(object):
    test_create_auction_award_2_lots = snitch(create_auction_award_2_lots)
    test_patch_auction_award_2_lots = snitch(patch_auction_award_2_lots)


class AuctionAwardDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_auction_award_document = snitch(create_auction_award_document)
    test_put_auction_award_document = snitch(put_auction_award_document)
    test_patch_auction_award_document = snitch(patch_auction_award_document)


class AuctionLotAwardComplaintResourceTestMixin(object):
    test_create_auction_award_complaint = snitch(create_auction_award_complaint)
    test_patch_auction_award_complaint = snitch(patch_auction_award_complaint)
    test_get_auction_award_complaint = snitch(get_auction_award_complaint)
    test_get_auction_award_complaints = snitch(get_auction_award_complaints)


class Auction2LotAwardComplaintResourceTestMixin(object):
    test_create_auction_award_complaint_2_lots = snitch(create_auction_award_complaint_2_lots)
    test_patch_auction_award_complaint_2_lots = snitch(patch_auction_award_complaint_2_lots)


class AuctionAwardComplaintDocumentResourceTestMixin(object):
    test_not_found_award_complaint_documen = snitch(not_found_award_complaint_documen)
    test_create_auction_award_complaint_document = snitch(create_auction_award_complaint_document)
    test_put_auction_award_complaint_document = snitch(put_auction_award_complaint_document)
    test_patch_auction_award_complaint_document = snitch(patch_auction_award_complaint_document)


class Auction2LotAwardComplaintDocumentResourceTestMixin(object):
    test_create_auction_award_2_lot_complaint_document = snitch(create_auction_award_2_lot_complaint_document)
    test_put_auction_award_2_lot_complaint_document = snitch(put_auction_award_2_lot_complaint_document)
    test_patch_auction_award_2_lot_complaint_document = snitch(patch_auction_award_2_lot_complaint_document)


class Auction2LotAwardDocumentResourceTestMixin(object):
    test_create_auction_2_lot_award_document = snitch(create_auction_2_lot_award_document)
    test_put_auction_2_lot_award_document = snitch(put_auction_2_lot_award_document)
    test_patch_auction_2_lot_award_document = snitch(patch_auction_2_lot_award_document)


def suite():
    suite = unittest.TestSuite()
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
