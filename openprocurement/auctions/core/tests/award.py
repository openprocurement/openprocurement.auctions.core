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
    invalid_patch_auction_award,
    patch_auction_award,
    patch_auction_award_admin,
    complate_auction_with_second_award1,
    complate_auction_with_second_award2,
    complate_auction_with_second_award3,
    unsuccessful_auction1,
    unsuccessful_auction2,
    unsuccessful_auction3,
    unsuccessful_auction4,
    unsuccessful_auction5,
    get_auction_awards,
    successful_second_auction_award,
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
    test_create_auction_award_lot = snitch(create_auction_award_lot)
    test_patch_auction_award_lot = snitch(patch_auction_award_lot)
    test_patch_auction_award_unsuccessful_lot = snitch(patch_auction_award_unsuccessful_lot)


class Auction2LotAwardResourceTestMixin(object):
    test_create_auction_award_2_lots = snitch(create_auction_award_2_lots)
    test_patch_auction_award_2_lots = snitch(patch_auction_award_2_lots)


class AuctionAwardProcessTestMixin(object):
    test_invalid_patch_auction_award = snitch(invalid_patch_auction_award)
    test_patch_auction_award = snitch(patch_auction_award)
    test_patch_auction_award_admin = snitch(patch_auction_award_admin)
    test_complate_auction_with_second_award1 = snitch(complate_auction_with_second_award1)
    test_complate_auction_with_second_award2 = snitch(complate_auction_with_second_award2)
    test_complate_auction_with_second_award3 = snitch(complate_auction_with_second_award3)
    test_successful_second_auction_award = snitch(successful_second_auction_award)
    test_unsuccessful_auction1 = snitch(unsuccessful_auction1)
    test_unsuccessful_auction2 = snitch(unsuccessful_auction2)
    test_unsuccessful_auction3 = snitch(unsuccessful_auction3)
    test_unsuccessful_auction4 = snitch(unsuccessful_auction4)
    test_unsuccessful_auction5 = snitch(unsuccessful_auction5)
    test_get_auction_awards = snitch(get_auction_awards)


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
