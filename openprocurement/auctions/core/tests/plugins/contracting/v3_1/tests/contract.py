from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.plugins.contracting.v3_1.tests.blanks.contract_blanks import (
    create_auction_contract,
    create_auction_contract_in_complete_status,
    get_auction_contract,
    patch_auction_contract_invalid,
    patch_auction_contract_blacklisted_fields,
    patch_auction_contract_value,
    patch_auction_contract_to_active,
    patch_auction_contract_to_active_date_signed_burst,
    patch_auction_contract_in_auction_complete_status,
    patch_auction_contract_to_cancelled_invalid_no_rejection_or_act,
    patch_auction_contract_to_cancelled_invalid_signed,
    patch_auction_contract_to_cancelled_rejection_protocol,
    patch_auction_contract_to_cancelled_act
)


class AuctionContractV3_1ResourceTestCaseMixin(object):
    test_create_auction_contract = snitch(create_auction_contract)
    test_create_auction_contract_in_complete_status = snitch(create_auction_contract_in_complete_status)
    test_get_auction_contract = snitch(get_auction_contract)
    test_patch_auction_contract_invalid = snitch(patch_auction_contract_invalid)
    test_patch_auction_contract_blacklisted_fields = snitch(patch_auction_contract_blacklisted_fields)
    test_patch_auction_contract_value = snitch(patch_auction_contract_value)
    test_patch_auction_contract_to_active = snitch(patch_auction_contract_to_active)
    test_patch_auction_contract_to_active_date_signed_burst = snitch(patch_auction_contract_to_active_date_signed_burst)
    test_patch_auction_contract_in_auction_complete_status = snitch(patch_auction_contract_in_auction_complete_status)
    test_patch_auction_contract_to_cancelled_invalid_no_rejection_or_act = snitch(
        patch_auction_contract_to_cancelled_invalid_no_rejection_or_act
    )
    test_patch_auction_contract_to_cancelled_invalid_signed = snitch(patch_auction_contract_to_cancelled_invalid_signed)
    test_patch_auction_contract_to_cancelled_rejection_protocol = snitch(
        patch_auction_contract_to_cancelled_rejection_protocol
    )
    test_patch_auction_contract_to_cancelled_act = snitch(patch_auction_contract_to_cancelled_act)
