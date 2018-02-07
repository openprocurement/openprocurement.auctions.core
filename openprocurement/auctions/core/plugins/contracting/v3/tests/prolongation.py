from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.prolongation_blanks import (
    get_prolongations_for_contract,
    get_prolongation_by_id,
    patch_prolongation_fields,
    apply_prolongation_short,
    apply_prolongation_long,
    upload_document,
    get_document,
    get_list_of_documents,
    patch_document,
    apply_prolongation_triple_times,
    apply_applied_prolongation,
    create_applied_prolongation,
)


class AuctionContractProlongationResourceTestMixin(object):
    test_get_prolongations_for_contract = snitch(
        get_prolongations_for_contract
    )

    test_get_prolongation_by_id = snitch(
        get_prolongation_by_id
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

    test_upload_document = snitch(
        upload_document
    )

    test_get_document = snitch(
        get_document
    )

    test_get_list_of_documents = snitch(
        get_list_of_documents
    )

    test_patch_document = snitch(
        patch_document
    )
    
    test_apply_prolongation_triple_times = snitch(
        apply_prolongation_triple_times
    )

    test_apply_applied_prolongation = snitch(
        apply_applied_prolongation
    )

    test_create_applied_prolongation = snitch(
        create_applied_prolongation
    )
