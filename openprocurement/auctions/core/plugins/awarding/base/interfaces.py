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

    def create_award_complaint(self, request, **kwargs):
        request.errors.add(
            'body',
            'data',
            'Can\'t create complaint'
        )
        request.errors.status = 403
        raise error_handler(request)
