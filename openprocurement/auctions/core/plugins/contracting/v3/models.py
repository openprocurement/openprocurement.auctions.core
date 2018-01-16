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
    get_auction,
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)
from openprocurement.auctions.core.plugins.contracting.v1.models import (
    Contract as BaseContract
)
from openprocurement.auctions.core.plugins.awarding.v3.utils import (
    get_pending_award,
)


class Contract(BaseContract):
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
            'create': blacklist('signingPeriod'),
            'Administrator': whitelist('signingPeriod'),
        }

    @serializable(serialized_name="signingPeriod", serialize_when_none=False)
    def contract_signingPeriod(self):
        period = self.signingPeriod
        if not period:
            return None
        if not period.endDate:
            auction = get_auction(self)
            award = get_active_award(auction)
            period = award.signingPeriod
        return period.to_primitive()

    def validate_datePaid(self, data, value):
        target_signingPeriod = data.get('signingPeriod')
        if target_signingPeriod == None:
            return None
        if value < data.get('signingPeriod').get('startDate'):
            raise ValidationError(
                'datePaid must be less than start of signingPeriod'
            )

