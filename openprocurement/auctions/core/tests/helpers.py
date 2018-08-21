# -*- coding: utf-8 -*-
from openprocurement.auctions.core.endpoints import ENDPOINTS


def get_auction(test_case, auction_id):
    return test_case.app.get(
        ENDPOINTS['auction'].format(
            auction_id=auction_id
        )
    )


def post_item(test_case, auction_id, auction_token, item_data):
    return test_case.app.post_json(
        ENDPOINTS['items'].format(auction_id=auction_id) + '?acc_token={}'.format(auction_token),
        {'data': item_data}
    )


def patch_item(test_case, auction_id, item_id, auction_token, patch_data):
    return test_case.app.patch_json(
        ENDPOINTS['item'].format(
            auction_id=auction_id,
            item_id=item_id
        ) + '?acc_token={}'.format(auction_token),
        {'data': patch_data}
    )
