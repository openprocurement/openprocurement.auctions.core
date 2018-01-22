from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Prolongation,
    Contract,
)
from openprocurement.auctions.core.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD,
)
from openprocurement.api.utils import calculate_business_date


PATHS = {  # resource paths
    'collection': '/auctions/{auction_id}/contracts/'
    '{contract_id}/prolongation',
    'exact': '/auctions/{auction_id}/contracts/'
    '{contract_id}/prolongation/{prolongation_id}',
    'contract': '/auctions/{auction_id}/contracts/{contract_id}',
}


def get_prolongations_for_contract(test_case):
    get_prolongations_response = test_case.app.get(
        PATHS['collection'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id
        )
    )
    test_case.assertEqual(
        get_prolongations_response.status,
        '200 OK'
    )
    test_case.assertIsInstance(
        get_prolongations_response.json['data'],
        list
    )


def get_prolongation_by_id(test_case):
    get_prolongation_response = test_case.app.get(
        PATHS['exact'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        )
    )
    test_case.assertEqual(
        get_prolongation_response.status,
        '200 OK'
    )
    # check data
    retrieved_prolongation = Prolongation(
        get_prolongation_response.json['data']
    )
    retrieved_prolongation.validate()
    test_case.assertEqual(
        retrieved_prolongation.id,
        test_case.prolongation_id
    )


def delete_prolongation_by_id(test_case):
    patch_data = {
        'data': {
            'status': 'deleted',
        }
    }
    delete_prolongation_response = test_case.app.patch_json(
        PATHS['exact'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        ),
        patch_data
    )
    test_case.assertEqual(
        delete_prolongation_response.status,
        '200 OK'
    )
    retrieved_prolongation = Prolongation(
        delete_prolongation_response.json['data']
    )
    retrieved_prolongation.validate()
    test_case.assertEqual(
        retrieved_prolongation.status,
        'deleted'
    )


def patch_prolongation_fields(test_case):
    patch_data = {
        'data': {
            'description': 'This Prolongation was updated!',
            'reason': 'dgfLackOfDocuments'
        }
    }
    delete_prolongation_response = test_case.app.patch_json(
        PATHS['exact'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        ),
        patch_data
    )
    test_case.assertEqual(
        delete_prolongation_response.status,
        '200 OK'
    )
    retrieved_prolongation = Prolongation(
        delete_prolongation_response.json['data']
    )
    retrieved_prolongation.validate()
    test_case.assertEqual(
        retrieved_prolongation.description,
        patch_data['data']['description']
    )


def get_related_contract(test_case):
    """This is utility for testing, not a blank test"""
    contract_response = test_case.app.get(
        PATHS['contract'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
        )
    )
    return Contract(contract_response.json['data'])


def apply_prolongation_short(test_case):
    pre_prolongation_contract = get_related_contract(test_case)

    patch_data = {
        'data': {
            'status': 'applied',
        }
    }
    patch_prolongation_response = test_case.app.patch_json(
        PATHS['exact'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        ),
        patch_data
    )

    test_case.assertEqual(
        patch_prolongation_response.status,
        '200 OK'
    )
    retrieved_prolongation = Prolongation(
        patch_prolongation_response.json['data']
    )
    retrieved_prolongation.validate()
    test_case.assertEqual(
        retrieved_prolongation.status,
        'applied'
    )
    post_prolongation_contract = get_related_contract(test_case)
    test_case.assertEqual(
        post_prolongation_contract.signingPeriod.endDate,
        calculate_business_date(
            pre_prolongation_contract.signingPeriod.startDate,
            PROLONGATION_SHORT_PERIOD
        )
    )


def apply_prolongation_long(test_case):
    pre_prolongation_contract = get_related_contract(test_case)

    patch_data = {
        'data': {
            'status': 'applied',
        }
    }
    # apply some short prolongation to be able apply long one
    short_prolongation_patch_response = test_case.app.patch_json(
        PATHS['exact'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        ),
        patch_data
    )

    patch_prolongation_response = test_case.app.patch_json(
        PATHS['exact'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation2_id
        ),
        patch_data
    )

    test_case.assertEqual(
        patch_prolongation_response.status,
        '200 OK'
    )
    retrieved_prolongation = Prolongation(
        patch_prolongation_response.json['data']
    )
    retrieved_prolongation.validate()
    test_case.assertEqual(
        retrieved_prolongation.status,
        'applied'
    )
    post_prolongation_contract = get_related_contract(test_case)
    test_case.assertEqual(
        post_prolongation_contract.signingPeriod.endDate,
        calculate_business_date(
            pre_prolongation_contract.signingPeriod.startDate,
            PROLONGATION_LONG_PERIOD
        )
    )
