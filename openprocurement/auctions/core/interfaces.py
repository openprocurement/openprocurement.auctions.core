# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute, Interface
)
from openprocurement.api.interfaces import IAuction  # noqa: F401


class IAuctionInitializator(Interface):
    """ Base auction marker interface """


class IAuctionChanger(Interface):
    """ Base auction marker interface """


class IAuctionManager(Interface):
    name = Attribute('Auction name')
