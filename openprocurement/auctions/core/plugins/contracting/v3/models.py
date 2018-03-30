# -*- coding:utf-8 -*-
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.transforms import (
    blacklist,
    whitelist
)
from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType

from openprocurement.api.models.schematics_extender import (
    ListType,
    IsoDateTimeType,
    Model
)
from openprocurement.api.models.auction_models.models import get_now
from openprocurement.api.models.models import Period
from openprocurement.api.utils import calculate_business_date

from openprocurement.auctions.core.models import (
    dgfOrganization as Organization,
    dgfItem as Item,
    dgfDocument as BaseDocument,
    dgfComplaint as Complaint,
    Contract as BaseContract
)
from openprocurement.auctions.core.plugins.contracting.v3.constants import (
    PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD,
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)


class Document(BaseDocument):
    documentType = StringType(choices=['prolongationProtocol'], default='prolongationProtocol')


ProlongationDocument = Document


class Prolongation(Model):

    class Options:
        roles = {
            'create': blacklist('id', 'dateCreated', 'status',),
            'edit': blacklist('id', 'dateCreated',),
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    dateCreated = IsoDateTimeType(default=get_now(), required=True)
    decisionID = StringType(required=True)
    status = StringType(choices=['draft', 'applied'], default='draft')
    description = StringType(required=True, min_length=10)
    datePublished = IsoDateTimeType(required=True)
    documents = ListType(ModelType(ProlongationDocument), default=[], required=True)
    reason = StringType(
        choices=[
            'dgfPaymentImpossibility',
            'dgfLackOfDocuments',
            'dgfLegalObstacles',
            'other'
        ],
        required=True
    )

    def validate_datePublished(self, data, datePublished):
        """Check if datePublished attribute is valid

            datePublished must be non less than `dateCreated` on some
            limit.
        """
        if not data.get('datePublished'):
            return

        offset_from_date_created = calculate_business_date(
            datePublished,
            PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD
        )
        if offset_from_date_created < data['dateCreated']:
            raise ValidationError(
                'datePublished must be no less on {limit} days, '
                'than dateCreated'.format(
                    limit=PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD.days
                )
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
    prolongations = ListType(ModelType(Prolongation), default=list())
    documents = ListType(
        ModelType(BaseDocument),
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
        if (
            target_signingPeriod is None
            or value is None
        ):
            return None
        if value < target_signingPeriod.get('startDate'):
            raise ValidationError(
                'datePaid must be greater than start of signingPeriod'
            )
