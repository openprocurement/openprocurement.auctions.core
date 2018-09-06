# -*- coding: utf-8 -*-
from openprocurement.api.plugins.transferring.validation import (
    validate_ownership_data
)
from openprocurement.auctions.core.plugins.transferring.validation import (
    validate_change_ownership_accreditation
)
from openprocurement.auctions.core.utils import (
    json_view,
    opresource,
    APIResource,
    ROUTE_PREFIX,
    context_unpack,
    save_auction,
    get_auction_route_name
)


@opresource(name='Auction ownership',
            path='/auctions/{auction_id}/ownership',
            description="Auctions Ownership")
class AuctionsResource(APIResource):

    @json_view(permission='create_auction',
               validators=(validate_change_ownership_accreditation,
                           validate_ownership_data))
    def post(self):
        auction = self.request.validated['auction']
        auction_path = get_auction_route_name(self.request, auction)
        location = self.request.route_path(auction_path, auction_id=auction.id)
        location = location[len(ROUTE_PREFIX):]  # strips /api/<version>
        ownership_changed = self.request.change_ownership(location)

        if ownership_changed and save_auction(self.request):
            self.LOGGER.info(
                'Updated ownership of auction {}'.format(auction.id),
                extra=context_unpack(
                    self.request, {'MESSAGE_ID': 'auction_ownership_update'}
                )
            )

            return {'data': self.request.context.serialize('view')}


@opresource(
    name='Auction credentials',
    path='/auctions/{auction_id}/extract_credentials',
    description="Auctions Extract Credentials"
)
class AuctionResource(APIResource):

    @json_view(permission='extract_credentials')
    def get(self):
        self.LOGGER.info('Extract credentials for auction {}'.format(self.context.id))
        auction = self.request.validated['auction']
        data = auction.serialize('extract_credentials') or {}
        data['transfer_token'] = auction.transfer_token
        return {'data': data}
