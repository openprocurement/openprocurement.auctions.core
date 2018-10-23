# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute, Interface
)
from openprocurement.api.interfaces import (
    IAuction as BaseIAuction,
    IContentConfigurator    # noqa forwarded import
)

# Auction interfaces


class IAuction(BaseIAuction):
    """Interface for auctions"""


class IAuctionManager(Interface):
    name = Attribute('Auction name')


class IAuctionInitializator(Interface):
    """Interface for auctions initializators"""


class IAuctionChanger(Interface):
    """Interface for auctions changers"""


class IAuctionCreator(Interface):
    """Interface for auctions creators"""


class IAuctionChecker(Interface):
    """Interface for auctions checkers"""


class IAuctionItemer(Interface):
    """Interface for auctions items"""


class IAuctionCanceller(Interface):
    """Interface for auctions cancellations"""


class IAuctionLogger(Interface):
    """Interface for auction logger"""


class IAuctionDocumenter(Interface):
    """Interface for auctions documenters"""


class IAuctionQuestioner(Interface):
    """Interface for auctions questioners"""


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


class IBidDocumenter(Interface):
    """Interface for bids documenters"""


class IBidDocumentManager(Interface):
    """Interface for bid documents manager"""


class IBidDocumentChanger(Interface):
    """Interface for bid documents changer"""


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


class ICancellationDocumenter(Interface):
    """Interface for cancellations documenters"""


class ICancellationLogger(Interface):
    """Interface for items manager"""


class ICancellationRepresenter(Interface):
    """Interface for cancellations represent"""


class ICancellationChangerInitializator(Interface):
    """Interface for auction cancellation changer initializator"""

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
