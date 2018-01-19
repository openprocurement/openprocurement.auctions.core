from openprocurement.auctions.core.plugins.awarding.v3.utils import create_awards
from openprocurement.auctions.core.plugins.awarding.v3.models import Award


class AwardingV3ConfiguratorMixin(object):
    award_model = Award

    def add_award(self):
        return create_awards(self.request)
