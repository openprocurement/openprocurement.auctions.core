# -*- coding: utf-8 -*-
from openprocurement.auctions.core.endpoints import ENDPOINTS

def get_auction(test_case, auction_id):
    return test_case.app.get(
        ENDPOINTS['auction'].format(
            auction_id=auction_id
        )
    )
