# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute,
    Interface,
)

class IAwardManagerAdapter(Interface):
    name = Attribute('Award name')

    def create_award(self, request, **kwargs):
        raise NotImplementedError

    def change_award(self, request, **kwargs):
        raise NotImplementedError
