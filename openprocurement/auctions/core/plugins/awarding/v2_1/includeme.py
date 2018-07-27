# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.base.interfaces import (
    IAwardManagerAdapter,
)


def includeme(config):
    from .adapters import AwardManagerV2_1Adapter
    from .interfaces import IAwardV2_1
    config.registry.registerAdapter(
        AwardManagerV2_1Adapter,
        (IAwardV2_1, ),
        IAwardManagerAdapter
    )
