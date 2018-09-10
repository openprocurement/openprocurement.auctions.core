# -*- coding: utf-8 -*-
from schematics.types.compound import ModelType
from zope.interface import implementer

from openprocurement.api.models.common import Period
from openprocurement.api.models.schematics_extender import (
    ListType,
)
from openprocurement.auctions.core.models import (
    dgfOrganization as Organization,
    LokiItem as Item,
    contractV3_1Document as Document,
    dgfComplaint as Complaint
)

from openprocurement.api.models.schema import (
    ContractAuctions as BaseContract
)
from .interfaces import IContractV3_1


@implementer(IContractV3_1)
class Contract(BaseContract):
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list())
    signingPeriod = ModelType(Period)
