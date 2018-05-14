# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    json_view,
    context_unpack,
    APIResource,
    calculate_business_date,
)

from openprocurement.auctions.core.models import STAND_STILL_TIME
from openprocurement.auctions.core.utils import (
    apply_patch,
    save_auction,
    opresource,
)
from openprocurement.auctions.core.validation import (
    validate_award_data,
    validate_patch_award_data,
    validate_award_data_post_common,
    validate_patch_award_data_patch_common,
)
from openprocurement.auctions.core.plugins.awarding.base.interfaces import IAwardManagerAdapter


@opresource(
    name='awarding_1_0:Auction Awards',
    collection_path='/auctions/{auction_id}/awards',
    path='/auctions/{auction_id}/awards/{award_id}',
    awardingType='awarding_1_0',
    description="Auction awards"
)
class AuctionAwardResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        return {'data': [i.serialize("view") for i in self.request.validated['auction'].awards]}

    @json_view(permission='view_auction')
    def get(self):
        return {'data': self.request.validated['award'].serialize("view")}

    @json_view(content_type="application/json", permission='create_award',
               validators=(validate_award_data, validate_award_data_post_common))
    def collection_post(self):
        manager = self.request.registry.getAdapter(self.request.validated['award'], IAwardManagerAdapter)
        manager.create_award(self.request)
        award = self.request.validated['award']
        if save_auction(self.request):
            self.LOGGER.info(
                'Created auction award {}'.format(award.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'auction_award_create'},
                    {'award_id': award.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(
                _route_name=route, award_id=award.id, _query={}
            )
            return {'data': award.serialize("view")}

    @json_view(content_type="application/json", permission='edit_auction',
               validators=(validate_patch_award_data, validate_patch_award_data_patch_common))
    def patch(self):
        manager = self.request.registry.getAdapter(self.context, IAwardManagerAdapter)
        manager.change_award(self.request, server_id=self.server_id)
        award = self.request.validated['award']
        if save_auction(self.request):
            self.LOGGER.info(
                'Updated auction award {}'.format(self.request.context.id),
                extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_patch'}))
            return {'data': award.serialize("view")}
