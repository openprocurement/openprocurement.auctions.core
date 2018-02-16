from schematics.exceptions import ValidationError

from openprocurement.api.utils import calculate_business_date

from openprocurement.auctions.core.plugins.contracting.v3.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD,
    PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD,
)


class ProlongationManager(object):
    """Behaviour logic of Prolongation model"""

    def __init__(self, prolongation):
        self.prolongation = prolongation

    def apply(self):
        """Choose order of prolongation and apply right"""
        self._check_documents_are_present()
        applied_prolongations_count = len([
            p for p in self.prolongation.__parent__.prolongations
            if p.status == 'applied'
        ])

        if applied_prolongations_count >= 2:
            raise Exception("Contract can be prolongated for 2 times only.")

        self.prolongation.status = 'applied'
        contract = self.prolongation.__parent__
        if applied_prolongations_count == 0:
            contract.signingPeriod.endDate = calculate_business_date(
                contract.signingPeriod.startDate,
                PROLONGATION_SHORT_PERIOD
            )
        elif applied_prolongations_count == 1:
            contract.signingPeriod.endDate = calculate_business_date(
                contract.signingPeriod.startDate,
                PROLONGATION_LONG_PERIOD
            )

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
