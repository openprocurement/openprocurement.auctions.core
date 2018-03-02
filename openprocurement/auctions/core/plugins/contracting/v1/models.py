from schematics.types.compound import (
    ModelType,
)

from openprocurement.api.models import (
    ListType,
    Contract as BaseContract,
)
from openprocurement.auctions.core.models import (
    flashItem as Item,
    Document
)


class Contract(BaseContract):
    """
        Contract model for Contracting 1.0 procedure
    """

    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))
