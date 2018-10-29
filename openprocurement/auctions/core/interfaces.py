# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute, Interface
)
from openprocurement.api.interfaces import (
    IAuction as BaseIAuction,
    IContentConfigurator    # noqa forwarded import
)


class ICreator(Interface):
    """Interface for creator"""

# Auction interfaces


class IAuction(BaseIAuction):
    """Interface for auctions"""


class IAuctionManager(Interface):
    name = Attribute('Auction name')


class IAuctionInitializator(Interface):
    """Interface for auctions initializators"""


class IAuctionReportInitializator(Interface):
    """Interface for auctions initializators"""


class IAuctionChanger(Interface):
    """Interface for auctions changers"""


class IAuctionChecker(Interface):
    """Interface for auctions checkers"""


class IAuctionLogger(Interface):
    """Interface for auction logger"""

# auction creators


class IAuctionCreator(Interface):
    """Interface for auctions creators"""


class IAuctionCancellationCreator(Interface):
    """Interface for auction cancellation creator"""


class IAuctionQuestionCreator(Interface):
    """Interface for auction creator"""


class IAuctionDocumentCreator(Interface):
    """Interface for auction document creator"""


class IAuctionItemCreator(Interface):
    """Interface for auctions creator"""


class IAuctionSubResourcesRepresenter(Interface):
    """Interface for auctions subresource representation"""


class IAuctionSubResourceItemRepresenter(Interface):
    """Interface for auctions subresource item representation"""


class IAuctionSubResourceCancellationRepresenter(Interface):
    """Interface for auctions subresource cancellation representation"""


class IAuctionSubResourcesRepresentersFactory(Interface):
    """Interface for auctions subresource representer factory"""

# Auction Auction interfaces


class IAuctioneer(Interface):
    """Interface for auctions auction"""

# Question interfaces


class IQuestion(Interface):
    """Interface for questions"""


class IQuestionManager(Interface):
    """Interface for questions managers"""


class IQuestionChanger(Interface):
    """Interface for questions changers"""

# Bid interfaces


class IBid(Interface):
    """Interface for bids"""


class IBidManager(Interface):
    """Interface for bids managers"""


class IBidChanger(Interface):
    """Interface for bid changers"""


class IBidDocumentManager(Interface):
    """Interface for bid documents manager"""


class IBidDocumentChanger(Interface):
    """Interface for bid documents changer"""


class IBidDocumentCreator(Interface):
    """Interface for bid document creator"""


class IBidDeleter(Interface):
    """Interface for bids deleters"""


class IBidInitializator(Interface):
    """Interface for bid initializators"""

# Document interfaces


class IDocumentManager(Interface):
    """Interface for documents managers"""


class IDocumentChanger(Interface):
    """Interface for documents changer"""

# Cancellation interfaces


class ICancellationManager(Interface):
    """Interface for items manager"""


class ICancellationChanger(Interface):
    """Interface for items manager"""


class ICancellationDocumentCreator(Interface):
    """Interface for cancellations document creator"""


class ICancellationLogger(Interface):
    """Interface for items manager"""


class ICancellationRepresenter(Interface):
    """Interface for cancellations represent"""


class ICancellationChangerInitializator(Interface):
    """Interface for auction cancellation changer initializator"""


class ICancellationSubResourcesRepresenter(Interface):
    """
    Interface for cancellation subresource representer
    """


class ICancellationSubResourceDocumentRepresenter(Interface):
    """
    Interface for cancellation subresource document representer
    """


class ICancellationSubResourcesRepresentersFactory(Interface):
    """
    Interface for cancellation subresource representer factory
    """

# Item interfaces


class IItemManager(Interface):
    """Interface for items manager"""


class IItemChanger(Interface):
    """Interface for item changer"""


class IItemLogger(Interface):
    """Interface for item logger"""


class IItemRepresenter(Interface):
    """Interface for item represent"""


class INamedValidators(Interface):
    """Interface for named validators"""
