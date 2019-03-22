# -*- coding: utf-8 -*-


class BaseAwardManagerAdapter(object):
    name = 'Award Manager'

    def __init__(self, context):
        self.context = context
