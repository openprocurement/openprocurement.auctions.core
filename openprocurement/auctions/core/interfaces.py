# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute, Interface
)
from openprocurement.api.interfaces import (
    IAuction as BaseIAuction,
    IContentConfigurator    # noqa forwarded import
)


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


class IAuctioneer(Interface):
    """Interface for auctions auction"""


class IAuctionDocumenter(Interface):
    """Interface for auctions documenters"""


class IAuctionQuestioner(Interface):
    """Interface for auctions questioners"""


class IAuctionSubResourcesRepresenter(Interface):
    """Interface for auctions subresource representation"""


class IAuctionSubResourceItemRepresenter(Interface):
    """Interface for auctions subresource item representation"""


class IAuctionSubResourcesRepresentersFactory(Interface):
    """Interface for auctions subresource representer factory"""


class IQuestion(Interface):
    """Interface for questions"""


class IQuestionManager(Interface):
    """Interface for questions managers"""


class IQuestionChanger(Interface):
    """Interface for questions changers"""


class IBid(Interface):
    """Interface for bids"""


class IBidManager(Interface):
    """Interface for bids managers"""


class IBidChanger(Interface):
    """Interface for bid changers"""


class IBidDocumenter(Interface):
    """Interface for bids documenters"""


class IBidDeleter(Interface):
    """Interface for bids deleters"""


class IBidInitializator(Interface):
    """Interface for bid initializators"""


class IDocumentManager(Interface):
    """Interface for documents managers"""


class IDocumentChanger(Interface):
    """Interface for documents changer"""


class IItemManager(Interface):
    """Interface for items manager"""


class IItemChanger(Interface):
    """Interface for item changer"""


class IItemLogger(Interface):
    """Interface for item logger"""


class IItemRepresenter(Interface):
    """Interface for item represent"""
