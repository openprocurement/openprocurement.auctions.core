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
from openprocurement.auctions.core.plugins.contracting.v2.utils import (
    check_auction_status,
)
from openprocurement.auctions.core.validation import (
    validate_contract_data,
    validate_patch_contract_data,
)


@opresource(
    name='dgfInsider:Auction Contracts',
    collection_path='/auctions/{auction_id}/contracts',
    path='/auctions/{auction_id}/contracts/{contract_id}',
    auctionsprocurementMethodType="dgfInsider",
    description="Insider auction contracts"
)
@opresource(
    name='dgfOtherAssets:Auction Contracts',
    collection_path='/auctions/{auction_id}/contracts',
    path='/auctions/{auction_id}/contracts/{contract_id}',
    auctionsprocurementMethodType="dgfOtherAssets",
    description="Auction contracts"
)
@opresource(
    name='dgfFinancialAssets:Auction Contracts',
    collection_path='/auctions/{auction_id}/contracts',
    path='/auctions/{auction_id}/contracts/{contract_id}',
    auctionsprocurementMethodType="dgfFinancialAssets",
    description=" Financial auction contracts"
)
class BaseAuctionAwardContractResource(APIResource):

    @json_view(content_type="application/json", permission='create_contract', validators=(validate_contract_data,))
    def collection_post(self):
        """Post a contract for award
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t add contract in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        contract = self.request.validated['contract']
        auction.contracts.append(contract)
        if save_auction(self.request):
            self.LOGGER.info('Created auction contract {}'.format(contract.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_contract_create'}, {'contract_id': contract.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route, contract_id=contract.id, _query={})
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

    @json_view(content_type="application/json", permission='edit_auction', validators=(validate_patch_contract_data,))
    def patch(self):
        """Update of contract
        """
        if self.request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update contract in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        auction = self.request.validated['auction']
        if any([i.status != 'active' for i in auction.lots if i.id in [a.lotID for a in auction.awards if a.id == self.request.context.awardID]]):
            self.request.errors.add('body', 'data', 'Can update contract only in active lot status')
            self.request.errors.status = 403
            return
        data = self.request.validated['data']

        if data['value']:
            for ro_attr in ('valueAddedTaxIncluded', 'currency'):
                if data['value'][ro_attr] != getattr(self.context.value, ro_attr):
                    self.request.errors.add('body', 'data', 'Can\'t update {} for contract value'.format(ro_attr))
                    self.request.errors.status = 403
                    return

            award = [a for a in auction.awards if a.id == self.request.context.awardID][0]
            if data['value']['amount'] < award.value.amount:
                self.request.errors.add('body', 'data', 'Value amount should be greater or equal to awarded amount ({})'.format(award.value.amount))
                self.request.errors.status = 403
                return

        if self.request.context.status != 'active' and 'status' in data and data['status'] == 'active':
            award = [a for a in auction.awards if a.id == self.request.context.awardID][0]
            stand_still_end = award.complaintPeriod.endDate
            if stand_still_end > get_now():
                self.request.errors.add('body', 'data', 'Can\'t sign contract before stand-still period end ({})'.format(stand_still_end.isoformat()))
                self.request.errors.status = 403
                return
            pending_complaints = [
                i
                for i in auction.complaints
                if i.status in ['claim', 'answered', 'pending'] and i.relatedLot in [None, award.lotID]
            ]
            pending_awards_complaints = [
                i
                for a in auction.awards
                for i in a.complaints
                if i.status in ['claim', 'answered', 'pending'] and a.lotID == award.lotID
            ]
            if pending_complaints or pending_awards_complaints:
                self.request.errors.add('body', 'data', 'Can\'t sign contract before reviewing all complaints')
                self.request.errors.status = 403
                return
            if not self.request.context.documents:
                self.request.errors.add('body', 'data', 'Cant\'t sign contract without document')
                self.request.errors.status = 403
                return
        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if contract_status != self.request.context.status and (contract_status != 'pending' or self.request.context.status != 'active'):
            self.request.errors.add('body', 'data', 'Can\'t update contract status')
            self.request.errors.status = 403
            return
        if self.request.context.status == 'active' and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_auction_status(self.request)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction contract {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_contract_patch'}))
            return {'data': self.request.context.serialize()}

