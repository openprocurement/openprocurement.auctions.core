from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.cancellation_blanks import (
    # AuctionCancellationResourceTestMixin
    create_auction_cancellation_invalid,
    create_auction_cancellation,
    patch_auction_cancellation,
    get_auction_cancellation,
    get_auction_cancellations,
    # AuctionLotCancellationResourceTestMixin
    create_auction_cancellation_lot,
    patch_auction_cancellation_lot,
    # AuctionLotsCancellationResourceTestMixin
    create_auction_cancellation_2_lots,
    patch_auction_cancellation_2_lots,
    # AuctionCancellationDocumentResourceTestMixin
    not_found,
    create_auction_cancellation_document,
    put_auction_cancellation_document,
    patch_auction_cancellation_document
)


class AuctionCancellationResourceTestMixin(object):

    test_create_auction_cancellation_invalid = snitch(create_auction_cancellation_invalid)
    test_create_auction_cancellation = snitch(create_auction_cancellation)
    test_patch_auction_cancellation = snitch(patch_auction_cancellation)
    test_get_auction_cancellation = snitch(get_auction_cancellation)
    test_get_auction_cancellations = snitch(get_auction_cancellations)


class AuctionLotCancellationResourceTestMixin(object):
    test_create_auction_lot_cancellation = snitch(create_auction_cancellation_lot)
    test_patch_auction_lot_cancellation = snitch(patch_auction_cancellation_lot)


class AuctionLotsCancellationResourceTestMixin(object):
    test_create_auction_lots_cancellation = snitch(create_auction_cancellation_2_lots)
    test_patch_auction_lots_cancellation = snitch(patch_auction_cancellation_2_lots)


class AuctionCancellationDocumentResourceTestMixin(object):

    test_not_found = snitch(not_found)
    test_create_auction_cancellation_document = snitch(create_auction_cancellation_document)
    test_put_auction_cancellation_document = snitch(put_auction_cancellation_document)
    test_patch_auction_cancellation_document = snitch(patch_auction_cancellation_document)
