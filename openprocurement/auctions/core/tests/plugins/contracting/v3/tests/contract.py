import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.plugins.contracting.v3.tests.blanks.contract_blanks import (
    create_auction_contract,
    create_auction_contract_in_complete_status,
    get_auction_contract,
    patch_signing_period,
    patch_date_paid,
)


class AuctionContractV3ResourceTestCaseMixin(object):
    test_create_auction_contract = unittest.skip('option not available')(snitch(create_auction_contract))
    test_create_auction_contract_in_complete_status = unittest.skip('option not available')(
        snitch(create_auction_contract_in_complete_status)
    )
    test_get_auction_contract = snitch(get_auction_contract)
    test_patch_signing_period = snitch(patch_signing_period)
    test_patch_date_paid = snitch(patch_date_paid)
