from schematics.types.compound import ModelType
from zope.interface import implementer

from openprocurement.api.models.schematics_extender import (
    ListType,
)
from openprocurement.api.models.schema import (
    ContractAuctions as BaseContract,
)

from openprocurement.auctions.core.models import (
    dgfOrganization as Organization,
    dgfCDB2Item as Item,
    dgfDocument as Document,
    dgfComplaint as Complaint
)

from .interfaces import IContractV2_1


@implementer(IContractV2_1)
class Contract(BaseContract):
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list())
