# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    error_handler,
    validate_with,
)

from openprocurement.auctions.core.plugins.contracting.base.adapters import (
    BaseContractManagerAdapter
)
from openprocurement.auctions.core.plugins.contracting.v2_1.validators import (
    validate_contract_create,
    validate_contract_update,
)
from openprocurement.auctions.core.utils import (
    check_auction_status,
    apply_patch,
)
from openprocurement.auctions.core.validation import (
    validate_patch_contract_data
)


class ContractManagerV2_1Adapter(BaseContractManagerAdapter):

    name = 'Contract v-2_1 adapter'

    create_validators = (
        validate_contract_create,
    )

    change_validators = (
        validate_patch_contract_data,
        validate_contract_update
    )

    @validate_with(create_validators)
    def create_contract(self, request, **kwargs):
        auction = request.validated['auction']
        contract = request.validated['contract']
        auction.contracts.append(contract)

    @validate_with(change_validators)
    def change_contract(self, request, **kwargs):
        context = kwargs['context']

        auction = request.validated['auction']
        data = request.validated['data']

        if data.get('value'):
            award = [a for a in auction.awards if a.id == request.context.awardID][0]
            for ro_attr in ('valueAddedTaxIncluded', 'currency'):
                if data['value'][ro_attr] != getattr(award.value, ro_attr):
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
            if not (
                data.get('value')  # there's value passed
                or context.value is not None  # there's value defined
            ):
                request.errors.add('body', 'data', 'Can\'t activate contract without value defined')
                request.errors.status = 403
                raise error_handler(request)

        current_contract_status = request.context.status
        apply_patch(request, save=False, src=request.context.serialize())
        if current_contract_status != request.context.status and (
                current_contract_status != 'pending' or request.context.status != 'active'):
            request.errors.add('body', 'data', 'Can\'t update contract status')
            request.errors.status = 403
            raise error_handler(request)
        if request.context.status == 'active' and not request.context.dateSigned:
            request.context.dateSigned = get_now()
        check_auction_status(request)
