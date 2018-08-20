# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.core.tests.blanks.items_blanks import (
    post_item,
)


class DgfItemsResourceTestMixin(object):
    test_post_item = snitch(post_item)
