# -*- coding: utf-8 -*-
from openprocurement.auctions.core.endpoints import ENDPOINTS
from openprocurement.auctions.core.tests.helpers import (
    get_auction,
)
from openprocurement.auctions.core.tests.fixtures.items import dgf_item
from openprocurement.auctions.core.tests.helpers import (
    get_auction,
    post_item,
)


def post_single_item(test_case):
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
    item_id = post_item(
        test_case,
        test_case.auction_id,
        test_case.auction_token,
        dgf_item
    ).json['data']['id']
    item_resp = test_case.app.get(
        ENDPOINTS['item'].format(
            auction_id=test_case.auction_id,
            item_id=item_id
        )
    )
    data = item_resp.json['data']
    test_case.assertEqual(item_resp.status_code, 200)
    test_case.assertNotIn('auctionID', data.keys())
    test_case.assertIn('classification', data.keys())


def get_items_collection(test_case):
    item_id_1 = post_item(
        test_case,
        test_case.auction_id,
        test_case.auction_token,
        dgf_item
    ).json['data']['id']
    item_id_2 = post_item(
        test_case,
        test_case.auction_id,
        test_case.auction_token,
        dgf_item
    ).json['data']['id']
    coll_get_resp = test_case.app.get(
        ENDPOINTS['items'].format(auction_id=test_case.auction_id)
    )
    coll_ids = [item['id'] for item in coll_get_resp.json['data']]
    test_case.assertTrue(len(coll_ids) > 2)
    test_case.assertIn(item_id_1, coll_ids)
    test_case.assertIn(item_id_2, coll_ids)
