# -*- coding: utf-8 -*-
from zope.interface import (
    Interface,
    Attribute
)
from openprocurement.api.interfaces import (
    IAuction as BaseIAuction,
    IContentConfigurator    # noqa forwarded import
)


# Auction interfaces


class IAuction(BaseIAuction):
    """Interface for auctions"""


# Question interfaces

class IQuestion(Interface):
    """Interface for questions"""


# Manager interfaces


class IManager(Interface):
    """Interface for managers"""

# Bid interfaces


class IBid(Interface):
    """Interface for bids"""


class IAuctionManager(Interface):
    name = Attribute('Auction name')
