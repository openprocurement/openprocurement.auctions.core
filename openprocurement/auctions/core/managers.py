# -*- coding: utf-8 -*-
from zope.interface import implementer

from openprocurement.auctions.core.utils import (
    save_auction
)

from openprocurement.auctions.core.interfaces import (
    IAuctionManager,
    IBidManager,
    IBidDocumentManager,
    ICancellationManager,
    IDocumentManager,
    IItemManager,
    IQuestionManager
)


@implementer(IAuctionManager)
class AuctionManager(object):
    name = 'Auction Manager'
    context = None

    def __init__(self, request, context):
        self._request = request
        self.context = context

    def initialize(self, status):
        initializator = self.Initializator(self._request, self.context)
        initializator.initialize(status)

    def change(self):
        changer = self.Changer(self._request, self.context)
        return changer.change()

    def award(self):
        auctioner = self.Auctioneer(self._request, self.context)
        if auctioner.award():
            awarding = self.Awarding(self.context, self._request)
            awarding.start_awarding()

    def cancel(self):
        canceller = self.Canceller(self._request, self.context)
        cancellation = canceller.cancel()
        return cancellation

    def check(self):
        checker = self.Checker(self._request, self.context)
        checker.check()
        if self.context.status == 'active.qualification':
            awarding = self.Awarding(self.context, self._request)
            awarding.start_awarding()

    def update_auction_urls(self):
        auctioner = self.Auctioneer(self._request, self.context)
        return auctioner.update_auction_urls()

    def auction_report(self):
        auctioner = self.Auctioneer(self._request, self.context)
        if auctioner.report():
            auctioner.initialize()

    def create(self, applicant):
        creator = self.Creator(self._request, self.context)
        return creator.create(applicant)

    def log_action(self, action, verbose):
        logger = self.Logger(self._request, self.context)
        logger.log_action(action, verbose)

    def represent_subresources_listing(self, subresource_implemented):
        representer = self.SubResourceRepresenter(self._request, self.context)
        return representer.represent_listing(subresource_implemented)

    def represent_subresource_created(self, subresource):
        representer = self.SubResourceRepresenter(self._request, self.context)
        return representer.represent_created(subresource)

    def save(self):
        if self.context.modified:
            return save_auction(self._request)


@implementer(IBidManager)
class BidManager(object):
    name = 'Bid Manager'

    def __init__(self, request, context):
        self._request = request
        self.context = context
        self._auction = context.__parent__
        self._is_changed = False
        self._is_saved = False

    def initialize(self):
        initializator = self.Initializator(self._request, self.context)
        initializator.initialize()

    def change(self):
        changer = self.Changer(self._request, self.context)
        self._is_changed = changer.change()
        return self._is_changed

    def create(self, applicant):
        creator = self.Creator(self._request, self.context)
        creature = creator.create(applicant)
        if creature:
            self._is_changed = True
        return creature

    def log_action(self, action, verbose):
        logger = self.Logger(self._request, self.context)
        logger.log_action(action, verbose)

    def save(self):
        if self._is_changed:
            self._is_saved = save_auction(self._request)
        return self._is_saved

    def delete(self):
        deleter = self.Deleter(self._request, self.context)
        self._is_changed = deleter.delete()
        return self._is_changed

    def represent(self, method):
        representer = self.Representer(self._request, self.context)
        return representer.represent(method)


@implementer(IQuestionManager)
class QuestionManager(object):
    name = 'Question Manager'

    def __init__(self, request, context):
        self._request = request
        self.context = context
        self._auction = context.__parent__

    def change(self):
        changer = self.Changer(self._request, self.context)
        return changer.change()

    def save(self):
        if self._auction.modified:
            return save_auction(self._request)


@implementer(IItemManager)
class ItemManager(object):
    name = 'Item Manager'

    def __init__(self, request, context):
        self._request = request
        self.context = context
        self._auction = context.__parent__
        self._is_changed = False
        self._is_saved = False

    def change(self):
        changer = self.Changer(self._request, self.context)
        self._is_changed = changer.change()

        return self._is_changed

    def create(self, applicant):
        creator = self.Creator(self._request, self.context)
        creature = creator.create(applicant)
        if creature:
            self._is_changed = True
        return creature

    def represent(self, method):
        representer = self.Representer(self.context)
        return representer.represent(method)

    def log_action(self, action, verbose):
        logger = self.Logger(self._request, self.context)
        logger.log_action(action, verbose)

    def save(self):
        if self._is_changed:
            self._is_saved = save_auction(self._request)
        return self._is_saved


@implementer(ICancellationManager)
class CancellationManager(object):
    name = 'Cancellation Manager'

    def __init__(self, request, context):
        self._request = request
        self.context = context
        self._auction = context.__parent__
        self._is_changed = False
        self._is_saved = False

    def change(self):
        changer = self.Changer(self._request, self.context)
        self._is_changed = changer.change()
        return self._is_changed

    def represent(self, method):
        representer = self.Representer(self.context)
        return representer.represent(method)

    def create(self, applicant):
        creator = self.Creator(self._request, self.context)
        creature = creator.create(applicant)
        if creature:
            self._is_changed = True
        return creature

    def log_action(self, action, verbose):
        logger = self.Logger(self._request, self.context)
        logger.log_action(action, verbose)

    def represent_subresources_listing(self, subresource_implemented):
        representer = self.SubResourceRepresenter(self._request, self.context)
        return representer.represent_listing(subresource_implemented)

    def represent_subresource_created(self, subresource):
        representer = self.SubResourceRepresenter(self._request, self.context)
        return representer.represent_created(subresource)

    def save(self):
        if self._is_changed:
            self._is_saved = save_auction(self._request)
        return self._is_saved


@implementer(IDocumentManager)
class DocumentManager(object):
    name = 'Document Manager'

    def __init__(self, request, context):
        self._request = request
        self.context = context
        self._auction = context.__parent__

    def change(self):
        changer = self.Changer(self._request, self.context)
        return changer.change()

    def put(self):
        changer = self.Changer(self._request, self.context)
        return changer.put()

    def save(self):
        if self._auction.modified:
            return save_auction(self._request)


@implementer(IBidDocumentManager)
class BidDocumentManager(object):
    name = 'Cancellation Manager'

    def __init__(self, request, context):
        self._request = request
        self.context = context
        self._auction = context.__parent__
        self._is_changed = False
        self._is_saved = False

    def change(self):
        changer = self.Changer(self._request, self.context)
        self._is_changed = changer.change()
        return self._is_changed

    def save(self):
        if self._is_changed:
            self._is_saved = save_auction(self._request)
        return self._is_saved
