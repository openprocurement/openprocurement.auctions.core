from openprocurement.auctions.core.tests.blanks.constants import (
    PATHS
)


def add_document_to_prolongation(
    test_case,
    auction_id,
    contract_id,
    prolongation_id,
):
    add_document_response = test_case.app.post(
<<<<<<< HEAD
        PATHS['prolongation_documents'].format(
=======
        PATHS['documents'].format(
>>>>>>> f3ed869... Add Prolongation views
            auction_id=auction_id,
            contract_id=contract_id,
            prolongation_id=prolongation_id
        ),
        upload_files=[(
            'file',
            'ProlongationDocument.doc',
            'content_with_prolongation_data'
        ),]
    )
    document_id = add_document_response.json['data']['id']
    key = add_document_response.json['data']['url'].split('?')[-1]
    return (document_id, key)
