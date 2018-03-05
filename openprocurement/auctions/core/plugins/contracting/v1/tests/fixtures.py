from openprocurement.auctions.core.endpoints import ENDPOINTS
from openprocurement.auctions.core.plugins.contracting.v1.models import Contract


def create_contract(test_case, auction_id, award_id, **kwargs):
    """Create Contract for given Award of Auction

        Kwargs will be appended to body of POST request data.
    """
    request_data = {
        'data': {'awardID': award_id}
    }
    request_data.update(kwargs)

    contract_response = test_case.app.post_json(
        ENDPOINTS['contracts'].format(
            auction_id=auction_id,
        ),
        request_data
    )

    contract = Contract(contract_response.json['data'])
    contract.validate()
    return contract
