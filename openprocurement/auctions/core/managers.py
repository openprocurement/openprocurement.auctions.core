# -*- coding: utf-8 -*-
from zope.interface import implementer
from openprocurement.api.utils import error_handler

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
        self._context = context

    def _validate(self, request, validators):
        kwargs = {'request': request, 'error_handler': error_handler}
        for validator in validators:
            validator(**kwargs)

    def initialize(self):
        initializator = self.Initializator(self._request, self._context)
        initializator.initialize()

    def change(self):
        changer = self.Changer(self._request, self._context)
        return changer.change()

    def upload_document(self):
        documenter = self.Documenter(self._request, self._context)
        return documenter.upload_document()

    def add_question(self):
        questioner = self.Questioner(self._request, self._context)
        return questioner.add_question()

    def check(self):
        checker = self.Checker(self._request, self._context)
        return checker.check()

    def create(self):
        creator = self.Creator(self._request, self._context)
        return creator.create()

    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass

    def save(self):
        return save_auction(self._request)


@implementer(IBidManager)
class BidManager(object):
    name = 'Bid Manager'

    def __init__(self, request, context):
        self._request = request
        self._context = context

    def initialize(self):
        initializator = self.Initializator(self._request, self._context)
        initializator.initialize()

    def change(self):
        changer = self.Changer(self._request, self._context)
        return changer.change()

    def upload_document(self):
        documenter = self.Documenter(self._request, self._context)
        return documenter.upload_document()

    def save(self):
        return save_auction(self._request)

    def delete(self):
        deleter = self.Deleter(self._request, self._context)
        if deleter.validate():
            return deleter.delete()


@implementer(IQuestionManager)
class QuestionManager(object):
    name = 'Question Manager'

    def __init__(self, request, context):
        self._request = request
        self._context = context

    def change(self):
        changer = self.Changer(self._request, self._context)
        return changer.change()

    def save(self):
        return save_auction(self._request)
