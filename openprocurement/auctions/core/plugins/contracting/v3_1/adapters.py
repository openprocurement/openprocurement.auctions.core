# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    error_handler,
)

from openprocurement.auctions.core.plugins.contracting.base.adapters import (
    BaseContractManagerAdapter,
)
from openprocurement.auctions.core.plugins.contracting.base.utils import (
    check_document_existence,
    check_auction_status
)
from openprocurement.auctions.core.plugins.contracting.v3_1.validators import (
    validate_contract_create,
    validate_contract_update,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    validate_with,
    get_related_award_of_contract,
)
from openprocurement.auctions.core.validation import (
    validate_patch_contract_data,
)


class ContractManagerV3_1Adapter(BaseContractManagerAdapter):

    name = 'Contract v-3_1 adapter'

    create_validators = (
        validate_contract_create,
    )

    change_validators = (
        validate_contract_update,
        validate_patch_contract_data,
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
        now = get_now()

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

        if request.context.status == 'pending' and 'status' in data and data['status'] == 'cancelled':
            if not (check_document_existence(request.context, 'rejectionProtocol') or
                    check_document_existence(request.context, 'act')):
                request.errors.add(
                    'body',
                    'data',
                    'Can\'t switch contract status to (cancelled) before'
                    ' auction owner load reject protocol or act'
                )
                request.errors.status = 403
                raise error_handler(request)
            if check_document_existence(request.context, 'contractSigned'):
                request.errors.add('body', 'data', 'Bidder contract for whom has already been uploaded cannot be disqualified.')
                request.errors.status = 403
                raise error_handler(request)
            award = get_related_award_of_contract(request.context, auction)
            award.signingPeriod.endDate = now
            award.complaintPeriod.endDate = now
            award.status = 'unsuccessful'
            auction.awardPeriod.endDate = None
            auction.status = 'active.qualification'
            request.content_configurator.back_to_awarding()

        if request.context.status == 'pending' and 'status' in data and data['status'] == 'active':
            award = [a for a in auction.awards if a.id == request.context.awardID][0]
            stand_still_end = award.complaintPeriod.endDate
            if stand_still_end > now:
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
            if not check_document_existence(request.context, 'contractSigned'):
                request.errors.add('body', 'data', 'Can\'t sign contract without contractSigned document')
                request.errors.status = 403
                raise error_handler(request)
            if not request.context.dateSigned:
                request.errors.add('body', 'data', 'Can\'t sign contract without specified dateSigned field')
                request.errors.status = 403
                raise error_handler(request)
        current_contract_status = request.context.status
        apply_patch(request, save=False, src=request.context.serialize())
        if current_contract_status != request.context.status and (
                current_contract_status == 'cancelled' or request.context.status == 'pending'):
            request.errors.add('body', 'data', 'Can\'t update contract status')
            request.errors.status = 403
            raise error_handler(request)
        check_auction_status(request)
