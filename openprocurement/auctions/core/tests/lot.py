# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.lot_blanks import (
    # AuctionLotResourceTest
    create_auction_lot_invalid,
    create_auction_lot,
    patch_auction_lot,
    patch_auction_vat,
    get_auction_lot,
    get_auction_lots,
    delete_auction_lot,
    auction_lot_guarantee,
    # AuctionLotProcessTest
    one_lot_0bid,
    one_lot_1bid,
    one_lot_2bid,
    two_lot_0bid,
    two_lot_2can,
    two_lot_2bid_0com_1can_before_auction,
    two_lot_1bid_0com_1can,
    two_lot_1bid_2com_1win,
    two_lot_1bid_0com_0win,
    two_lot_1bid_1com_1win,
    two_lot_2bid_2com_2win,
    two_lot_1feature_2bid_2com_2win
)


class AuctionLotResourceTestMixin(object):

    test_create_auction_lot_invalid = snitch(create_auction_lot_invalid)
    test_create_auction_lot = snitch(create_auction_lot)
    test_patch_auction_lot = snitch(patch_auction_lot)

    test_patch_auction_vat = snitch(patch_auction_vat)
    test_get_auction_lot = snitch(get_auction_lot)

    test_get_auction_lots = snitch(get_auction_lots)
    test_delete_auction_lot = snitch(delete_auction_lot)
    # test_auction_lot_guarantee = snitch(auction_lot_guarantee)


class AuctionLotProcessTestMixin(object):

    test_one_lot_0bid = snitch(one_lot_0bid)
    test_one_lot_1bid = snitch(one_lot_1bid)
    test_one_lot_2bid = snitch(one_lot_2bid)
    test_two_lot_0bid = snitch(two_lot_0bid)
    test_two_lot_2can = snitch(two_lot_2can)
    test_two_lot_2bid_0com_1can_before_auction = snitch(two_lot_2bid_0com_1can_before_auction)
    test_two_lot_1bid_0com_1can = snitch(two_lot_1bid_0com_1can)
    test_two_lot_1bid_2com_1win = snitch(two_lot_1bid_2com_1win)
    test_two_lot_1bid_0com_0win = snitch(two_lot_1bid_0com_0win)
    test_two_lot_1bid_1com_1win = snitch(two_lot_1bid_1com_1win)
    test_two_lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win)
    test_two_lot_1feature_2bid_2com_2win = snitch(two_lot_1feature_2bid_2com_2win)
