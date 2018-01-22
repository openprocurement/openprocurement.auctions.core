from datetime import datetime, timedelta
from schematics.exceptions import ValidationError

from openprocurement.auctions.core.tests.base import BaseWebTest
from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Contract,
    Prolongation,
)
from openprocurement.auctions.core.constants import (
    PROLONGATION_SHORT_PERIOD,
    PROLONGATION_LONG_PERIOD,
    PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD,
)
from openprocurement.api.models import Period
from openprocurement.api.utils import calculate_business_date

contract_data = {
    'awardID': '774f344a615692604de040918a72b149'  # random md5
}


class TestContractingV3Prolongation(BaseWebTest):

    def fixture_required_data(self):
        return {
            'decisionID': 'very_importante_documente',
            'description': 'Prolongate your contract for free!',
            'reason': 'other',
            'documents': [],
        }

    def fixture_created(self):
        contract = Contract(contract_data)
        contract.signingPeriod = Period({
            'startDate': '2000-01-01T10:00:00+02:00',
            'endDate': '2000-01-10T10:00:00+02:00'
        })
        prolongation = Prolongation(self.fixture_required_data())
        prolongation.attach_to_contract(contract)
        prolongation.__parent__ = contract  # mock
        return (contract, prolongation)

    def test_attach_to_contract(self):
        contract = Contract(contract_data)

        self.assertEqual(contract.prolongations, list())
        prolongation = Prolongation(self.fixture_required_data())
        prolongation.attach_to_contract(contract)

        self.assertIn(prolongation, contract.prolongations)

    def test_date_created(self):
        contract, prolongation = self.fixture_created()
        self.assertNotEqual(
            prolongation.dateCreated,
            None
        )
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

    def test_datePublished_protection(self):
        contract, prolongation = self.fixture_created()

        prolongation.datePublished = datetime(2000, 1, 1)
        fields_awailable_for_creation = prolongation.serialize('create')
        self.assertNotIn(
            'datePublished',
            fields_awailable_for_creation,
            'datePublished cannot be set with `create` role'
        )

        fields_awailable_for_edit = prolongation.serialize('edit')
        self.assertNotIn(
            'datePublished',
            fields_awailable_for_edit,
            'datePublished cannot be set with `edit` role'
        )

    def test_datePublished_validation(self):
        contract, prolongation = self.fixture_created()

        prolongation.dateCreated = datetime(2000, 1, 1)
        prolongation.datePublished =\
            prolongation.dateCreated -\
            PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD +\
            timedelta(days=1)
        prolongation.validate()

        prolongation.datePublished =\
            prolongation.dateCreated -\
            PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD -\
            timedelta(days=1)
        with self.assertRaises(ValidationError) as context:  # noqa: F841
            prolongation.validate()

    def test_delete(self):
        contract, prolongation = self.fixture_created()

        prolongation.delete()
        assert contract.prolongations[0].status == \
            prolongation.status == \
            'deleted'

    def test_delete_when_applied(self):
        contract, prolongation = self.fixture_created()
        prolongation.status = 'applied'
        with self.assertRaises(Exception) as context:  # noqa: F841
            prolongation.delete()

    def test_apply_short(self):
        contract, prolongation = self.fixture_created()
        pre_prolongation_contract_signingPeriod = contract.signingPeriod

        target_signingPeriod_endDate = calculate_business_date(
            contract.signingPeriod.startDate,
            PROLONGATION_SHORT_PERIOD
        )
        prolongation._apply_short()

        self.assertEqual(
            prolongation.status,
            'applied'
        )

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
            PROLONGATION_LONG_PERIOD
        )

        previous_short_prolongation = self.fixture_created()[0]
        previous_short_prolongation.status = 'applied'
        contract.prolongations.append(previous_short_prolongation)
        prolongation._apply_long(previous_short_prolongation)
        self.assertEqual(
            previous_short_prolongation.status,
            'deleted'
        )

        self.assertEqual(
            prolongation.status,
            'applied'
        )

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

        prolongation.apply()

        self.assertEqual(
            prolongation.status,
            'applied'
        )

    def test_apply_when_need_to_apply_long(self):
        contract, prolongation = self.fixture_created()
        previous_applied_prolongation = self.fixture_created()[0]
        contract.prolongations.append(previous_applied_prolongation)
        previous_applied_prolongation.status = 'applied'

        self.assertEqual(
            prolongation.status,
            'draft'
        )

        prolongation.apply()

        self.assertEqual(
            prolongation.status,
            'applied'
        )
        self.assertEqual(
            previous_applied_prolongation.status,
            'deleted'
        )


class TestContractingV3Contract(BaseWebTest):

    def test_datePaid_good_date(self):
        start_of_signing_period = datetime(2000, 1, 1)
        end_of_signing_period = datetime(2000, 1, 10)
        good_datepaid1 = datetime(1999, 12, 31)
        good_datepaid2 = datetime(2000, 1, 1)
        period = Period()

        period.startDate = start_of_signing_period
        period.endDate = end_of_signing_period

        contract = Contract(contract_data)
        contract.signingPeriod = period
        period.validate()

        contract.datePaid = good_datepaid1
        contract.validate()
        # datePaid must be not greater than start of signingPeriod
        contract.datePaid = good_datepaid2
        contract.validate()

    def test_datePaid_wrong_date(self):
        contract = Contract(contract_data)
        period = Period()
        period.startDate = datetime(2000, 1, 1)
        period.endDate = datetime(2000, 1, 10)
        contract.signingPeriod = period
        self.db.commit()
        with self.assertRaises(ValidationError) as context:  # noqa: F841
            contract.datePaid = datetime(2000, 1, 5)
            contract.validate()

    def test_datePaid_when_signingPeriod_None(self):
        contract = Contract(contract_data)
        period = Period()
        period.startDate = datetime(2000, 1, 1)
        period.endDate = datetime(2000, 1, 10)
        contract.signingPeriod = period
        contract.datePaid = None
        contract.validate()
