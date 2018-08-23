# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.core.tests.blanks.validation import (
    patch_item_during_rectification_period,
    patch_item_after_rectification_period,
)

class RectificationPeriodValidationTestMixin(object):
    test_patch_item_during_rectification_period = snitch(patch_item_during_rectification_period)
    test_patch_item_after_rectification_period = snitch(patch_item_after_rectification_period)
