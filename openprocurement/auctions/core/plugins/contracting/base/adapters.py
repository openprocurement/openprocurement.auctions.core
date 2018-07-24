# -*- coding: utf-8 -*-
class BaseContractManagerAdapter(object):
    name = 'Contract Manager'

    def __init__(self, context):
        self.context = context
