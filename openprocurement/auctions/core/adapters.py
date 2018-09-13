# -*- coding: utf-8 -*-
from openprocurement.api.adapters import (
    ContentConfigurator,
    AwardingNextCheckAdapter
)
from openprocurement.api.utils import error_handler


class AuctionConfigurator(ContentConfigurator):
    name = 'Auction Configurator'
    model = None
    award_model = None


class AuctionAwardingNextCheckAdapter(AwardingNextCheckAdapter):
    name = 'Auction Awarding Next Check Adapter'


class AuctionManagerAdapter(object):
    name = 'Auction Manager'
    context = None

    allow_pre_terminal_statuses = False

    def __init__(self, context):
        self.context = context

    def _validate(self, request, validators):
        kwargs = {'request': request, 'error_handler': error_handler}
        for validator in validators:
            validator(**kwargs)

    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass

    def pendify_auction_status(self, target_status):
        """Get terminal status of auction, but take into account need of pre-terminal status of it

        Let auction a1 have pre-terminal statuses, e.g. "pending.complete", "pending.cancelled", etc.
        So, pendify_auction(a1, "complete") will set status of the a1 to "pending.complete".
        Otherwise, if some auction a2 will not have pre-terminal statuses, this function will
        operate as following: pendify_auction(a2, "complete") will turn status of a2 into "complete".
        """
        auction = self.context
        pending_prefix = 'pending'

        if (
            getattr(auction, 'merchandisingObject', False),  # indicates registry integration
            and self.allow_pre_terminal_statuses  # allows to manage using of preterm statuses
        ):
            status = '{0}.{1}'.format(pending_prefix, target_status)
        else:
            status = target_status

        auction.status = status
