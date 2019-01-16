# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    validate_with,
)

from openprocurement.auctions.core.plugins.contracting.base.adapters import (
    BaseContractManagerAdapter,
)
from openprocurement.auctions.core.plugins.contracting.base.utils import (
    check_auction_status
)
from openprocurement.auctions.core.plugins.contracting.v3_1.validators import (
    validate_contract_create,
    validate_contract_update,
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

        request.context.contract_extender.change_contract_extender(request=request, **kwargs)

        check_auction_status(request)
