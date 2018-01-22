from openprocurement.auctions.core.plugins.awarding.v3.models import Award
from openprocurement.auctions.core.plugins.awarding.v3.utils import (
    create_awards,
    switch_to_next_award
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
