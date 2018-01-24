# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.complaint_blanks import (
    # AuctionComplaintResourceTest
    create_auction_complaint_invalid,
    create_auction_complaint,
    patch_auction_complaint,
    review_auction_complaint,
    get_auction_complaint,
    get_auction_complaints,
    # InsiderAuctionComplaintDocumentResourceTest
    not_found,
    create_auction_complaint_document,
    put_auction_complaint_document,
    patch_auction_complaint_document
)


class AuctionComplaintResourceTestMixin(object):
    test_create_auction_complaint_invalid = snitch(create_auction_complaint_invalid)
    test_create_auction_complaint = snitch(create_auction_complaint)
    test_patch_auction_complaint = snitch(patch_auction_complaint)
    test_review_auction_complaint = snitch(review_auction_complaint)
    test_get_auction_complaint = snitch(get_auction_complaint)
    test_get_auction_complaints = snitch(get_auction_complaints)


class InsiderAuctionComplaintDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_auction_complaint_document = snitch(create_auction_complaint_document)
    test_put_auction_complaint_document = snitch(put_auction_complaint_document)
    test_patch_auction_complaint_document = snitch(patch_auction_complaint_document)
