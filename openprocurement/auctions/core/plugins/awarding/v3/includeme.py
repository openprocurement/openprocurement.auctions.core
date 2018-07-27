# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.base.interfaces import (
    IAwardManagerAdapter,
)


def includeme(config):
    from .adapters import AwardManagerV3Adapter
    from .interfaces import IAwardV3
    config.registry.registerAdapter(
        AwardManagerV3Adapter,
        (IAwardV3, ),
        IAwardManagerAdapter
    )
