from schematics.exceptions import ValidationError

from openprocurement.api.utils import calculate_business_date

from openprocurement.auctions.core.models import get_auction
from openprocurement.auctions.core.plugins.contracting.v3.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD
)


class ProlongationManager(object):
    """Behaviour logic of Prolongation model"""

    def __init__(self, prolongation):
        self.prolongation = prolongation

    def apply(self):
        """Choose order of prolongation and apply right"""
        self._check_documents_are_present()
        auction = get_auction(self.prolongation)
        contract = self.prolongation.__parent__
        applied_prolongations_count = len([
            p for p in contract.prolongations
            if p.status == 'applied'
        ])

        if applied_prolongations_count >= 2:
            raise Exception("Contract can be prolongated for 2 times only.")

        self.prolongation.status = 'applied'
        prolongation_period = (
            PROLONGATION_LONG_PERIOD if applied_prolongations_count else PROLONGATION_SHORT_PERIOD
        )
        contract.signingPeriod.endDate = calculate_business_date(
            contract.signingPeriod.startDate,
            prolongation_period,
            context=auction
        )

    def _check_documents_are_present(self):
        if len(self.prolongation.documents) == 0:
            raise ValidationError(
                'Prolongation must have documents to apply'
            )
