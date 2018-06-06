# -*- coding: utf-8 -*-
from logging import getLogger

LOGGER = getLogger(__name__)


def includeme(config, plugin_map): #pylint: disable=unused-argument
    config.scan("openprocurement.auctions.core.plugins.transferring.views")
    LOGGER.info("Included auctions transferring plugin",
                extra={'MESSAGE_ID': 'included_plugin'})
