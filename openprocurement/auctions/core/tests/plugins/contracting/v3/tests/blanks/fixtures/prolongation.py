from openprocurement.auctions.core.plugins.contracting.v3.tests.constants import (
    PATHS
)


def add_document_to_prolongation(
    test_case,
    auction_id,
    contract_id,
    prolongation_id,
):
    add_document_response = test_case.app.post_json(
        PATHS['prolongation_documents'].format(
            auction_id=auction_id,
            contract_id=contract_id,
            prolongation_id=prolongation_id,
            token=test_case.auction_token
        ),
        {'data': {
            'title': u'Notice.pdf',
            'url': test_case.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/pdf',
            "documentType": "prolongationProtocol",
            "description": "some description"
        }}
    )
    document_id = add_document_response.json['data']['id']
    key = add_document_response.json['data']['url'].split('?')[-1]
    return (document_id, key)
