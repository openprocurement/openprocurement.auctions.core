# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.core.tests.blanks.items_blanks import (
    get_item,
)


class DgfItemsResourceTestMixin(object):
    test_get_item = snitch(get_item)
