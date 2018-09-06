# -*- coding: utf-8 -*-
from openprocurement.api.validation import (
    validate_accreditation_level
)
from openprocurement.api.utils import (
   get_resource_accreditation
)


def validate_change_ownership_accreditation(request, **kwargs):    # pylint: disable=unused-argument
    levels = get_resource_accreditation(request, 'auction', request.context, 'create')
    err_msg = 'Broker Accreditation level does not permit ownership change'
    validate_accreditation_level(request, request.validated['auction'], levels, err_msg)
