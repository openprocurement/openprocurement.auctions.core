# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute, Interface
)


class IAuction(Interface):
    """ Base auction marker interface """


class IAuctionManager(Interface):
    name = Attribute('Auction name')

    def create_auction(request):
        raise NotImplementedError

    def change_auction(request):
        raise NotImplementedError
