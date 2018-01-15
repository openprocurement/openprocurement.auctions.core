from uuid import uuid4

from schematics.types import (
    MD5Type,
    StringType
)
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError

from openprocurement.api.models import (
    Award as BaseAward,
    Value,
    Organization,
    IsoDateTimeType,
    Document,
    Period,
    ListType,
    Model
)
from openprocurement.api.utils import get_now
from openprocurement.auctions.core.models import (
    flashComplaint as Complaint,
    flashItem as Item
)


class Award(BaseAward):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    title = StringType()  # Award title
    title_en = StringType()
    title_ru = StringType()
    description = StringType()  # Award description
    description_en = StringType()
    description_ru = StringType()
    status = StringType(required=True, choices=['pending', 'unsuccessful', 'active', 'cancelled'], default='pending')
    date = IsoDateTimeType(default=get_now)
    value = ModelType(Value)
    suppliers = ListType(ModelType(Organization), required=True, min_size=1, max_size=1)
    items = ListType(ModelType(Item))
    documents = ListType(ModelType(Document), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    complaintPeriod = ModelType(Period)

    def validate_lotID(self, data, lotID):
        if isinstance(data['__parent__'], Model):
            if not lotID and data['__parent__'].lots:
                raise ValidationError(u'This field is required.')
            if lotID and lotID not in [i.id for i in data['__parent__'].lots]:
                raise ValidationError(u"lotID should be one of lots")

