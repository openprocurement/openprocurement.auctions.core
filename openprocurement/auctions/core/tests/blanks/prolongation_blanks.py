from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Prolongation,
    Contract,
    ProlongationDocument,
)
from openprocurement.auctions.core.plugins.contracting.v3.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD,
)
from openprocurement.api.utils import calculate_business_date
from openprocurement.auctions.core.tests.blanks.constants import (
    PATHS
)
from openprocurement.auctions.core.tests.blanks.fixtures.prolongation import (
    add_document_to_prolongation
)


def get_prolongations_for_contract(test_case):
    get_prolongations_response = test_case.app.get(
        PATHS['prolongations'].format(
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
        PATHS['prolongation'].format(
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


def patch_prolongation_fields(test_case):
    patch_data = {
        'data': {
            'description': 'This Prolongation was updated!',
            'reason': 'dgfLackOfDocuments'
        }
    }
    patch_prolongation_response = test_case.app.patch_json(
        PATHS['prolongation'].format(
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
        retrieved_prolongation.description,
        patch_data['data']['description']
    )


def get_related_contract(test_case):
    """This is utility for testing, not a blank test
    """
    contract_response = test_case.app.get(
        PATHS['contract'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
        )
    )
    return Contract(contract_response.json['data'])


def apply_prolongation_short(test_case):
    pre_prolongation_contract = get_related_contract(test_case)
    add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation_id,
    )

    patch_data = {
        'data': {
            'status': 'applied',
        }
    }
    patch_prolongation_response = test_case.app.patch_json(
        PATHS['prolongation'].format(
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
    add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation_id,
    )
    add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation2_id,
    )

    patch_data = {
        'data': {
            'status': 'applied',
        }
    }
    # apply some short prolongation to be able apply long one
    short_prolongation_patch_response = test_case.app.patch_json(
        PATHS['prolongation'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        ),
        patch_data
    )

    patch_prolongation_response = test_case.app.patch_json(
        PATHS['prolongation'].format(
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


def apply_prolongation_triple_times(test_case):
    pre_prolongation_contract = get_related_contract(test_case)
    add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation_id,
    )
    add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation2_id,
    )
    add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation3_id,
    )

    patch_data = {
        'data': {
            'status': 'applied',
        }
    }
    # apply some short prolongation to be able apply long one
    short_prolongation_patch_response = test_case.app.patch_json(
        PATHS['prolongation'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        ),
        patch_data
    )

    valid_patch_prolongation_response = test_case.app.patch_json(
        PATHS['prolongation'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation2_id
        ),
        patch_data
    )

    third_patch_prolongation_response = test_case.app.patch_json(
        PATHS['prolongation'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation3_id
        ),
        patch_data,
        status=403
    )
    test_case.assertEqual(
        third_patch_prolongation_response.status,
        '403 Forbidden'
    )
    test_case.assertEqual(
        third_patch_prolongation_response.content_type,
        'application/json'
    )
    test_case.assertEqual(
        third_patch_prolongation_response.json['errors'][0]["description"],
        "Contract can be prolongated for 2 times only."
    )

    # check if contract signing was prolongated for the third time
    post_prolongation_contract = get_related_contract(test_case)
    test_case.assertEqual(
        post_prolongation_contract.signingPeriod.endDate,
        calculate_business_date(
            pre_prolongation_contract.signingPeriod.startDate,
            PROLONGATION_LONG_PERIOD
        )
    )


def upload_document(test_case):
    prolongation_response = test_case.app.get(
        PATHS['prolongation'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        )
    )
    prolongation_before_document_post = Prolongation(
        prolongation_response.json['data']
    )
    test_case.assertEqual(
        prolongation_before_document_post.documents,
        []
    )

    add_document_response = test_case.app.post(
        PATHS['documents'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        ),
        upload_files=[(
            'file',
            'ProlongationDocument.doc',
            'content_with_prolongation_data'
        ),]
    )
    test_case.assertEqual(
        add_document_response.status,
        '201 Created'
    )
    prolongation_response = test_case.app.get(
        PATHS['prolongation'].format(
            auction_id=test_case.auction_id,
            contract_id=test_case.contract_id,
            prolongation_id=test_case.prolongation_id
        )
    )
    prolongation_after_document_post = Prolongation(
        prolongation_response.json['data']
    )
    test_case.assertNotEqual(
        prolongation_after_document_post.documents,
        []
    )
    test_case.assertEqual(
        add_document_response.status,
        '201 Created'
    )

def get_document(test_case):
    document_id, document_key = add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation_id,
    )
    url = PATHS['document'].format(
        auction_id=test_case.auction_id,
        contract_id=test_case.contract_id,
        prolongation_id=test_case.prolongation_id,
        document_id=document_id,
        key=document_key
    )
    get_document_response = test_case.app.get(
        url
    )
    test_case.assertEqual(
        get_document_response.status,
        '200 OK'
    )
    test_case.assertEqual(
        get_document_response.status,
        '200 OK'
    )
    test_case.assertEqual(
        get_document_response.content_type,
        'application/msword'
    )

def get_list_of_documents(test_case):
    document_id, document_key = add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation_id,
    )
    document_id_2, document_key_2 = add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation_id,
    )
    list_of_docs_response = test_case.app.get(
        PATHS['documents'].format(
        auction_id=test_case.auction_id,
        contract_id=test_case.contract_id,
        prolongation_id=test_case.prolongation_id
        )
    )
    test_case.assertIsInstance(
        list_of_docs_response.json['data'],
        list
    )
    test_case.assertEqual(
        len(list_of_docs_response.json['data']),
        2
    )

def patch_document(test_case):
    document_id, document_key = add_document_to_prolongation(
        test_case,
        test_case.auction_id,
        test_case.contract_id,
        test_case.prolongation_id,
    )
    pre_patch_prolongation_response = test_case.app.get(
        PATHS['prolongation'].format(
        auction_id=test_case.auction_id,
        contract_id=test_case.contract_id,
        prolongation_id=test_case.prolongation_id
        )
    )
    pre_patch_doc_title = pre_patch_prolongation_response.json['data']['documents'][0]['title']
    patch_document_response = test_case.app.patch_json(
        PATHS['document'].format(
        auction_id=test_case.auction_id,
        contract_id=test_case.contract_id,
        prolongation_id=test_case.prolongation_id,
        document_id=document_id,
        key=document_key
        ),
        {'data':
            {'title': 'updated.doc'}
        }
    )
    test_case.assertEqual(
        patch_document_response.status,
        '200 OK'
    )
