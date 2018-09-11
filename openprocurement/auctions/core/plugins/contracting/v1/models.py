# -*- coding: utf-8 -*-
from schematics.types.compound import (
    ModelType,
)
from zope.interface import implementer

from openprocurement.api.models.schematics_extender import (
    ListType,
)
from openprocurement.api.models.schema import (
    ContractAuctions,
)

from openprocurement.auctions.core.models import (
    flashItem as Item,
    dgfCDB2Document as Document
)
from .interfaces import IContractV1


@implementer(IContractV1)
class Contract(ContractAuctions):
    """
        Contract model for Contracting 1.0 procedure
    """

    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))
