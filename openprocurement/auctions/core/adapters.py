# -*- coding: utf-8 -*-
from openprocurement.api.adapters import (
    ContentConfigurator,
    AwardingNextCheckAdapter
)
from openprocurement.api.utils import error_handler


class AuctionConfigurator(ContentConfigurator):
    name = 'Auction Configurator'
    model = None
    award_model = None


class AuctionAwardingNextCheckAdapter(AwardingNextCheckAdapter):
    name = 'Auction Awarding Next Check Adapter'


class AuctionManagerAdapter(object):
    name = 'Auction Manager'
    context = None

    def __init__(self, context):
        self.context = context

    def _validate(self, request, validators):
        kwargs = {'request': request, 'error_handler': error_handler}
        for validator in validators:
            validator(**kwargs)

    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass
