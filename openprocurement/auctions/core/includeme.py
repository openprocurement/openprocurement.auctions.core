# -*- coding: utf-8 -*-
import logging

from pyramid.events import ContextFound
from pyramid.interfaces import IRequest

from openprocurement.api.interfaces import (
    IContentConfigurator,
    IAwardingNextCheck
)
from openprocurement.api.utils import (
    get_content_configurator,
    get_plugin_aliases
)

from openprocurement.auctions.core.adapters import (
    AuctionConfigurator,
    AuctionAwardingNextCheckAdapter,
    AuctionManagerAdapter
)
from openprocurement.auctions.core.design import add_design
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.core.interfaces import IAuctionManager
from openprocurement.auctions.core.utils import (
    set_logging_context,
    extract_auction,
    register_auction_procurementMethodType,
    isAuction,
    auction_from_data,
    init_plugins,
    awardingTypePredicate,
    SubscribersPicker
)
from openprocurement.api.app import get_evenly_plugins

LOGGER = logging.getLogger(__name__)


def includeme(config, plugin_map):
    add_design()
    config.add_subscriber(set_logging_context, ContextFound)

    # auction procurementMethodType plugins support
    config.registry.auction_procurementMethodTypes = {}
    config.registry.pmtConfigurator = {}
    config.add_route_predicate('auctionsprocurementMethodType', isAuction)
    config.add_route_predicate('awardingType', awardingTypePredicate)
    config.add_subscriber_predicate('auctionsprocurementMethodType', SubscribersPicker)
    config.add_request_method(extract_auction, 'auction', reify=True)
    config.add_request_method(auction_from_data)
    config.add_directive(
        'add_auction_procurementMethodType',
        register_auction_procurementMethodType
    )
    config.scan("openprocurement.auctions.core.views")
    config.scan("openprocurement.api.subscribers")
    config.scan("openprocurement.auctions.core.subscribers")
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
    LOGGER.info("Included openprocurement.auctions.core plugin",
                extra={'MESSAGE_ID': 'included_plugin'})

    # Aliases information
    LOGGER.info('Start aliases')
    get_plugin_aliases(plugin_map)
    LOGGER.info('End aliases')

    get_evenly_plugins(config, plugin_map['plugins'], 'openprocurement.auctions.core.plugins')
