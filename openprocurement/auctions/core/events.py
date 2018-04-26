# -*- coding: utf-8 -*-


class AuctionInitializeEvent(object):
    """ Asset initialization event. """

    def __init__(self, auction):
        self.auction = auction
