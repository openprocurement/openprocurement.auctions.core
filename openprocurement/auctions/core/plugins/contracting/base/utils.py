# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution

from openprocurement.api.utils import (
    log_auction_status_change
)
from openprocurement.auctions.core.interfaces import IAuctionManager

# Obtain pure distribution name
PKG = get_distribution('.'.join(__package__.split('.')[:3]))
LOGGER = getLogger(PKG.project_name)


def check_auction_status(request):
    """Update auction status taking as basis it's awards and contracts

        If auction has not successful awards - mark it as `unsuccessful`,
        else if it has active contract - mark it as complete.
    """
    auction = request.validated['auction']
    adapter = request.registry.getAdapter(auction, IAuctionManager)
    if auction.awards:
        awards_statuses = set([award.status for award in auction.awards])
    else:
        awards_statuses = set([""])
    if not awards_statuses.difference(set(['unsuccessful', 'cancelled'])):
        adapter.pendify_auction_status('unsuccessful')
        log_auction_status_change(request, auction, auction.status)
    if auction.contracts and auction.contracts[-1].status == 'active':
        adapter.pendify_auction_status('complete')
        log_auction_status_change(request, auction, auction.status)


def check_document_existence(contract, document_type):
    if contract.documents:
        for document in contract.documents:
            if document['documentType'] == document_type:
                return True
    return False
