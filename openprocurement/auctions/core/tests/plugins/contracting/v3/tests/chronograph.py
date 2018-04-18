from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.plugins.contracting.v3.tests.blanks.chronograph_blanks import (
    contract_signing_period_switch_to_qualification,
    contract_signing_period_switch_to_complete,
)


class AuctionContractSwitchTestMixin(object):
    test_contract_signing_period_switch_to_qualification = snitch(
        contract_signing_period_switch_to_qualification
    )

    test_contract_signing_period_switch_to_complete = snitch(
        contract_signing_period_switch_to_complete
    )
