# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.contracting.base.interfaces import (
    IContractManagerAdapter
)


def includeme(config):
    from .adapters import ContractManagerV2_1Adapter
    from .interfaces import IContractV2_1
    config.registry.registerAdapter(
        ContractManagerV2_1Adapter,
        (IContractV2_1,),
        IContractManagerAdapter
    )
