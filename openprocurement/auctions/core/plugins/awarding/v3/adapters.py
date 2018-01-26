from .models import Award
from .utils import (
    create_awards,
    switch_to_next_award,
    next_check_awarding
)

from openprocurement.auctions.core.adapters import (
    AuctionAwardingNextCheckAdapter
)


class AwardingV3ConfiguratorMixin(object):
    """Brings methods that are needed for the process of Awarding
        
        start_awarding - call after auction ends in auction view
        back_to_awarding - call when participant was disqualified
    """
    award_model = Award

    def start_awarding(self):
        """
            Call create_awards method, that create specified in constant
            number of awards in pending and pending.waiting status 
        """
        return create_awards(self.request)

    def back_to_awarding(self):
        """
            Call when we need to qualify another biddder
        """
        return switch_to_next_award(self.request)

    def check_award_status(self, request, award, now):
        """Checking protocol and contract loading by the owner in time."""
        return check_award_status(request, award, now)

      
class AwardingNextCheckV3(AuctionAwardingNextCheckAdapter):
    """Use next_check_awarding from V3 awarding"""
    def add_awarding_checks(self, auction):
        return next_check_awarding(auction)
