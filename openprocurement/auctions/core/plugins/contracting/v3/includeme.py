# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.contracting.base.interfaces import (
    IContractManagerAdapter
)


def includeme(config):
    from .adapters import ContractManagerV3Adapter
    from .interfaces import IContractV3
    config.registry.registerAdapter(
        ContractManagerV3Adapter,
        (IContractV3,),
        IContractManagerAdapter
    )
