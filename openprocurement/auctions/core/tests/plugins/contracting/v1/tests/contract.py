import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.plugins.contracting.v1.tests.blanks.contract_blanks import (
    create_auction_contract,
    create_auction_contract_in_complete_status,
    get_auction_contract,
)


class AuctionContractV1ResourceTestCaseMixin(object):
    test_create_auction_contract = unittest.skip('option not available')(
        snitch(create_auction_contract))
    test_create_auction_contract_in_complete_status = unittest.skip('option not available')(
        snitch(create_auction_contract_in_complete_status)
    )
    test_get_auction_contract = snitch(get_auction_contract)
