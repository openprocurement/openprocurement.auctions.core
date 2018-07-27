# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.contracting.base.interfaces import (
    IContractManagerAdapter
)


def includeme(config):
    from .adapters import ContractManagerV2Adapter
    from .interfaces import IContractV2
    config.registry.registerAdapter(
        ContractManagerV2Adapter,
        (IContractV2,),
        IContractManagerAdapter
    )
