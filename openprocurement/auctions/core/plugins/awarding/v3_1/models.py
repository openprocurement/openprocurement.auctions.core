# -*- coding: utf-8 -*-
from datetime import timedelta

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
    awardV3_1Document as Document,
    dgfComplaint as Complaint,
    SwiftsureItem as Item,
    dgfOrganization as Organization,
    Award as BaseAward
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)
from .interfaces import IAwardV3_1


@implementer(IAwardV3_1)
class Award(BaseAward):
    """
        Award model for Awarding 3.1 procedure
    """
    class Options:
        roles = {
            'create': blacklist('id', 'status', 'date', 'documents', 'complaints', 'complaintPeriod', 'verificationPeriod', 'signingPeriod'),
            'Administrator': whitelist('verificationPeriod', 'signingPeriod', 'admissionPeriod'),
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

    status = StringType(required=True, choices=['pending.waiting', 'unsuccessful', 'active', 'cancelled', 'pending', 'pending.admission'], default='pending')
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])
    items = ListType(ModelType(Item))
    verificationPeriod = ModelType(Period)
    signingPeriod = ModelType(Period)
    admissionPeriod = ModelType(Period)

    VERIFICATION_PERIOD_PARAMS = {
        'delta': timedelta(days=10),
        'specific_hour': 18,
        'working_days': True
    }

    SIGNING_PERIOD_PARAMS = {
        'delta': timedelta(days=40),
        'specific_hour': 18,
        'working_days': False,
        'result_is_working_day': True
    }

    ADMISSION_PERIOD_PARAMS = {
        'delta': timedelta(days=5),
        'specific_hour': 18,
        'working_days': True
    }

    @serializable(serialized_name="verificationPeriod", serialize_when_none=False)
    def award_verificationPeriod(self):
        period = self.verificationPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            period.endDate = calculate_business_date(
                start=period.startDate,
                context=auction,
                **self.VERIFICATION_PERIOD_PARAMS
            )
        return period.to_primitive()

    @serializable(serialized_name="signingPeriod", serialize_when_none=False)
    def award_signingPeriod(self):
        period = self.signingPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            period.endDate = calculate_business_date(
                start=period.startDate,
                context=auction,
                **self.SIGNING_PERIOD_PARAMS
            )
        return period.to_primitive()
