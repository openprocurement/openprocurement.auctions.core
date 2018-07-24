# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.contracting.base.interfaces import (
    IContractManagerAdapter
)


def includeme(config):
    from .adapters import ContractManagerV1Adapter
    from .interfaces import IContractV1
    config.registry.registerAdapter(
        ContractManagerV1Adapter,
        (IContractV1,),
        IContractManagerAdapter
    )
    config.scan("openprocurement.auctions.core.plugins.contracting.v1.views")
