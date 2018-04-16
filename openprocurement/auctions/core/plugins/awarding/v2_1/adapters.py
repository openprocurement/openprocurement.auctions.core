from .models import Award
from .utils import (
    create_awards,
    switch_to_next_award,
    next_check_awarding,
)

from openprocurement.auctions.core.adapters import (
    AuctionAwardingNextCheckAdapter
)


class AwardingV2_1ConfiguratorMixin(object):
    """ Brings methods that are needed for the process of Awarding
        
        start_awarding - call after auction ends in auction view
        back_to_awarding - call when participant was disqualified
    """
    award_model = Award
    awarding_type = 'awarding_2_1'

    def start_awarding(self):
        """
            Call create_awards method, that create 2 awards for 2 bidders
        """
        return create_awards(self.request)

    def back_to_awarding(self):
        """
            Call when we need to qualify another biddder
        """
        return switch_to_next_award(self.request)


class AwardingNextCheckV2_1(AuctionAwardingNextCheckAdapter):
    """Use next_check_awarding from V2 awarding"""
    def add_awarding_checks(self, auction):
        return next_check_awarding(auction)