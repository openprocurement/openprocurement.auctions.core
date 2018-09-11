# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    error_handler,
    validate_with,
)
from openprocurement.auctions.core.plugins.contracting.base.adapters import (
    BaseContractManagerAdapter
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    check_auction_status,
)
from openprocurement.auctions.core.validation import (
    validate_patch_contract_data
)


class ContractManagerV2Adapter(BaseContractManagerAdapter):

    name = 'Contract v-2 adapter'

    change_validators = (
        validate_patch_contract_data,
    )

    def create_contract(self, request, **kwargs):
        auction = request.validated['auction']
        if auction.status not in ['active.qualification', 'active.awarded']:
            request.errors.add('body', 'data', 'Can\'t add contract in current ({}) auction status'.format(auction.status))
            request.errors.status = 403
            raise error_handler(request)
        contract = request.validated['contract']
        auction.contracts.append(contract)

    @validate_with(change_validators)
    def change_contract(self, request, **kwargs):
        context = kwargs['context']

        if request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
            request.errors.add('body', 'data', 'Can\'t update contract in current ({}) auction status'.format(request.validated['auction_status']))
            request.errors.status = 403
            raise error_handler(request)
        auction = request.validated['auction']
        if any([i.status != 'active' for i in auction.lots if i.id in [a.lotID for a in auction.awards if a.id == request.context.awardID]]):
            request.errors.add('body', 'data', 'Can update contract only in active lot status')
            request.errors.status = 403
            raise error_handler(request)
        data = request.validated['data']

        if data['value']:
            for ro_attr in ('valueAddedTaxIncluded', 'currency'):
                if data['value'][ro_attr] != getattr(context.value, ro_attr):
                    request.errors.add('body', 'data', 'Can\'t update {} for contract value'.format(ro_attr))
                    request.errors.status = 403
                    raise error_handler(request)

            award = [a for a in auction.awards if a.id == request.context.awardID][0]
            if data['value']['amount'] < award.value.amount:
                request.errors.add('body', 'data', 'Value amount should be greater or equal to awarded amount ({})'.format(award.value.amount))
                request.errors.status = 403
                raise error_handler(request)

        if request.context.status != 'active' and 'status' in data and data['status'] == 'active':
            award = [a for a in auction.awards if a.id == request.context.awardID][0]
            stand_still_end = award.complaintPeriod.endDate
            if stand_still_end > get_now():
                request.errors.add('body', 'data', 'Can\'t sign contract before stand-still period end ({})'.format(stand_still_end.isoformat()))
                request.errors.status = 403
                raise error_handler(request)
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
                request.errors.add('body', 'data', 'Can\'t sign contract before reviewing all complaints')
                request.errors.status = 403
                raise error_handler(request)
            if not request.context.documents:
                request.errors.add('body', 'data', 'Cant\'t sign contract without document')
                request.errors.status = 403
                raise error_handler(request)
        contract_status = request.context.status
        apply_patch(request, save=False, src=request.context.serialize())
        if contract_status != request.context.status and (contract_status != 'pending' or request.context.status != 'active'):
            request.errors.add('body', 'data', 'Can\'t update contract status')
            request.errors.status = 403
            raise error_handler(request)
        if request.context.status == 'active' and not request.context.dateSigned:
            request.context.dateSigned = get_now()
        check_auction_status(request)
