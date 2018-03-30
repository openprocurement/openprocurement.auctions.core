from schematics.types.compound import (
    ModelType,
)

from openprocurement.api.models.auction_models.models import (
    ListType,
)

from openprocurement.auctions.core.models import (
    flashItem as Item,
    Contract as BaseContract,
    Document
)


class Contract(BaseContract):
    """
        Contract model for Contracting 1.0 procedure
    """

    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))
