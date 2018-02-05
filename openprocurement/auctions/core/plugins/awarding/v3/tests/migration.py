from openprocurement.auctions.core.tests.base import snitch

from .blanks.migration_blanks import (
    migrate_pendingVerification_pending,
    migrate_pendingPayment_active,
    migrate_contract_cancelled,
    migrate_contract_pending
)


class MigrateAwardingV2toV3Mixin(object):
    test_migrate_pendingVerification_pending = snitch(
        migrate_pendingVerification_pending
    )
    test_migrate_pendingPayment_active = snitch(
        migrate_pendingPayment_active
    )
    test_migrate_contract_cancelled = snitch(
        migrate_contract_cancelled
    )
    test_migrate_contract_pending = snitch(
        migrate_contract_pending
    )
