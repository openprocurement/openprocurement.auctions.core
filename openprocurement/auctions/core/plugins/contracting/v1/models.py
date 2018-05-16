from schematics.types.compound import (
    ModelType,
)

from openprocurement.api.models.schematics_extender import (
    ListType,
)

from openprocurement.auctions.core.models import (
    flashItem as Item,
    Contract as BaseContract,
    dgfCDB2Document as Document
)


class Contract(BaseContract):
    """
        Contract model for Contracting 1.0 procedure
    """

    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))
