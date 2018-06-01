# -*- coding: utf-8 -*-
from hashlib import sha512
from openprocurement.auctions.core.utils import (
    json_view,
    opresource,
    APIResource,
    ROUTE_PREFIX,
    context_unpack
)
from openprocurement.auctions.core.utils import (
    save_auction,
    get_auction_route_name
)
from openprocurement.auctions.core.plugins.transferring.utils import (
    extract_transfer, update_ownership, save_transfer
)
from openprocurement.auctions.core.plugins.transferring.validation import (
    validate_ownership_data, validate_auction_accreditation_level
)


@opresource(name='Auction ownership',
            path='/auctions/{auction_id}/ownership',
            description="Auctions Ownership")
class AuctionsResource(APIResource):

    @json_view(permission='create_auction',
               validators=(validate_auction_accreditation_level,
                           validate_ownership_data))
    def post(self):
        auction = self.request.validated['auction']
        data = self.request.validated['ownership_data']

        if auction.transfer_token == sha512(data['transfer']).hexdigest():
            auction_path = get_auction_route_name(self.request, auction)
            location = self.request.route_path(auction_path, auction_id=auction.id)

            location = location[len(ROUTE_PREFIX):]  # strips /api/<version>
            transfer = extract_transfer(self.request, transfer_id=data['id'])
            if transfer.get('usedFor') and transfer.get('usedFor') != location:
                self.request.errors.add('body', 'transfer', 'Transfer already used')
                self.request.errors.status = 403
                return
        else:
            self.request.errors.add('body', 'transfer', 'Invalid transfer')
            self.request.errors.status = 403
            return

        update_ownership(auction, transfer)
        self.request.validated['auction'] = auction

        transfer.usedFor = location
        self.request.validated['transfer'] = transfer
        if save_transfer(self.request):
            self.LOGGER.info('Updated transfer relation {}'.format(transfer.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'transfer_relation_update'}))

            if save_auction(self.request):
                self.LOGGER.info(
                    'Updated ownership of auction {}'.format(auction.id),
                    extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_ownership_update'}))

                return {'data': auction.serialize('view')}
