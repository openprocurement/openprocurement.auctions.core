from logging import getLogger
from pkg_resources import get_distribution

from openprocurement.api.utils import (
    context_unpack,
)
# Obtain pure distribution name
PKG = get_distribution('.'.join(__package__.split('.')[:3]))
LOGGER = getLogger(PKG.project_name)


def check_auction_status(request):
    """Update auction status taking as basis it's awards and contracts

        If auction has not successful awards - mark it as `unsuccessful`,
        else if it has active contract - mark it as complete.
    """
    auction = request.validated['auction']
    if auction.awards:
        awards_statuses = set([award.status for award in auction.awards])
    else:
        awards_statuses = set([""])
    if not awards_statuses.difference(set(['unsuccessful', 'cancelled'])):
        LOGGER.info(
            'Switched auction {} to {}'.format(auction.id, 'unsuccessful'),
            extra=context_unpack(
                request,
                {'MESSAGE_ID': 'switched_auction_unsuccessful'})
        )
        auction.status = 'unsuccessful'
    if auction.contracts and auction.contracts[-1].status == 'active':
        LOGGER.info(
            'Switched auction {} to {}'.format(auction.id, 'complete'),
            extra=context_unpack(
                request,
                {'MESSAGE_ID': 'switched_auction_complete'}
            )
        )
        auction.status = 'complete'
