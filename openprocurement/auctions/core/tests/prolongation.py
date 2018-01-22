from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.prolongation_blanks import (
    get_prolongations_for_contract,
    get_prolongation_by_id,
    delete_prolongation_by_id,
    patch_prolongation_fields,
    apply_prolongation_short,
    apply_prolongation_long,
)


class AuctionContractProlongationResourceTestMixin(object):
    test_get_prolongations_for_contract = snitch(
        get_prolongations_for_contract
    )

    test_get_prolongation_by_id = snitch(
        get_prolongation_by_id
    )

    test_delete_prolongation_by_id = snitch(
        delete_prolongation_by_id
    )

    test_patch_prolongation_fields = snitch(
        patch_prolongation_fields
    )

    test_apply_prolongation_short = snitch(
        apply_prolongation_short
    )

    test_apply_prolongation_long = snitch(
        apply_prolongation_long
    )
