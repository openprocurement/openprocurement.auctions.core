from schematics.types.compound import ModelType

from openprocurement.api.models.auction_models import (
    ListType,
)

from openprocurement.auctions.core.models import (
    Contract as BaseContract,
    dgfOrganization as Organization,
    dgfItem as Item,
    dgfDocument as Document,
    dgfComplaint as Complaint
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)


class Contract(BaseContract):
    """
        Contract model for Contracting 2.0 procedure
    """
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(
        ModelType(Document),
        default=list(),
        validators=[validate_disallow_dgfPlatformLegalDetails]
    )

