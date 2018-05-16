from zope.interface import implementer
from pyramid.security import Allow
from schematics.transforms import (
    blacklist,
    whitelist
)
from schematics.types import StringType
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType

from openprocurement.api.models.common import Period
from openprocurement.api.models.schematics_extender import ListType

from openprocurement.auctions.core.models import (
    Award as BaseAward,
    dgfCDB2Complaint as Complaint,
    dgfCDB2Document as Document,
    dgfCDB2Item as Item,
    dgfOrganization as Organization,
    get_auction,
)
from openprocurement.auctions.core.plugins.awarding.base.constants import (
    AWARD_PAYMENT_TIME,
    CONTRACT_SIGNING_TIME,
)
from openprocurement.auctions.core.plugins.awarding.v2_1.constants import (
    VERIFY_AUCTION_PROTOCOL_TIME
)
from .utils import calculate_enddate
from .interfaces import IAwardV2_1


@implementer(IAwardV2_1)
class Award(BaseAward):
    class Options:
        roles = {
            'create': blacklist('id', 'status', 'date', 'documents', 'complaints', 'complaintPeriod', 'verificationPeriod', 'paymentPeriod', 'signingPeriod'),
            'Administrator': whitelist('verificationPeriod', 'paymentPeriod', 'signingPeriod'),
        }

    def __local_roles__(self):
        auction = get_auction(self)
        for bid in auction.bids:
            if bid.id == self.bid_id:
                bid_owner = bid.owner
                bid_owner_token = bid.owner_token
        return dict([('{}_{}'.format(bid_owner, bid_owner_token), 'bid_owner')])

    def __acl__(self):
        auction = get_auction(self)
        for bid in auction.bids:
            if bid.id == self.bid_id:
                bid_owner = bid.owner
                bid_owner_token = bid.owner_token
        return [(Allow, '{}_{}'.format(bid_owner, bid_owner_token), 'edit_auction_award')]

    # pending status is deprecated. Only for backward compatibility with awarding 1.0
    status = StringType(required=True, choices=['pending.waiting', 'pending.verification', 'pending.payment', 'unsuccessful', 'active', 'cancelled', 'pending'], default='pending.verification')
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))
    verificationPeriod = ModelType(Period)
    paymentPeriod = ModelType(Period)
    signingPeriod = ModelType(Period)

    @serializable(serialized_name="verificationPeriod", serialize_when_none=False)
    def award_verificationPeriod(self):
        period = self.verificationPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            calculate_enddate(auction, period, VERIFY_AUCTION_PROTOCOL_TIME)
        return period.to_primitive()

    @serializable(serialized_name="paymentPeriod", serialize_when_none=False)
    def award_paymentPeriod(self):
        period = self.paymentPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            calculate_enddate(auction, period, AWARD_PAYMENT_TIME)
        return period.to_primitive()

    @serializable(serialized_name="signingPeriod", serialize_when_none=False)
    def award_signingPeriod(self):
        period = self.signingPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            calculate_enddate(auction, period, CONTRACT_SIGNING_TIME)
        return period.to_primitive()
