# -*- coding: utf-8 -*-
from schematics.transforms import (
    blacklist,
    whitelist
)
from openprocurement.api.models.auction_models import (
    schematics_default_role,
    schematics_embedded_role,
)
from openprocurement.api.models.common import (
    sensitive_embedded_role,
)

view_complaint_role = (blacklist('owner_token', 'owner') + schematics_default_role)

auction_embedded_role = sensitive_embedded_role

enquiries_role = (
    auction_embedded_role +
    blacklist(
        '_attachments',
        'bids',
        'numberOfBids',
        'revisions',
    )
)

draft_role = whitelist('status')

auction_post_role = whitelist('bids')

auction_patch_role = whitelist('auctionUrl', 'bids', 'lots')

auction_role = (
    auction_embedded_role +
    blacklist(
        '_attachments',
        'bids',
        'numberOfBids',
        'revisions',
    )
)

create_role = (
    auction_embedded_role +
    blacklist(
        '_attachments',
        'auctionID',
        'auctionPeriod',
        'auctionUrl',
        'awardCriteria',
        'awardPeriod',
        'awards',
        'bids',
        'cancellations',
        'complaints',
        'contracts',
        'date',
        'dateModified',
        'doc_id',
        'documents',
        'numberOfBidders',
        'owner',
        'procurementMethod',
        'questions',
        'revisions',
        'status',
        'submissionMethod',
    )
)

plain_role = (
    schematics_embedded_role +
    blacklist(
        '_attachments',
        'dateModified',
        'revisions',
    )
)

edit_role = (
    auction_embedded_role +
    blacklist(
        '_attachments',
        'auctionID',
        'auctionPeriod',
        'auctionUrl',
        'awardCriteria',
        'awardPeriod',
        'awards',
        'bids',
        'cancellations',
        'complaints',
        'contracts',
        'date',
        'dateModified',
        'doc_id',
        'documents',
        'lots',
        'mode',
        'numberOfBidders',
        'owner',
        'procurementMethod',
        'procurementMethodType',
        'questions',
        'revisions',
        'status',
        'submissionMethod',
    )
)

default_lot_role = (blacklist('numberOfBids') + schematics_default_role)

embedded_lot_role = (blacklist('numberOfBids') + schematics_embedded_role)

view_bid_role = (
    schematics_default_role +
    blacklist(
        'owner_token',
        'transfer_token',
    )
)

flash_bid_roles = {
    'embedded': view_bid_role,
    'view': view_bid_role,
    'auction_view': whitelist(
        'date',
        'id',
        'lotValues',
        'owner',
        'parameters',
        'participationUrl',
        'value',
    ),
    'active.qualification': view_bid_role,
    'active.awarded': view_bid_role,
    'complete': view_bid_role,
    'unsuccessful': view_bid_role,
    'cancelled': view_bid_role,
}

Administrator_bid_role = whitelist('tenderers')

chronograph_role = whitelist('auctionPeriod', 'lots', 'next_check')

chronograph_view_role = whitelist(
    'auctionPeriod',
    'awardPeriod',
    'awards',
    'complaints',
    'doc_id',
    'enquiryPeriod',
    'lots',
    'mode',
    'numberOfBids',
    'procurementMethodType',
    'status',
    'submissionMethodDetails',
    'tenderPeriod',
)

Administrator_role = whitelist(
    'auctionPeriod',
    'lots',
    'mode',
    'procuringEntity',
    'status',
    'suspended',
)

view_role = (blacklist('_attachments', 'revisions') + auction_embedded_role)

listing_role = whitelist('dateModified', 'doc_id')

auction_view_role = whitelist(
    'auctionID',
    'auctionPeriod',
    'auctionUrl',
    'bids',
    'dateModified',
    'features',
    'items',
    'lots',
    'minimalStep',
    'procurementMethodType',
)
auction_roles = {
    'plain': plain_role,
    'create': create_role,
    'edit': edit_role,
    'edit_draft': draft_role,
    'edit_active.enquiries': edit_role,
    'edit_active.tendering': whitelist(),
    'edit_active.auction': whitelist(),
    'edit_active.qualification': whitelist(),
    'edit_active.awarded': whitelist(),
    'edit_complete': whitelist(),
    'edit_unsuccessful': whitelist(),
    'edit_cancelled': whitelist(),
    'view': view_role,
    'listing': listing_role,
    'auction_view': auction_view_role,
    'auction_post': auction_post_role,
    'auction_patch': auction_patch_role,
    'draft': enquiries_role,
    'active.enquiries': enquiries_role,
    'active.tendering': enquiries_role,
    'active.auction': auction_role,
    'active.qualification': view_role,
    'active.awarded': view_role,
    'complete': view_role,
    'unsuccessful': view_role,
    'cancelled': view_role,
    'chronograph': chronograph_role,
    'chronograph_view': chronograph_view_role,
    'Administrator': Administrator_role,
    'default': schematics_default_role,
    'contracting': whitelist('doc_id', 'owner'),
    'extract_credentials': whitelist('owner', 'id')
}

dgf_blacklist_if_not_in_rectificationPeriod = blacklist(
    'description',
    'description_en',
    'description_ru',
    'dgfDecisionDate',
    'dgfDecisionID',
    'dgfID',
    'guarantee',
    'items',
    'minimalStep',
    'tenderAttepmts',
    'title',
    'title_en',
    'title_ru',
)


dgf_auction_roles = {
    'create': (
        auction_embedded_role +
        blacklist(
            '_attachments',
            'auctionID',
            'auctionUrl',
            'awardCriteria',
            'awardPeriod',
            'awards',
            'bids',
            'cancellations',
            'complaints',
            'contracts',
            'date',
            'dateModified',
            'doc_id',
            'documents',
            'eligibilityCriteria',
            'eligibilityCriteria_en',
            'eligibilityCriteria_ru',
            'enquiryPeriod',
            'numberOfBidders',
            'owner',
            'procurementMethod',
            'questions',
            'rectificationPeriod',
            'revisions',
            'status',
            'submissionMethod',
            'suspended',
            'tenderPeriod',
        )
    ),
    'edit_active.tendering_during_rectificationPeriod': (
        edit_role +
        blacklist(
            'auctionParameters',
            'auction_guarantee',
            'auction_minimalStep',
            'auction_value',
            'awardCriteriaDetails',
            'awardCriteriaDetails_en',
            'awardCriteriaDetails_ru',
            'eligibilityCriteria',
            'eligibilityCriteria_en',
            'eligibilityCriteria_ru',
            'enquiryPeriod',
            # COMMENTS BELOW ARE FOR CLARITY: PRELASE, DON'T DELETE THEM
            # 'guarantee',  allowed to edit during rectificationPeriod
            # 'items',  allowed to edit during rectificationPeriod
            # 'minimalStep',  allowed to edit during rectificationPeriod
            'merchandisingObject',
            'procurementMethodRationale',
            'procurementMethodRationale_en',
            'procurementMethodRationale_ru',
            'procuringEntity',
            'rectificationPeriod',
            'submissionMethodDetails',
            'submissionMethodDetails_en',
            'submissionMethodDetails_ru',
            'suspended',
            'tenderPeriod',
            'value',
        )
    ),
    'edit_active.tendering_after_rectificationPeriod': (
        edit_role +
        dgf_blacklist_if_not_in_rectificationPeriod +
        blacklist(
            'auctionParameters',
            'auction_guarantee',
            'auction_minimalStep',
            'auction_value',
            'awardCriteriaDetails',
            'awardCriteriaDetails_en',
            'awardCriteriaDetails_ru',
            'eligibilityCriteria',
            'eligibilityCriteria_en',
            'eligibilityCriteria_ru',
            'enquiryPeriod',
            'guarantee',
            'items',
            'minimalStep',
            'procurementMethodRationale',
            'procurementMethodRationale_en',
            'procurementMethodRationale_ru',
            'procuringEntity',
            'rectificationPeriod',
            'submissionMethodDetails',
            'submissionMethodDetails_en',
            'submissionMethodDetails_ru',
            'suspended',
            'tenderPeriod',
            'value',
        )
     ),
    'Administrator': (
        Administrator_role +
        whitelist(
            'auctionParameters',
            'awards',
            'suspended',
            'rectificationPeriod',
        )
    ),
    'pending.verification': (
        enquiries_role +
        blacklist('rectificationPeriod')
    ),
    'invalid': view_role,
    'edit_pending.verification': whitelist(),
    'edit_invalid': whitelist(),
    'convoy': whitelist(
        'dgfID',
        'documents',
        'items',
        'status',
    ),
    'auction_view': (auction_view_role + whitelist('auctionParameters')),
}

# Swiftsure auction
swiftsure_auction_roles = {
    'create': (
        auction_embedded_role +
        blacklist(
            '_attachments',
            'auctionID',
            'auctionUrl',
            'awardCriteria',
            'awardPeriod',
            'awards',
            'bids',
            'cancellations',
            'complaints',
            'contracts',
            'date',
            'dateModified',
            'doc_id',
            'documents',
            'eligibilityCriteria',
            'eligibilityCriteria_en',
            'eligibilityCriteria_ru',
            'enquiryPeriod',
            'numberOfBidders',
            'owner',
            'procurementMethod',
            'questions',
            'revisions',
            'submissionMethod',
            'suspended',
            'tenderPeriod',
        )
    ),
    'edit_active.tendering': whitelist(),
    'Administrator': (
        Administrator_role +
        whitelist(
            'auctionParameters',
            'awards',
            'suspended',
        )
    ),
    'pending.verification': enquiries_role,
    'pending.activation': enquiries_role,
    'invalid': view_role,
    'edit_pending.verification': whitelist(),
    'edit_invalid': whitelist(),
    'convoy': whitelist(
        'dgfID',
        'documents',
        'items',
        'status',
    ),
    'auction_view': (
        auction_view_role +
        whitelist(
            'auctionParameters'
            'bankAccount',
            'minNumberOfQualifiedBids',
            'registrationFee',
        )
    ),
}

# Tessel auction
tessel_auction_roles = {
    'create': (
        auction_embedded_role +
        blacklist(
            '_attachments',
            'auctionID',
            'auctionUrl',
            'awardCriteria',
            'awardPeriod',
            'awards',
            'bids',
            'cancellations',
            'complaints',
            'contracts',
            'date',
            'dateModified',
            'doc_id',
            'eligibilityCriteria',
            'eligibilityCriteria_en',
            'eligibilityCriteria_ru',
            'enquiryPeriod',
            'numberOfBidders',
            'owner',
            'procurementMethod',
            'questions',
            'revisions',
            'submissionMethod',
            'suspended',
            'tenderPeriod',
        )
    ),
    'edit_active.tendering': whitelist(),
    'Administrator': (
        Administrator_role +
        whitelist(
            'auctionParameters',
            'awards',
            'suspended',
        )
    ),
    'pending.verification': enquiries_role,
    'invalid': view_role,
    'edit_pending.verification': whitelist(),
    'edit_invalid': whitelist(),
    'convoy': whitelist(
        'documents',
        'items',
        'status',
    ),
    'auction_view': (
        auction_view_role +
        whitelist(
            'auctionParameters',
            'bankAccount',
            'minNumberOfQualifiedBids',
            'registrationFee',
        )
    ),
    'pending.activation': enquiries_role,
}

dgf_item_roles = {
    'create': blacklist(
        'deliveryAddress',
        'deliveryDate',
        'deliveryLocation',
    ),
    'edit_active.tendering': blacklist(
        'deliveryAddress',
        'deliveryDate',
        'deliveryLocation',
    ),
    'view': whitelist(
        'additionalClassifications',
        'address',
        'classification',
        'deliveryAddress',
        'deliveryDate',
        'deliveryLocation',
        'description',
        'description_en',
        'description_ru',
        'id',
        'location',
        'quantity',
        'relatedLot',
        'schema_properties',
        'unit',
    ),
    'edit': blacklist(
        'id',
    ),
}
