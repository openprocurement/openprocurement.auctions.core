# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.contracting.base.interfaces import (
    IContractManagerAdapter
)


def includeme(config):
    from .adapters import ContractManagerV3_1Adapter
    from .interfaces import IContractV3_1
    config.registry.registerAdapter(
        ContractManagerV3_1Adapter,
        (IContractV3_1,),
        IContractManagerAdapter
    )
    config.scan("openprocurement.auctions.core.plugins.contracting.v3_1.views")
