# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    save_auction,
    opresource,
)
from openprocurement.auctions.core.validation import (
    validate_prolongation_data,
    validate_patch_prolongation_data,
)
from openprocurement.auctions.core.plugins.contracting.v3.models import(
    Prolongation
)
from openprocurement.auctions.core.plugins.contracting.v3.utils.prolongation import (
    ProlongationManager
)


@opresource(
    name='awarding_3_0:Auction Prolongation',
    collection_path='/auctions/{auction_id}/contracts/{contract_id}/prolongations',
    path='/auctions/{auction_id}/contracts/{contract_id}/prolongations/{prolongation_id}',
    awardingType='awarding_3_0',
    description=" Auction prolongations"
)
class AuctionAwardContractProlongationResource(APIResource):

    @json_view(
        content_type="application/json",
        permission='create_contract',
        validators=(validate_prolongation_data,)
    )
    def collection_post(self):
        """Create prolongation for a Contract"""
        auction = self.request.validated['auction']
        contract = self.request.validated['contract']

        new_prolongation = self.request.validated['prolongation']
        contract.prolongations.append(new_prolongation)

        if save_auction(self.request):
            self.LOGGER.info(
                'Created auction contract prolongation with ID {0}'.format(new_prolongation.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'contract_prolongation_create'},
                    {'prolongation_id': new_prolongation.id}
                ),
            )
            self.request.response.status = 201
            
            self.request.response.headers['Location'] = self.request.current_route_url(
                    _route_name=self.request.matched_route.name,
                    contract_id=contract.id,
                    _query={}
                )
            return {'data': new_prolongation.serialize()}

    @json_view(permission='view_auction')
    def collection_get(self):
        """List prolongations for contract"""
        return {
            'data': [
                i.serialize() for i in self.request.context.prolongations
            ]
        }

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the contract for award"""
        return {'data': self.request.validated['prolongation'].serialize()}

    @json_view(
        content_type="application/json",
        permission='edit_auction',
        validators=(validate_patch_prolongation_data,)
    )
    def patch(self):
        """Update of prolongation
            
            Fields, except on `status`, can be updated only when
            Prolongation has status `draft`.
        """
        old_prolongation = self.request.context
        new_status = self.request.validated['data'].get('status')

        is_status_change = (new_status != old_prolongation.status)

        if not is_status_change and old_prolongation.status == 'draft':
            apply_patch(self.request) # apply patch only in `draft`
        if new_status == 'applied':
            # this method checks intention of long apply
            managed_prolongation = ProlongationManager(old_prolongation)
            try:
                managed_prolongation.apply()
            except Exception as e:
                self.request.errors.add('body', 'data', e.message)
                self.request.errors.status = 403
                return
            save_auction(self.request)

        self.LOGGER.info(
            'Updated prolongation {}'.format(
                self.request.context.id
            ),
            extra=context_unpack(
                self.request,
                {'MESSAGE_ID': 'contract_prolongation_patch'}
                )
            )
        return {'data': self.request.context.serialize()}

