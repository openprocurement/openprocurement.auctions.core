# -*- coding: utf-8 -*-
from zope.interface import implementer

from openprocurement.auctions.core.utils import (
    save_auction
)

from openprocurement.auctions.core.interfaces import (
    IAuctionManager,
    IBidManager,
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

    def decide_procedure(self):
        auctioner = self.Auctioneer(self._request, self.context)
        return auctioner.decide_procedure()

    def upload_document(self):
        documenter = self.Documenter(self._request, self.context)
        return documenter.upload_document()

    def add_question(self):
        questioner = self.Questioner(self._request, self.context)
        return questioner.add_question()

    def check(self):
        checker = self.Checker(self._request, self.context)
        return checker.check()

    def update_auction_urls(self):
        auctioner = self.Auctioneer(self._request, self.context)
        return auctioner.update_auction_urls()

    def bring_auction_result(self):
        auctioner = self.Auctioneer(self._request, self.context)
        return auctioner.bring_auction_result()

    def create(self):
        creator = self.Creator(self._request, self.context)
        return creator.create()

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

    def initialize(self):
        initializator = self.Initializator(self._request, self.context)
        initializator.initialize()

    def change(self):
        changer = self.Changer(self._request, self.context)
        return changer.change()

    def upload_document(self):
        documenter = self.Documenter(self._request, self.context)
        return documenter.upload_document()

    def save(self):
        if self._auction.modified:
            return save_auction(self._request)

    def delete(self):
        deleter = self.Deleter(self._request, self.context)
        if deleter.validate():
            return deleter.delete()


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
