from openprocurement.auctions.core.plugins.awarding.v2.utils import create_awards
from openprocurement.auctions.core.plugins.awarding.v2.models import Award


class AwardingV2ConfiguratorMixin(object):
    award_model = Award

    def add_award(self):
        return create_awards(self.request)
