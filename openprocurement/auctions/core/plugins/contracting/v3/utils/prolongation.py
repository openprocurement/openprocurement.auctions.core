from schematics.exceptions import ValidationError

from openprocurement.api.utils import calculate_business_date

from openprocurement.auctions.core.models import get_auction
from openprocurement.auctions.core.plugins.contracting.v3.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD,
    CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
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
            auction,
            working_days=True,
            specific_hour=CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
        )

    def _check_documents_are_present(self):
        if not self.prolongation.documents:
            raise ValidationError(
                'Prolongation must have documents to apply'
            )
