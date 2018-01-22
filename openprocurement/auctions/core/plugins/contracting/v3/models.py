# -*- coding:utf-8 -*-
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.models import Model
from schematics.exceptions import ValidationError
from schematics.transforms import (
    blacklist,
    whitelist
)

from openprocurement.api.models import (
    ListType,
    Period,
    IsoDateTimeType,
    get_now,
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


class Prolongation(Model):
    _crearedDate = IsoDateTimeType(default=get_now())
    decisionID = StringType(required=True)
    status = StringType(
        choices=[
            'draft',
            'applied',
            'deleted',
        ],
        default='draft'
    )
    reason = StringType(
        choices=[
            'dgfPaymentImpossibility',
            'dgfLackOfDocuments',
            'dgfLegalObstacles',
            'other'
        ]
    )
    description = StringType(
        required=True,
        min_length=10
    )
    dayPublished = IsoDateTimeType() # TODO: add validation
    documents = ModelType(Document) # TODO: add validation

    class Options:
        roles = {
            'view': blacklist('_created'),
        }

    def validate_dayPublished(self, value, data):
        time_limit = PROLONGATION['DAY_PUBLISHED_LIMIT']
        if value > self._created + time_limit:
            raise ValidationError(
                'dayPublished must be not later than {0} days after '
                'creation of prolongation'.format(time_limit.days)
            )
        pass


class Contract(BaseContract):
    """
        Contract for Contracting 3.0 procedure
    """
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    signingPeriod = ModelType(Period)
    datePaid = IsoDateTimeType()
    prolondation = ModelType(Prolongation)
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

