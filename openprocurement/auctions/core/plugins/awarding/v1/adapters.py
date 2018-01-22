from openprocurement.auctions.core.plugins.awarding.v1.models import Award
from openprocurement.auctions.core.plugins.awarding.v1.utils import (
    add_next_award
)


class AwardingV1ConfiguratorMixin(object):
    """
        Brings methods that are needed for the process of Awarding
        start_awarding - call after auction ends in auction view
        back_to_awarding - call when participant was disqualified
    """
    award_model = Award

    def start_awarding(self):
        """
            Use universal add_next_award method that 1 award object
        """
        return add_next_award(self.request)

    def back_to_awarding(self):
        """
            Call when we need to qualify another biddder
        """
        return add_next_award(self.request)
