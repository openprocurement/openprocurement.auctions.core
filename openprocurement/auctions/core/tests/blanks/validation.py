# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.auctions.core.tests.helpers import (
    get_auction,
    get_item,
    patch_item,
)


def patch_item_during_rectification_period(test_case):
    auction_data = get_auction(test_case, test_case.auction_id).json['data']
    item_before_patch = auction_data['items'][0]
    target_value = 'rectification'
    patch_item(
        test_case,
        test_case.auction_id,
        item_before_patch['id'],
        test_case.auction_token,
        {'description': target_value}
    )
    item_after_patch = get_item(
        test_case,
        test_case.auction_id,
        item_before_patch['id']
    ).json['data']
    test_case.assertEqual(item_after_patch['description'], target_value)


def patch_item_after_rectification_period(test_case):
    auction_data = get_auction(test_case, test_case.auction_id).json['data']
    item_before_patch = auction_data['items'][0]
    # let's forge auction's rectificationPeriod
    auc_doc = test_case.db[test_case.auction_id]
    rectification_period = {
        'rectificationPeriod': {
            'startDate': (get_now() - timedelta(days=7)).isoformat(),
            'endDate': (get_now() - timedelta(days=5)).isoformat(),
        }
    }
    auc_doc.update(rectification_period)
    test_case.db[test_case.auction_id] = auc_doc
    # forge completed
    patch_item(
        test_case,
        test_case.auction_id,
        item_before_patch['id'],
        test_case.auction_token,
        {'description': 'ololol'},
        status=403
    )
    item_after_patch = get_item(
        test_case,
        test_case.auction_id,
        item_before_patch['id']
    ).json['data']
    test_case.assertEqual(item_after_patch['description'], item_before_patch['description'])
