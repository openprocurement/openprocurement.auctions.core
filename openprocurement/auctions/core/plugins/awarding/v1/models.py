from schematics.types import (
    StringType
)
from schematics.types.compound import ModelType

from openprocurement.api.models import (
    Organization,
    Document,
    ListType
)

from openprocurement.auctions.core.models import (
    flashComplaint as Complaint,
    flashItem as Item,
    Award as BaseAward
)


class Award(BaseAward):
    """
        Awarding Model for Awarding 1.0 procedure
    """
    status = StringType(required=True, choices=['pending', 'unsuccessful', 'active', 'cancelled'], default='pending')
    suppliers = ListType(ModelType(Organization), required=True, min_size=1, max_size=1)
    items = ListType(ModelType(Item))
    documents = ListType(ModelType(Document), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
