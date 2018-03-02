# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.tender_blanks import (
    # AuctionResourceTest
    empty_listing,
    listing,
    listing_changes,
    listing_draft,
    create_auction_draft,
    get_auction,
    auction_not_found,
    auction_Administrator_change,
    patch_auction,
    dateModified_auction,
    guarantee
)


class AuctionResourceTestMixin(object):
    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_auction_draft = snitch(create_auction_draft)
    test_get_auction = snitch(get_auction)
    test_auction_not_found = snitch(auction_not_found)
    test_auction_Administrator_change = snitch(auction_Administrator_change)


class DgfInsiderResourceTestMixin(object):
    test_patch_auction = snitch(patch_auction)
    test_dateModified_auction = snitch(dateModified_auction)
    test_guarantee = snitch(guarantee)
