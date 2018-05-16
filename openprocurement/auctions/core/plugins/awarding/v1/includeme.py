# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.base.interfaces import (
    IAwardManagerAdapter,
)


def includeme(config):
    from .adapters import AwardManagerV1Adapter
    from .interfaces import IAwardV1
    config.scan("openprocurement.auctions.core.plugins.awarding.v1.views")
    config.registry.registerAdapter(
        AwardManagerV1Adapter,
        (IAwardV1, ),
        IAwardManagerAdapter
    )
