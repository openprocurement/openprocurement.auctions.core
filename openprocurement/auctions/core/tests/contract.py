# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.contract_blanks import (
    # AuctionContractResourceTest
    create_auction_contract_invalid,
    create_auction_contract,
    create_auction_contract_in_complete_status,
    get_auction_contract,
    get_auction_contracts,
    # AuctionContractDocumentResourceTest
    not_found,
    create_auction_contract_document,
    put_auction_contract_document,
    patch_auction_contract_document,
    # Auction2LotContractDocumentResourceTest
    create_auction_2_lot_contract_document,
    put_auction_2_lot_contract_document,
    patch_auction_2_lot_contract_document
)


class AuctionContractResourceTestMixin(object):
    test_create_auction_contract_invalid = snitch(create_auction_contract_invalid)
    test_create_auction_contract = snitch(create_auction_contract)
    test_create_auction_contract_in_complete_status = snitch(create_auction_contract_in_complete_status)
    test_get_auction_contract = snitch(get_auction_contract)
    test_get_auction_contracts = snitch(get_auction_contracts)


class AuctionContractDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_auction_contract_document = snitch(create_auction_contract_document)
    test_put_auction_contract_document = snitch(put_auction_contract_document)
    test_patch_auction_contract_document = snitch(patch_auction_contract_document)


class Auction2LotContractDocumentResourceTestMixin(object):
    test_create_auction_2_lot_contract_document = snitch(create_auction_2_lot_contract_document)
    test_put_auction_2_lot_contract_document = snitch(put_auction_2_lot_contract_document)
    test_patch_auction_2_lot_contract_document = snitch(patch_auction_2_lot_contract_document)
