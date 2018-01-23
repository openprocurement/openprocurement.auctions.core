# -*- coding:utf-8 -*-
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from schematics.transforms import (
    blacklist,
    whitelist
)

from openprocurement.api.models import (
    ListType,
    Period,
    IsoDateTimeType,
)
from openprocurement.auctions.core.models import (
    dgfOrganization as Organization,
    dgfItem as Item,
    dgfDocument as Document,
    dgfComplaint as Complaint,
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)
from openprocurement.api.models import (
    Contract as BaseContract
)


class Contract(BaseContract):
    """
        Contract for Contracting 3.0 procedure
    """
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    signingPeriod = ModelType(Period)
    datePaid = IsoDateTimeType()
    documents = ListType(
        ModelType(Document),
        default=list(),
        validators=[validate_disallow_dgfPlatformLegalDetails]
    )
    class Options:
        roles = {
            'edit': blacklist('signingPeriod'),
            'create': blacklist('signingPeriod', 'datePaid'),
            'Administrator': whitelist('signingPeriod', 'datePaid'),
        }

    def validate_datePaid(self, data, value):
        target_signingPeriod = data.get('signingPeriod')
        if target_signingPeriod == None or \
            value == None:
            return None
        if value > data.get('signingPeriod').get('startDate'):
            raise ValidationError(
                'datePaid must not greater than start of signingPeriod'
            )

