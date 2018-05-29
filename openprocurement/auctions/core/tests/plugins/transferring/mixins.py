from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.plugins.transferring.blanks.resource_blanks import (
    change_resource_ownership,
    resource_location_in_transfer,
    already_applied_transfer,
    half_applied_transfer,
    new_owner_can_change,
    broker_not_accreditation_level,
    level_permis,
    switch_mode
)

class AuctionOwnershipChangeTestCaseMixin(object):

    test_change_resource_ownership = snitch(change_resource_ownership)
    test_resource_location_in_transfer = snitch(resource_location_in_transfer)
    test_already_applied_transfer = snitch(already_applied_transfer)
    test_half_applied_transfer = snitch(half_applied_transfer)
    test_new_owner_can_change = snitch(new_owner_can_change)
    test_broker_not_accreditation_level = snitch(broker_not_accreditation_level)
    test_level_test_permis = snitch(level_permis)
    test_mode_test = snitch(switch_mode)
