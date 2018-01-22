PATHS = {  # resource paths
<<<<<<< HEAD
    'prolongations': '/auctions/{auction_id}/contracts/{contract_id}/prolongations',
    'prolongation': '/auctions/{auction_id}/contracts/{contract_id}/prolongations/{prolongation_id}',
    'contract': '/auctions/{auction_id}/contracts/{contract_id}',
    'prolongation_documents': '/auctions/{auction_id}/contracts/{contract_id}/prolongations/{prolongation_id}/documents',
    'prolongation_document': '/auctions/{auction_id}/contracts/{contract_id}/prolongations/{prolongation_id}/documents/{document_id}?{key}',
=======
    'prolongations': '/auctions/{auction_id}/contracts/'
    '{contract_id}/prolongations',
    'prolongation': '/auctions/{auction_id}/contracts/'
    '{contract_id}/prolongations/{prolongation_id}',
    'contract': '/auctions/{auction_id}/contracts/{contract_id}',
    'documents': '/auctions/{auction_id}/contracts/'
    '{contract_id}/prolongations/{prolongation_id}/documents',
    'document': '/auctions/{auction_id}/contracts/'
    '{contract_id}/prolongations/{prolongation_id}'
    '/documents/{document_id}?{key}',
>>>>>>> f3ed869... Add Prolongation views
}
