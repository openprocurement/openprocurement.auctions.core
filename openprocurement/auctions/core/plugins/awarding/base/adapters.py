# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler


class BaseAwardManagerAdapter(object):
    name = 'Award Manager'

    def __init__(self, context):
        self.context = context

    def _validate(self, request, validators):
        kwargs = {'request': request, 'error_handler': error_handler}
        for validator in validators:
            validator(**kwargs)
