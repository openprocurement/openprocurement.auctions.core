from .models import Award
from .utils import (
    create_awards,
    switch_to_next_award,
    check_award_status
)


class AwardingV2ConfiguratorMixin(object):
    """ Brings methods that are needed for the process of Awarding
        
        start_awarding - call after auction ends in auction view
        back_to_awarding - call when participant was disqualified
    """
    award_model = Award

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

    def check_award_status(self, request, award, now):
        """Checking required documents loading and payment receiving in time."""
        return check_award_status(request, award, now)
