# -*- coding: utf-8 -*-
from openprocurement.auctions.core.endpoints import ENDPOINTS
from openprocurement.auctions.core.tests.helpers import (
    get_auction,
)
from openprocurement.auctions.core.tests.fixtures.items import dgf_item
from openprocurement.auctions.core.tests.helpers import (
    get_auction,
)


def post_item(test_case):
    auction_data_before_post = get_auction(test_case, test_case.auction_id)

    response = test_case.app.post_json(
        ENDPOINTS['items'].format(auction_id=test_case.auction_id) +
            '?acc_token={}'.format(test_case.auction_token),
        {'data': dgf_item}
    )
    test_case.assertEqual(response.status_code, 201)

    auction_data_after_post = get_auction(test_case, test_case.auction_id)

    items_before_post = len(auction_data_before_post.json['data']['items'])
    items_after_post = len(auction_data_after_post.json['data']['items'])
    # check that one item was added
    test_case.assertEqual(items_before_post + 1, items_after_post)


def get_item(test_case):
    pass
