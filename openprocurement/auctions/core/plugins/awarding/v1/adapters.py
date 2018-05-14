from .models import Award
from .utils import (
    add_next_award,
    next_check_awarding
)

from openprocurement.auctions.core.adapters import (
    AuctionAwardingNextCheckAdapter
)
from openprocurement.auctions.core.plugins.awarding.base.adapters import (
    BaseAwardManagerAdapter
)
from openprocurement.api.utils import (
    get_now,
    context_unpack,
    calculate_business_date,
)
from openprocurement.auctions.core.utils import (
    save_auction,
    apply_patch,
)
from openprocurement.auctions.core.models import STAND_STILL_TIME


class AwardingV1ConfiguratorMixin(object):
    """ Brings methods that are needed for the process of Awarding

        start_awarding - call after auction ends in auction view
        back_to_awarding - call when participant was disqualified
    """
    award_model = Award
    awarding_type = 'awarding_1_0'

    def start_awarding(self):
        """Using add_next_award method from belowThreshold procedure.

           add_next_award create 1 award and Awarding process start with
           1 award object
        """
        return add_next_award(self.request)

    def back_to_awarding(self):
        """ Call when we need to qualify another biddder.

            When award created at the first time has unsuccessful status
            add_next_award will create another one award object for another
            bidder
        """
        return add_next_award(self.request)


class AwardingNextCheckV1(AuctionAwardingNextCheckAdapter):
    """Use next_check_awarding from V1 awarding"""
    def add_awarding_checks(self, auction):
        return next_check_awarding(auction)


class AwardManagerV1Adapter(BaseAwardManagerAdapter):
    """
    Logic for actions on Award-v1
    """
    name = 'Avard-v1 Manager'

    def create_award(self, request, **kwargs):
        award = request.validated['award']
        award.complaintPeriod = {'startDate': get_now().isoformat()}
        request.validated['auction'].awards.append(award)


    def change_award(self, request, **kwargs):
        auction = request.validated['auction']
        award = request.context
        award_status = award.status
        server_id = kwargs['server_id']

        if any([i.status != 'active' for i in auction.lots if i.id == award.lotID]):
            request.errors.add('body', 'data', 'Can update award only in active lot status')
            request.errors.status = 403
            return
        apply_patch(request, save=False, src=request.context.serialize())
        if award_status == 'pending' and award.status == 'active':
            award.complaintPeriod.endDate = calculate_business_date(get_now(), STAND_STILL_TIME, auction, True)
            auction.contracts.append(type(auction).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'value': award.value,
                'date': get_now(),
                'items': [i for i in auction.items if i.relatedLot == award.lotID],
                'contractID': '{}-{}{}'.format(auction.auctionID, server_id, len(auction.contracts) + 1)}))
            request.content_configurator.start_awarding()
        elif award_status == 'active' and award.status == 'cancelled':
            now = get_now()
            if award.complaintPeriod.endDate > now:
                award.complaintPeriod.endDate = now
            for j in award.complaints:
                if j.status not in ['invalid', 'resolved', 'declined']:
                    j.status = 'cancelled'
                    j.cancellationReason = 'cancelled'
                    j.dateCanceled = now
            for i in auction.contracts:
                if i.awardID == award.id:
                    i.status = 'cancelled'
            request.content_configurator.back_to_awarding()
        elif award_status == 'pending' and award.status == 'unsuccessful':
            award.complaintPeriod.endDate = calculate_business_date(get_now(), STAND_STILL_TIME, auction, True)
            request.content_configurator.back_to_awarding()
        elif (
            award_status == 'unsuccessful'
            and award.status == 'cancelled'
            and any(
                [i.status in ['claim', 'answered', 'pending', 'resolved'] for i in award.complaints]
            )
        ):
            if auction.status == 'active.awarded':
                auction.status = 'active.qualification'
                auction.awardPeriod.endDate = None
            now = get_now()
            award.complaintPeriod.endDate = now
            cancelled_awards = []
            for i in auction.awards[auction.awards.index(award):]:
                if i.lotID != award.lotID:
                    continue
                i.complaintPeriod.endDate = now
                i.status = 'cancelled'
                for j in i.complaints:
                    if j.status not in ['invalid', 'resolved', 'declined']:
                        j.status = 'cancelled'
                        j.cancellationReason = 'cancelled'
                        j.dateCanceled = now
                cancelled_awards.append(i.id)
            for i in auction.contracts:
                if i.awardID in cancelled_awards:
                    i.status = 'cancelled'
            request.content_configurator.back_to_awarding()
        elif (
            request.authenticated_role != 'Administrator'
            and not(
                award_status == 'pending'
                and award.status == 'pending'
            )
        ):
            request.errors.add('body', 'data', 'Can\'t update award in current ({}) status'.format(award_status))
            request.errors.status = 403
            return
