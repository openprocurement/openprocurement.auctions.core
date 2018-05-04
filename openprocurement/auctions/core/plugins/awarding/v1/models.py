from zope.interface import implementer
from schematics.types import (
    StringType
)
from schematics.types.compound import ModelType

from openprocurement.api.models.auction_models import (
    Organization,
    Document
)
from openprocurement.api.models.schematics_extender import ListType

from openprocurement.auctions.core.models import (
    flashComplaint as Complaint,
    flashItem as Item,
    Award as BaseAward
)
from .interfaces import IAwardV1


@implementer(IAwardV1)
class Award(BaseAward):
    """
        Awarding Model for Awarding 1.0 procedure
    """
    status = StringType(required=True, choices=['pending', 'unsuccessful', 'active', 'cancelled'], default='pending')
    suppliers = ListType(ModelType(Organization), required=True, min_size=1, max_size=1)
    items = ListType(ModelType(Item))
    documents = ListType(ModelType(Document), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
