from openprocurement.auctions.core.plugins.awarding.v1.models import Award
from openprocurement.auctions.core.plugins.awarding.v1.utils import add_next_award


class AwardingV1ConfiguratorMixin(object):
    award_model = Award

    def add_award(self):
        return add_next_award(self.request)
