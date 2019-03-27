# -*- coding: utf-8 -*-


class BaseAwardManagerAdapter(object):
    name = 'Award Manager'

    COPY_AWARD_VALUE_TO_CONTRACT = True

    def __init__(self, context):
        self.context = context
