from schematics.types.compound import ModelType

from openprocurement.api.models.schematics_extender import (
    ListType,
)
from openprocurement.auctions.core.models import (
    dgfOrganization as Organization,
    dgfCDB2Item as Item,
    dgfDocument as Document,
    dgfComplaint as Complaint
)

from openprocurement.auctions.core.models import (
    Contract as BaseContract
)


class Contract(BaseContract):
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list())
