from schematics.exceptions import ValidationError

from openprocurement.api.utils import calculate_business_date

from openprocurement.auctions.core.plugins.\
        contracting.v3.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD,
    PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD,
)


class ProlongationManager(object):
    """Behaviour logic of Prolongation model"""

    def __init__(self, prolongation):
        self.prolongation = prolongation

    def _apply_short(self):
        """Apply short-time prolongation to related Contract instance
        """
        self.prolongation.status = 'applied'
        contract = self.prolongation.__parent__
        contract.signingPeriod.endDate = calculate_business_date(
            contract.signingPeriod.startDate,
            PROLONGATION_SHORT_PERIOD
        )

    def _apply_long(self):
        """Apply long-time prolongation to related Contract instance
        """
        self.prolongation.status = 'applied'
        contract = self.prolongation.__parent__
        contract.signingPeriod.endDate = calculate_business_date(
            contract.signingPeriod.startDate,
            PROLONGATION_LONG_PERIOD
        )

    def apply(self):
        """Choose order of prolongation and apply right"""
        self._check_documents_are_present()
        applied_prolongations_count = len([
            p for p in self.prolongation.__parent__.prolongations
            if p.status == 'applied'
        ])
        if applied_prolongations_count == 0:
            self._apply_short()
        elif applied_prolongations_count == 1:
            self._apply_long()

    def add_document(self, document):
        if self.prolongation.status == 'draft':
            self.prolongation.documents.append(document)
        else:
            raise ValidationError(
                'Document can be added only in `draft` status.'
            )

    def _check_documents_are_present(self):
        if len(self.prolongation.documents) == 0:
            raise ValidationError(
                'Prolongation must have documents to apply'
            )
