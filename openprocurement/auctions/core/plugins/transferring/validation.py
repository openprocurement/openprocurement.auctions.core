# -*- coding: utf-8 -*-
from openprocurement.api.plugins.transferring.validation import (
    validate_accreditation_level
)
from openprocurement.api.utils import (
   get_resource_accreditations
)


def validate_auction_accreditation_level(request, **kwargs): #pylint: disable=unused-argument
    levels = get_resource_accreditations(request, 'auction')['create']
    validate_accreditation_level(request, request.validated['auction'], levels)


def validate_bid_accreditation_level(request):
    levels = get_resource_accreditations(request, 'auction')['edit']
    validate_accreditation_level(request, request.validated['auction'], levels)


def validate_contract_accreditation_level(request):
    levels = get_resource_accreditations(request, 'auction')['create']
    validate_accreditation_level(request, request.validated['contract'], levels)


validate_complaint_accreditation_level = validate_bid_accreditation_level
