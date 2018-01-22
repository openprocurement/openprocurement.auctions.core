# -*- coding:utf-8 -*-
from uuid import uuid4

from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from schematics.transforms import (
    blacklist,
    whitelist
)

from openprocurement.api.models import (
    ListType,
    Period,
    IsoDateTimeType,
    Model,
    get_now,
)
from openprocurement.api.models import (
    Contract as BaseContract
)
from openprocurement.api.utils import calculate_business_date
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)
from openprocurement.auctions.core.models import (
    dgfOrganization as Organization,
    dgfItem as Item,
    dgfDocument as BaseDocument,
    dgfComplaint as Complaint,
)
from openprocurement.auctions.core.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD,
    PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD,
)


class Document(BaseDocument):
    documentType = StringType(
        choices=['prolongationProtocol'],
        default='prolongationProtocol'
    )


ProlongationDocument = Document


class Prolongation(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    dateCreated = IsoDateTimeType(default=get_now(), required=True)
    decisionID = StringType(required=True)
    status = StringType(
        choices=[
            'draft',
            'applied',
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
    datePublished = IsoDateTimeType()
    documents = ListType(ModelType(ProlongationDocument), default=[])

    class Options:
        roles = {
            'create': blacklist('id', 'dateCreated', 'datePublished',),
            'edit': blacklist('id', 'dateCreated', 'datePublished',),
        }

    def _apply_short(self):
        self.status = 'applied'
        contract = self.__parent__
        contract.signingPeriod.endDate = calculate_business_date(
            contract.signingPeriod.startDate,
            PROLONGATION_SHORT_PERIOD
        )

    def _apply_long(self, previous_prolongation):
        self.status = 'applied'
        previous_prolongation.status = 'draft'
        contract = self.__parent__
        contract.signingPeriod.endDate = calculate_business_date(
            contract.signingPeriod.startDate,
            PROLONGATION_LONG_PERIOD
        )

    def apply(self):
        """Choose order of prolongation and apply right"""
        is_second_appliance = False
        previous_prolongation = None

        for prolongation in self.__parent__.prolongations:
            if prolongation.status == 'applied':
                is_second_appliance = True
                previous_prolongation = prolongation
                break

        if is_second_appliance:
            self._apply_long(previous_prolongation)
        else:
            self._apply_short()

    def add_document(self, document):
        if self.status == 'draft':
            self.documents.append(document)
        else:
            raise ValidationError(
                'Document can be added only in `draft` status.'
            )

    def validate_datePublished(self, data, value):
        """Check if datePublished attribute is valid

            datePublished must be non less than `dateCreated` on some
            limit.
        """
        if not data.get('datePublished'):
            return
        if value + PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD <\
                data['dateCreated']:
            raise ValidationError(
                'datePublished must be no less on {limit} days, '
                'than dateCreated'.format(
                    limit=PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD
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
        if target_signingPeriod is None or \
                value is None:
            return None
        if value > data.get('signingPeriod').get('startDate'):
            raise ValidationError(
                'datePaid must not greater than start of signingPeriod'
            )
