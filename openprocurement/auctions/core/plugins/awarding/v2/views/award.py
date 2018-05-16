# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    APIResource,
    context_unpack,
    json_view,
)
from openprocurement.auctions.core.utils import (
    opresource,
    save_auction,
)
from openprocurement.auctions.core.validation import (
    validate_award_data,
)
from openprocurement.auctions.core.plugins.awarding.base.interfaces import (
    IAwardManagerAdapter,
)


@opresource(
    name='awarding_2_0:Auction Awards',
    collection_path='/auctions/{auction_id}/awards',
    path='/auctions/{auction_id}/awards/{award_id}',
    awardingType='awarding_2_0',
    description="Auction awards"
)
class AuctionAwardResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        return {'data': [i.serialize("view") for i in self.request.validated['auction'].awards]}

    @json_view(content_type="application/json", permission='create_award',
               validators=(validate_award_data, ))
    def collection_post(self):
        award = self.request.validated['award']
        award_manager = self.request.registry.getAdapter(award, IAwardManagerAdapter)
        award_manager.create_award(self.request)

        if save_auction(self.request):
            self.LOGGER.info(
                'Created auction award {}'.format(award.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'auction_award_create'},
                    {'award_id': award.id}
                )
            )
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(
                _route_name=route, award_id=award.id, _query={}
            )
            return {'data': award.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        return {'data': self.request.validated['award'].serialize("view")}

    @json_view(content_type="application/json", permission='edit_auction_award')
    def patch(self):
        award = self.request.context
        award_manager = self.request.registry.getAdapter(award, IAwardManagerAdapter)
        award_manager.change_award(self.request, server_id=self.server_id)

        if save_auction(self.request):
            self.LOGGER.info('Updated auction award {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_patch'}))
            return {'data': award.serialize("view")}
