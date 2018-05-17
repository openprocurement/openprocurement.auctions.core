# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler


class BaseAwardManagerAdapter(object):
    name = 'Award Manager'

    def __init__(self, context):
        self.context = context
