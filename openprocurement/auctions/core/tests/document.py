# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.document_blanks import (
    # AuctionDocumentResourceTest
    not_found,
    create_auction_document,
    put_auction_document,
    patch_auction_document,
    # AuctionDocumentWithDSResourceTest
    create_auction_document_json_invalid,
    create_auction_document_json,
    put_auction_document_json,
    create_auction_document_pas,
    put_auction_document_pas,
    create_auction_offline_document,
    put_auction_offline_document,
)


class AuctionDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_auction_document = snitch(create_auction_document)
    test_put_auction_document = snitch(put_auction_document)
    test_patch_auction_document = snitch(patch_auction_document)


class AuctionDocumentWithDSResourceTestMixin(object):
    test_create_auction_document_json_invalid = snitch(create_auction_document_json_invalid)
    test_create_auction_document_json = snitch(create_auction_document_json)
    test_put_auction_document_json = snitch(put_auction_document_json)
    test_create_auction_document_pas = snitch(create_auction_document_pas)
    test_put_auction_document_pas = snitch(put_auction_document_pas)
    test_create_auction_offline_document = snitch(create_auction_offline_document)
    test_put_auction_offline_document = snitch(put_auction_offline_document)
