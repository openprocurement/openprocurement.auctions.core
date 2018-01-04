from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.bidder_blanks import (
    # AuctionBidderDocumentResourceTestMixin
    not_found,
    create_auction_bidder_document,
    put_auction_bidder_document,
    patch_auction_bidder_document,
    # AuctionBidderDocumentWithDSResourceTest
    create_auction_bidder_document_json,
    put_auction_bidder_document_json
)


class AuctionBidderDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_auction_bidder_document = snitch(create_auction_bidder_document)
    test_put_auction_bidder_document = snitch(put_auction_bidder_document)
    test_patch_auction_bidder_document = snitch(patch_auction_bidder_document)

class AuctionBidderDocumentWithDSResourceTestMixin(object):
    test_create_auction_bidder_document_json = snitch(create_auction_bidder_document_json)
    test_put_auction_bidder_document_json = snitch(put_auction_bidder_document_json)