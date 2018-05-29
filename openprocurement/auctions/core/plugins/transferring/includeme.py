# -*- coding: utf-8 -*-

from logging import getLogger
from openprocurement.auctions.core.plugins.transferring.utils import (
    transfer_from_data,
    extract_transfer
)


LOGGER = getLogger(__name__)


def includeme(config, plugin_map): #pylint: disable=unused-argument
    LOGGER.info('Init relocation plugin.')
    config.add_request_method(extract_transfer, 'transfer', reify=True)
    config.add_request_method(transfer_from_data)
    config.scan("openprocurement.auctions.core.plugins.transferring.views")
