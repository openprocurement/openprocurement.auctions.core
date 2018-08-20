# -*- coding: utf-8 -*-
from openprocurement.auctions.core.endpoints import ENDPOINTS
from openprocurement.auctions.core.tests.helpers import (
    get_auction,
)
from openprocurement.auctions.core.tests.fixtures.items import dgf_item


def post_item(test_case):
    response = test_case.app.post_json(
        ENDPOINTS['items'].format(auction_id=test_case.auction_id),
        {'data': dgf_item}
    )
    test_case.assertEqual(response.status_code, 201)
