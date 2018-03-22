from openprocurement.auctions.core.endpoints import ENDPOINTS


def get_auction(test_case):
    """Fixture for querying of the auction
    """
    response = test_case.app.get(
        ENDPOINTS['auction'].format(
            auction_id=test_case.auction_id,
        )
    )
    return response.json['data']
