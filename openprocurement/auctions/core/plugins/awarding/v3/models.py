from pyramid.security import Allow
from schematics.transforms import (
    blacklist,
    whitelist
)
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer

from openprocurement.api.models.common import Period
from openprocurement.api.models.schematics_extender import ListType
from openprocurement.api.utils import calculate_business_date

from openprocurement.auctions.core.models import (
    get_auction,
    dgfDocument as Document,
    dgfComplaint as Complaint,
    dgfItem as Item,
    dgfOrganization as Organization,
    Award as BaseAward
)
from openprocurement.auctions.core.plugins.awarding.base.constants import (
    CONTRACT_SIGNING_TIME,
)
from openprocurement.auctions.core.plugins.awarding.v3.constants import (
    VERIFY_AUCTION_PROTOCOL_TIME
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)
from .interfaces import IAwardV3


@implementer(IAwardV3)
class Award(BaseAward):
    """
        Award model for Awawrding 3.0 procedure
    """
    class Options:
        roles = {
            'create': blacklist('id', 'status', 'date', 'documents', 'complaints', 'complaintPeriod', 'verificationPeriod', 'signingPeriod', 'paymentPeriod'),
            'Administrator': whitelist('verificationPeriod', 'signingPeriod'),
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

    status = StringType(required=True, choices=['pending.waiting', 'unsuccessful', 'active', 'cancelled', 'pending', 'pending.payment', 'pending.verification'], default='pending') # pending.payment and pending.verification is deprecated
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])
    items = ListType(ModelType(Item))
    verificationPeriod = ModelType(Period)
    signingPeriod = ModelType(Period)
    paymentPeriod = ModelType(Period)

    @serializable(serialized_name="verificationPeriod", serialize_when_none=False)
    def award_verificationPeriod(self):
        period = self.verificationPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            period.endDate = calculate_business_date(period.startDate, VERIFY_AUCTION_PROTOCOL_TIME, auction, True)
            round_to_18_hour_delta = period.endDate.replace(hour=18, minute=0, second=0) - period.endDate
            period.endDate = calculate_business_date(period.endDate, round_to_18_hour_delta, auction, False)

        return period.to_primitive()

    @serializable(serialized_name="signingPeriod", serialize_when_none=False)
    def award_signingPeriod(self):
        period = self.signingPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            period.endDate = calculate_business_date(period.startDate, CONTRACT_SIGNING_TIME, auction, True)
            round_to_18_hour_delta = period.endDate.replace(hour=18, minute=0, second=0) - period.endDate
            period.endDate = calculate_business_date(period.endDate, round_to_18_hour_delta, auction, False)
        return period.to_primitive()
