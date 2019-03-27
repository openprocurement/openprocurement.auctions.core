# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.base.interfaces import (
    IAwardManagerAdapter,
)


def includeme(config):
    from .adapters import AwardManagerVXAdapter
    from .interfaces import IAwardVX
    config.registry.registerAdapter(
        AwardManagerVXAdapter,
        (IAwardVX, ),
        IAwardManagerAdapter
    )
