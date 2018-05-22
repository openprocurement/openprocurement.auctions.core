from .models import Award
from .utils import (
    create_awards,
    switch_to_next_award,
    next_check_awarding,
    check_award_status
)

from openprocurement.auctions.core.adapters import (
    AuctionAwardingNextCheckAdapter
)
from openprocurement.auctions.core.plugins.awarding.base.adapters import (
    BaseAwardManagerAdapter
)
from openprocurement.api.utils import (
    get_now,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    validate_with,
)
from openprocurement.auctions.core.validation import (
    validate_award_data_post_common,
    validate_patch_award_data,
    validate_patch_award_data_patch_common,
)
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    check_document_existence
)


class AwardingV2ConfiguratorMixin(object):
    """ Brings methods that are needed for the process of Awarding

        start_awarding - call after auction ends in auction view
        back_to_awarding - call when participant was disqualified
    """
    award_model = Award
    awarding_type = 'awarding_2_0'

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


class AwardingNextCheckV2(AuctionAwardingNextCheckAdapter):
    """Use next_check_awarding from V2 awarding"""
    def add_awarding_checks(self, auction):
        return next_check_awarding(auction)


class AwardManagerV2Adapter(BaseAwardManagerAdapter):

    name = 'Awarding-v2 manager'

    create_validators = (
        validate_award_data_post_common,
    )

    change_validators = (
        validate_patch_award_data,
        validate_patch_award_data_patch_common,
    )

    @validate_with(create_validators)
    def create_award(self, request, **kwargs):
        award = request.validated['award']
        award.complaintPeriod = award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {
            'startDate': get_now()
        }
        request.validated['auction'].awards.append(award)

    @validate_with(change_validators)
    def change_award(self, request, **kwargs):
        auction = request.validated['auction']
        award = request.context
        award_status = award.status
        server_id = kwargs['server_id']

        now = get_now()
        if award_status in ['unsuccessful', 'cancelled']:
            request.errors.add('body', 'data', 'Can\'t update award in current ({}) status'.format(award_status))
            request.errors.status = 403
            return
        apply_patch(request, save=False, src=request.context.serialize())
        if award_status == 'pending.waiting' and award.status == 'cancelled':
            if request.authenticated_role == 'bid_owner':
                award.complaintPeriod.endDate = now
            else:
                request.errors.add(
                    'body',
                    'data',
                    'Only bid owner may cancel award in current ({}) status'.format(award_status)
                )
                request.errors.status = 403
                return
        elif award_status == 'pending.verification' and award.status == 'pending.payment':
            if check_document_existence(award, 'auctionProtocol'):
                award.verificationPeriod.endDate = now
            else:
                request.errors.add(
                    'body',
                    'data',
                    'Can\'t switch award status to (pending.payment) before auction owner load auction protocol'
                )
                request.errors.status = 403
                return
        elif award_status == 'pending.payment' and award.status == 'active' and award.paymentPeriod.endDate > now:
            award.complaintPeriod.endDate = award.paymentPeriod.endDate = now
            auction.contracts.append(type(auction).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'value': award.value,
                'date': get_now(),
                'items': [i for i in auction.items if i.relatedLot == award.lotID],
                'contractID': '{}-{}{}'.format(
                    auction.auctionID,
                    server_id,
                    len(auction.contracts) + 1
                )
            }))
            auction.status = 'active.awarded'
            auction.awardPeriod.endDate = now
        elif award_status != 'pending.waiting' and award.status == 'unsuccessful':
            if award_status == 'pending.verification':
                award.verificationPeriod.endDate = now
            elif award_status == 'pending.payment':
                award.paymentPeriod.endDate = now
            elif award_status == 'active':
                award.signingPeriod.endDate = now
                auction.awardPeriod.endDate = None
                auction.status = 'active.qualification'
                for i in auction.contracts:
                    if i.awardID == award.id:
                        i.status = 'cancelled'
            award.complaintPeriod.endDate = now
            request.content_configurator.back_to_awarding()
        elif award_status != award.status:
            request.errors.add(
                'body', 'data', 'Can\'t switch award ({}) status to ({}) status'.format(
                    award_status,
                    award.status
                )
            )
            request.errors.status = 403
            return
