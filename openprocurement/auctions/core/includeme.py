# -*- coding: utf-8 -*-
from pkg_resources import iter_entry_points
from pyramid.events import ContextFound
from pyramid.interfaces import IRequest

from openprocurement.api.interfaces import (
    IContentConfigurator,
    IAwardingNextCheck
)
from openprocurement.api.utils import get_content_configurator

from openprocurement.auctions.core.adapters import (
    AuctionConfigurator,
    AuctionAwardingNextCheckAdapter
)
from openprocurement.auctions.core.design import add_design
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.core.utils import (
    set_logging_context,
    extract_auction,
    register_auction_procurementMethodType,
    isAuction,
    auction_from_data,
    init_plugins,
    awardingTypePredicate
)


def includeme(config):
    add_design()
    config.add_subscriber(set_logging_context, ContextFound)

    # auction procurementMethodType plugins support
    config.registry.auction_procurementMethodTypes = {}
    config.add_route_predicate('auctionsprocurementMethodType', isAuction)
    config.add_route_predicate('awardingType', awardingTypePredicate)
    config.add_request_method(extract_auction, 'auction', reify=True)
    config.add_request_method(auction_from_data)
    config.add_directive(
        'add_auction_procurementMethodType',
        register_auction_procurementMethodType
    )
    config.scan("openprocurement.auctions.core.views")
    config.scan("openprocurement.api.subscribers")
    init_plugins(config)

    # register Adapters
    config.registry.registerAdapter(
        AuctionConfigurator,
        (IAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AuctionAwardingNextCheckAdapter,
        (IAuction, ),
        IAwardingNextCheck
    )

    config.add_request_method(get_content_configurator, 'content_configurator', reify=True)

    settings = config.registry.settings
    config.registry.pmtConfigurator = {key.split('.')[1]: settings.get(key) for key in settings.keys() if
                                       key.startswith('pmt')}

    plugins = (config.registry.settings.get('plugins') and
              config.registry.settings['plugins'].split(','))
    for entry_point in iter_entry_points('openprocurement.auctions.core.plugins'):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
