# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute, Interface
)
from openprocurement.api.interfaces import IAuction  # noqa: F401


class IAuctionManager(Interface):
    name = Attribute('Auction name')

    def create_auction(request):
        raise NotImplementedError

    def change_auction(request):
        raise NotImplementedError
