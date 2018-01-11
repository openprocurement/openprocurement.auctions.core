from uuid import uuid4
from schematics.types import (
    StringType,
    MD5Type
)
from schematics.types.compound import (
    ModelType,
)

from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Value,
    Organization,
    Period,
    Contract as BaseContract,
)
from openprocurement.auctions.core.models import (
    flashItem as Item,
    Document
)


class Contract(BaseContract):

    documents = ListType(ModelType(Document), default=list())
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    awardID = StringType(required=True)
    contractID = StringType()
    contractNumber = StringType()
    title = StringType()  # Contract title
    title_en = StringType()
    title_ru = StringType()
    description = StringType()  # Contract description
    description_en = StringType()
    description_ru = StringType()
    status = StringType(
        choices=['pending', 'terminated', 'active', 'cancelled'],
        default='pending'
    )
    period = ModelType(Period)
    value = ModelType(Value)
    dateSigned = IsoDateTimeType()
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    date = IsoDateTimeType()

