# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    save_auction,
    apply_patch
)

from openprocurement.api.adapters import (
    ContentConfigurator,
    AwardingNextCheckAdapter
)


class AuctionConfigurator(ContentConfigurator):
    name = 'Auction Configurator'
    model = None
    award_model = None


class AuctionAwardingNextCheckAdapter(AwardingNextCheckAdapter):
    name = 'Auction Awarding Next Check Adapter'


class AuctionManagerAdapter(object):
    name = 'Auction Manager'

    def __init__(self, request, context):
        self._request = request
        self._context = context

    def initialize(self, initializator):
        self._initializator = initializator
        self._initializator.initialize()

    def change(self, changer):
        self._changer = changer
        return self._changer.change()

    def upload_document(self, documenter):
        self._documenter = documenter
        return self._documenter.upload_document()

    def add_question(self, questioner):
        self._questioner = questioner
        return self._questioner.add_question()

    def check(self, checker):
        apply_patch(self._request, save=False, src=self._request.validated['auction_src'])
        self._checker = checker
        return self._checker.check()

    def create_auction(self):
        pass

    def change_auction(self):
        pass

    def save(self):
        return save_auction(self._request)
