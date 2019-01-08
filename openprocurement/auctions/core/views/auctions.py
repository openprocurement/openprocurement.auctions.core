# -*- coding: utf-8 -*-

from openprocurement.api.utils import get_now
from openprocurement.api.utils import (
    context_unpack,
    set_ownership,
    decrypt,
    encrypt,
    generate_id,
    json_view,
    APIResource,
    APIResourceListing
)

from openprocurement.auctions.core.design import (
    FIELDS,
    auctions_by_dateModified_view,
    auctions_real_by_dateModified_view,
    auctions_test_by_dateModified_view,
    auctions_by_local_seq_view,
    auctions_real_by_local_seq_view,
    auctions_test_by_local_seq_view,
)
from openprocurement.auctions.core.interfaces import (
    IAuctionManager
)
from openprocurement.auctions.core.utils import (
    generate_auction_id,
    save_auction,
    auction_serialize,
    opresource,
    get_auction_route_name)
from openprocurement.auctions.core.validation import validate_auction_data


VIEW_MAP = {
    u'': auctions_real_by_dateModified_view,
    u'test': auctions_test_by_dateModified_view,
    u'_all_': auctions_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    u'': auctions_real_by_local_seq_view,
    u'test': auctions_test_by_local_seq_view,
    u'_all_': auctions_by_local_seq_view,
}
FEED = {
    u'dateModified': VIEW_MAP,
    u'changes': CHANGES_VIEW_MAP,
}


@opresource(name='Auctions',
            path='/auctions',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#auction for more info")
class AuctionsResource(APIResourceListing):

    def __init__(self, request, context):
        super(AuctionsResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = auction_serialize
        self.object_name_for_listing = 'Auctions'
        self.log_message_id = 'auction_list_custom'

    @json_view(content_type="application/json", permission='create_auction', validators=(validate_auction_data,))
    def post(self):
        """This API request is targeted to creating new Auctions by procuring organizations.
        """
        auction = self.request.validated['auction']

        if auction['_internal_type'] == 'geb':
            manager = self.request.registry.queryMultiAdapter((self.request, auction), IAuctionManager)
            applicant = self.request.validated['auction']
            auction = manager.create(applicant)
            if not auction:
                return
            manager.initialize(manager.context.status)
        else:
            self.request.registry.getAdapter(auction, IAuctionManager).create_auction(self.request)
            auction_id = generate_id()
            auction.id = auction_id
            auction.auctionID = generate_auction_id(get_now(), self.db, self.server_id)
            if hasattr(auction, "initialize"):
                auction.initialize()
            status = self.request.json_body['data'].get('status')
            if status and status in ['draft', 'pending.verification']:
                auction.status = status
        acc = set_ownership(auction, self.request)
        self.request.validated['auction'] = auction
        self.request.validated['auction_src'] = {}
        if save_auction(self.request):
            self.LOGGER.info('Created auction {} ({})'.format(auction['id'], auction.auctionID),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_create'}, {'auction_id': auction['id'], 'auctionID': auction.auctionID}))
            self.request.response.status = 201
            auction_route_name = get_auction_route_name(self.request, auction)
            self.request.response.headers['Location'] = self.request.route_url(route_name=auction_route_name, auction_id=auction['id'])
            return {'data': auction.serialize(auction.status), 'access': acc}
