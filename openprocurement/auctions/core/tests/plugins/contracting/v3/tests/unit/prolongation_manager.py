import os

from uuid import uuid4
from datetime import datetime, timedelta
from schematics.exceptions import ValidationError
from zope.interface import implementer

from openprocurement.api.models.common import Period
from openprocurement.api.utils import calculate_business_date, set_specific_hour

from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.core.tests.base import BaseWebTest
from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Contract,
    Prolongation,
    ProlongationDocument,
)
from openprocurement.auctions.core.plugins.contracting.v3.utils.prolongation import (
    ProlongationManager
)
from openprocurement.auctions.core.plugins.contracting.v3.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD,
    PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD,
    CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
)

contract_data = {'awardID': uuid4().hex}


class TestContractingV3ProlongationManager(BaseWebTest):

    def fixture_required_data(self):
        return {
            'decisionID': 'very_importante_documente',
            'description': 'Prolongate your contract for free!',
            'reason': 'other',
            'documents': [],
        }

    def fixture_document(self):
        doc_data = {
            'title': 'TestDoc',
            'url': 'https://d.com/some_id',
            'format': 'application/msword',
        }
        prolongation_doc = ProlongationDocument(doc_data)
        return prolongation_doc

    def fixture_auction(self):
        @implementer(IAuction)
        class MockAuction(object):
            """Auction mock for sandbox mode compatibility
            """
            def __init__(self):
                if os.environ.get('SANDBOX_MODE'):
                    self.procurementMethodDetails = 'quick, accelerator=1440'

            def __contains__(self, item):
                if item in dir(self):
                    return True

            def __getitem__(self, key):
                return getattr(self, key, None)

        return MockAuction()

    def fixture_created(self):
        contract = Contract(contract_data)
        contract.__parent__ = self.fixture_auction()
        contract.signingPeriod = Period({
            'startDate': '2000-01-01T10:00:00+02:00',
            'endDate': '2000-01-10T10:00:00+02:00'
        })

        prolongation = Prolongation(self.fixture_required_data())
        contract.prolongations.append(contract)
        prolongation.__parent__ = contract  # mock

        prolongation_doc = self.fixture_document()
        prolongation_doc.__parent__ = prolongation
        prolongation.documents.append(prolongation_doc)
        return (contract, prolongation)

    def test_date_created(self):
        contract, prolongation = self.fixture_created()
        self.assertNotEqual(prolongation.dateCreated, None)
        fields_awailable_for_creation = prolongation.serialize('create')
        self.assertNotIn(
            'dateCreated',
            fields_awailable_for_creation,
            'dateCreated cannot be set with `create` role'
        )

        fields_awailable_for_edit = prolongation.serialize('edit')
        self.assertNotIn(
            'dateCreated',
            fields_awailable_for_edit,
            'dateCreated cannot be set with `edit` role'
        )

    def test_datePublished_validation(self):
        contract, prolongation = self.fixture_created()

        prolongation.dateCreated = datetime(2000, 1, 1)
        prolongation.datePublished = prolongation.dateCreated - PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD + timedelta(days=1)
        prolongation.validate()

        prolongation.datePublished = prolongation.dateCreated - PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD - timedelta(days=1)
        with self.assertRaises(ValidationError) as context:  # noqa: F841
            prolongation.validate()

    def test_delete_when_applied(self):
        contract, prolongation = self.fixture_created()
        prolongation.status = 'applied'

        managed_prolongation = ProlongationManager(prolongation)
        with self.assertRaises(Exception) as context:  # noqa: F841
            managed_prolongation.delete()

    def test_apply_short(self):
        contract, prolongation = self.fixture_created()
        pre_prolongation_contract_signingPeriod = contract.signingPeriod

        target_signingPeriod_endDate = calculate_business_date(
            contract.signingPeriod.startDate,
            PROLONGATION_SHORT_PERIOD,
            context=contract.__parent__,
            working_days=True,
            specific_hour=CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
        )
        managed_prolongation = ProlongationManager(prolongation)
        managed_prolongation.apply()

        self.assertEqual(prolongation.status, 'applied')

        # check update of startDate
        self.assertEqual(
            contract.signingPeriod.startDate,
            pre_prolongation_contract_signingPeriod.startDate,
            'startDate of Contract is incorrect'
        )
        # check update of endDate
        self.assertEqual(
            contract.signingPeriod.endDate,
            target_signingPeriod_endDate,
            'endDate of Contract is incorrect'
        )

    def test_apply_long(self):
        contract, prolongation = self.fixture_created()
        pre_prolongation_contract_signingPeriod = contract.signingPeriod

        target_signingPeriod_endDate = calculate_business_date(
            contract.signingPeriod.startDate,
            PROLONGATION_LONG_PERIOD,
            context=contract.__parent__,
            working_days=True,
            specific_hour=CONTRACT_SIGNING_PERIOD_END_DATE_HOUR
        )

        previous_short_prolongation = self.fixture_created()[0]
        previous_short_prolongation.status = 'applied'
        contract.prolongations.append(previous_short_prolongation)

        managed_prolongation = ProlongationManager(prolongation)
        managed_prolongation.apply()
        self.assertEqual(previous_short_prolongation.status, 'applied')

        self.assertEqual(prolongation.status, 'applied')

        # check update of startDate
        self.assertEqual(
            contract.signingPeriod.startDate,
            pre_prolongation_contract_signingPeriod.startDate,
            'startDate of Contract is incorrect'
        )
        # check update of endDate
        self.assertEqual(
            contract.signingPeriod.endDate,
            target_signingPeriod_endDate,
            'endDate of Contract is incorrect',
        )

    def test_apply_when_need_to_apply_short(self):
        contract, prolongation = self.fixture_created()

        managed_prolongation = ProlongationManager(prolongation)
        managed_prolongation.apply()

        self.assertEqual(prolongation.status, 'applied')

    def test_apply_when_need_to_apply_long(self):
        contract, prolongation = self.fixture_created()
        previous_applied_prolongation = self.fixture_created()[0]
        contract.prolongations.append(previous_applied_prolongation)
        previous_applied_prolongation.status = 'applied'

        self.assertEqual(prolongation.status, 'draft')

        managed_prolongation = ProlongationManager(prolongation)
        managed_prolongation.apply()

        self.assertEqual(prolongation.status, 'applied')
        self.assertEqual(previous_applied_prolongation.status, 'applied')

    def test_apply_without_documents(self):
        contract, prolongation = self.fixture_created()

        prolongation.documents = []
        managed_prolongation = ProlongationManager(prolongation)
        with self.assertRaises(ValidationError) as context:
            managed_prolongation.apply()
