# -*- coding: utf-8 -*-
from copy import deepcopy

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
    blacklist(
        '_attachments',
        'revisions',
        'bids',
        'numberOfBids') +
    auction_embedded_role)

draft_role = whitelist('status')
auction_post_role = whitelist('bids')
auction_patch_role = whitelist('auctionUrl', 'bids', 'lots')
auction_role = (
    blacklist(
        '_attachments',
        'revisions',
        'bids',
        'numberOfBids') +
    auction_embedded_role)

create_role = (
    blacklist(
        'owner',
        '_attachments',
        'revisions',
        'date',
        'dateModified',
        'doc_id',
        'auctionID',
        'bids',
        'documents',
        'awards',
        'questions',
        'complaints',
        'auctionUrl',
        'status',
        'auctionPeriod',
        'awardPeriod',
        'procurementMethod',
        'awardCriteria',
        'submissionMethod',
        'cancellations',
        'numberOfBidders',
        'contracts') +
    auction_embedded_role)

plain_role = (
    blacklist(
        '_attachments',
        'revisions',
        'dateModified') +
    schematics_embedded_role)

edit_role = (
    blacklist(
        'status',
        'procurementMethodType',
        'lots',
        'owner',
        '_attachments',
        'revisions',
        'date',
        'dateModified',
        'doc_id',
        'auctionID',
        'bids',
        'documents',
        'awards',
        'questions',
        'complaints',
        'auctionUrl',
        'auctionPeriod',
        'awardPeriod',
        'procurementMethod',
        'awardCriteria',
        'submissionMethod',
        'mode',
        'cancellations',
        'numberOfBidders',
        'contracts') +
    auction_embedded_role)

default_lot_role = (blacklist('numberOfBids') + schematics_default_role)
embedded_lot_role = (blacklist('numberOfBids') + schematics_embedded_role)
view_bid_role = (
    blacklist(
        'owner_token',
        'transfer_token') +
    schematics_default_role)
flash_bid_roles = {
    'embedded': view_bid_role,
    'view': view_bid_role,
    'auction_view': whitelist(
        'value',
        'lotValues',
        'id',
        'date',
        'parameters',
        'participationUrl',
        'owner'),
    'active.qualification': view_bid_role,
    'active.awarded': view_bid_role,
    'complete': view_bid_role,
    'unsuccessful': view_bid_role,
    'cancelled': view_bid_role,
}
Administrator_bid_role = whitelist('tenderers')
chronograph_role = whitelist('auctionPeriod', 'lots', 'next_check')
chronograph_view_role = whitelist(
    'status',
    'enquiryPeriod',
    'tenderPeriod',
    'auctionPeriod',
    'awardPeriod',
    'awards',
    'lots',
    'doc_id',
    'submissionMethodDetails',
    'mode',
    'numberOfBids',
    'complaints',
    'procurementMethodType')
Administrator_role = whitelist(
    'status',
    'mode',
    'procuringEntity',
    'auctionPeriod',
    'lots',
    'suspended')
view_role = (blacklist('_attachments', 'revisions') + auction_embedded_role)
listing_role = whitelist('dateModified', 'doc_id')
auction_view_role = whitelist(
    'auctionID',
    'dateModified',
    'bids',
    'auctionPeriod',
    'minimalStep',
    'auctionUrl',
    'features',
    'lots',
    'items',
    'procurementMethodType')
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


dgf_auction_roles = {
    'create': (
        auction_embedded_role +
        blacklist(
            'owner',
            '_attachments',
            'revisions',
            'date',
            'dateModified',
            'doc_id',
            'auctionID',
            'bids',
            'documents',
            'awards',
            'questions',
            'complaints',
            'auctionUrl',
            'status',
            'enquiryPeriod',
            'tenderPeriod',
            'awardPeriod',
            'procurementMethod',
            'eligibilityCriteria',
            'eligibilityCriteria_en',
            'eligibilityCriteria_ru',
            'awardCriteria',
            'submissionMethod',
            'cancellations',
            'numberOfBidders',
            'contracts',
            'suspended')),
    'edit_active.tendering': (
        edit_role +
        blacklist(
            'enquiryPeriod',
            'tenderPeriod',
            'value',
            'auction_value',
            'minimalStep',
            'auction_minimalStep',
            'guarantee',
            'auction_guarantee',
            'eligibilityCriteria',
            'eligibilityCriteria_en',
            'eligibilityCriteria_ru',
            'awardCriteriaDetails',
            'awardCriteriaDetails_en',
            'awardCriteriaDetails_ru',
            'procurementMethodRationale',
            'procurementMethodRationale_en',
            'procurementMethodRationale_ru',
            'submissionMethodDetails',
            'submissionMethodDetails_en',
            'submissionMethodDetails_ru',
            'items',
            'procuringEntity',
            'suspended',
            'auctionParameters')),
    'Administrator': (
        whitelist(
            'suspended',
            'awards',
            'auctionParameters') +
        Administrator_role),
    'pending.verification': enquiries_role,
    'invalid': view_role,
    'edit_pending.verification': whitelist(),
    'edit_invalid': whitelist(),
    'convoy': whitelist(
        'status',
        'items',
        'documents',
        'dgfID'),
    'auction_view': (
        auction_view_role +
        whitelist('auctionParameters')),
}

# Swiftsure auction
swiftsure_auction_roles = deepcopy(dgf_auction_roles)
swiftsure_auction_roles['edit_active.tendering'] = whitelist()

swiftsure_auction_roles['auction_view'] = (
    dgf_auction_roles['auction_view'] +
    whitelist('minNumberOfQualifiedBids', 'registrationFee', 'bankAccount')
)
swiftsure_auction_roles['pending.activation'] = enquiries_role
swiftsure_auction_roles['create'] = (
    auction_embedded_role +
    blacklist(
        'owner',
        '_attachments',
        'revisions',
        'date',
        'dateModified',
        'doc_id',
        'auctionID',
        'bids',
        'documents',
        'awards',
        'questions',
        'complaints',
        'auctionUrl',
        'enquiryPeriod',
        'tenderPeriod',
        'awardPeriod',
        'procurementMethod',
        'eligibilityCriteria',
        'eligibilityCriteria_en',
        'eligibilityCriteria_ru',
        'awardCriteria',
        'submissionMethod',
        'cancellations',
        'numberOfBidders',
        'contracts',
        'suspended'))

# Tessel auction
tessel_auction_roles = deepcopy(dgf_auction_roles)
tessel_auction_roles['create'] = (
    auction_embedded_role +
    blacklist(
        'owner',
        '_attachments',
        'revisions',
        'date',
        'dateModified',
        'doc_id',
        'auctionID',
        'bids',
        'awards',
        'questions',
        'complaints',
        'auctionUrl',
        'enquiryPeriod',
        'tenderPeriod',
        'awardPeriod',
        'procurementMethod',
        'eligibilityCriteria',
        'eligibilityCriteria_en',
        'eligibilityCriteria_ru',
        'awardCriteria',
        'submissionMethod',
        'cancellations',
        'numberOfBidders',
        'contracts',
        'suspended'))
tessel_auction_roles['edit_active.tendering'] = whitelist()
tessel_auction_roles['auction_view'] = (
    dgf_auction_roles['auction_view'] +
    whitelist('minNumberOfQualifiedBids', 'registrationFee', 'bankAccount')
)
tessel_auction_roles['pending.activation'] = enquiries_role
tessel_auction_roles['convoy'] = whitelist('status', 'items', 'documents')
