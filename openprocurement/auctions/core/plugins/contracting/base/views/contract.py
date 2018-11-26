# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.auctions.core.endpoints import ENDPOINTS
from openprocurement.auctions.core.plugins.contracting.base.interfaces import (
    IContractManagerAdapter
)
from openprocurement.auctions.core.utils import (
    save_auction,
    opresource,
)
from openprocurement.auctions.core.validation import (
    validate_contract_data,
)


@opresource(name='Auction Contracts',
            collection_path=ENDPOINTS['contracts'],
            path=ENDPOINTS['contract'],
            description="Auction contracts")
class BaseAuctionAwardContractResource(APIResource):

    @json_view(content_type="application/json", permission='create_contract',
               validators=(validate_contract_data,))
    def collection_post(self):
        """Post a contract for award
        """
        contract = self.request.validated['contract']
        contract_manager = self.request.registry.getAdapter(contract, IContractManagerAdapter)
        contract_manager.create_contract(self.request)

        if save_auction(self.request):
            self.LOGGER.info(
                'Created auction contract {}'.format(contract.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'auction_contract_create'},
                    {'contract_id': contract.id}
                )
            )
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(
                _route_name=route, contract_id=contract.id, _query={}
            )
            return {'data': contract.serialize()}

    @json_view(permission='view_auction')
    def collection_get(self):
        """List contracts for award
        """
        return {'data': [i.serialize() for i in self.request.context.contracts]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the contract for award
        """
        return {'data': self.request.validated['contract'].serialize()}

    @json_view(content_type="application/json", permission='edit_auction')
    def patch(self):
        """Update of contract
        """
        contract = self.request.context
        contract_manager = self.request.registry.getAdapter(contract, IContractManagerAdapter)
        contract_manager.change_contract(self.request, context=self.context)
        self.request.auction.modified = True

        if save_auction(self.request):
            self.LOGGER.info(
                'Updated auction contract {}'.format(self.request.context.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'auction_contract_patch'}
                )
            )
            return {'data': self.request.context.serialize()}
