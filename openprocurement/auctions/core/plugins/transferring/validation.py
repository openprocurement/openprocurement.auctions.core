# -*- coding: utf-8 -*-
from openprocurement.api.plugins.transferring.validation import (
    validate_accreditation_level
)


def validate_auction_accreditation_level(request, **kwargs): #pylint: disable=unused-argument
    if hasattr(request.validated['auction'], 'transfer_accreditation'):
        predicate = 'transfer_accreditation'
    else:
        predicate = 'create_accreditation'
    validate_accreditation_level(request, request.validated['auction'], predicate)


def validate_bid_accreditation_level(request):
    validate_accreditation_level(request, request.validated['auction'], 'edit_accreditation')


def validate_contract_accreditation_level(request):
    validate_accreditation_level(request, request.validated['contract'], 'create_accreditation')


validate_complaint_accreditation_level = validate_bid_accreditation_level
