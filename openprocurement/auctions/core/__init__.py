# -*- coding: utf-8 -*-
from pyramid.events import ContextFound
from pkg_resources import iter_entry_points
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.core.design import add_design
from openprocurement.auctions.core.utils import set_logging_context, extract_auction, register_auction_procurementMethodType, isAuction, auction_from_data
from openprocurement.auctions.core.adapters import AuctionConfigurator


def includeme(config):
    add_design()
    config.add_subscriber(set_logging_context, ContextFound)
    config.scan("openprocurement.auctions.core.views")

    # auction procurementMethodType plugins support
    puginns = config.registry.app_meta(['plugins'])
    config.add_route_predicate('auctionsprocurementMethodType', isAuction)
    config.registry.auction_procurementMethodTypes = {}
    config.add_request_method(extract_auction, 'auction', reify=True)
    config.add_request_method(auction_from_data)
    config.add_directive('add_auction_procurementMethodType', register_auction_procurementMethodType)
    config.registry.registerAdapter(AuctionConfigurator, (IAuction, IRequest),
                                    IContentConfigurator)

    plugins = config.registry.app_meta(['plugins'])
    for entry_point in iter_entry_points('openprocurement.auctions.core.plugins'):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
