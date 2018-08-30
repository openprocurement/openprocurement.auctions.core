# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute, Interface
)


class IAuction(Interface):
    """ Base auction marker interface """


class IAuctionInitializator(Interface):
    """ Base auction marker interface """


class IAuctionChanger(Interface):
    """ Base auction marker interface """


class IAuctionManager(Interface):
    name = Attribute('Auction name')
