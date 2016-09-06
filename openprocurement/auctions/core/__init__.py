# -*- coding: utf-8 -*-
from pyramid.events import ContextFound
from pkg_resources import iter_entry_points
from openprocurement.auctions.core.design import add_design
from openprocurement.auctions.core.utils import set_logging_context, extract_auction


def includeme(config):
    add_design()
    config.add_subscriber(set_logging_context, ContextFound)
    config.add_request_method(extract_auction, 'auction', reify=True)
    config.scan("openprocurement.auctions.core.views")

    plugins = config.registry.settings.get('plugins') and config.registry.settings['plugins'].split(',')
    for entry_point in iter_entry_points('openprocurement.auctions.core.plugins'):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
