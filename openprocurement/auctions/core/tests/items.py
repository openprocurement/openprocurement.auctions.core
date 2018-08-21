# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.core.tests.blanks.items_blanks import (
    get_item,
    get_items_collection,
    post_single_item,
)


class DgfItemsResourceTestMixin(object):
    test_post_single_item = snitch(post_single_item)
    test_get_item = snitch(get_item)
    test_get_items_collection = snitch(get_items_collection)
