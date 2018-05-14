from uuid import uuid4
from datetime import datetime

from schematics.exceptions import ValidationError

from openprocurement.api.models.common import Period

from openprocurement.auctions.core.tests.base import BaseWebTest
from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Contract,
)

contract_data = {'awardID': uuid4().hex}


class TestContractingV3ContractValidation(BaseWebTest):

    def test_datePaid_good_date(self):
        start_of_signing_period = datetime(2000, 1, 1)
        end_of_signing_period = datetime(2000, 1, 10)
        good_datepaid1 = datetime(2000, 1, 5)
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
        with self.assertRaises(ValidationError) as _:  # noqa: F841
            contract.datePaid = datetime(1999, 12, 30)
            contract.validate()

    def test_datePaid_when_signingPeriod_None(self):
        contract = Contract(contract_data)
        period = Period()
        period.startDate = datetime(2000, 1, 1)
        period.endDate = datetime(2000, 1, 10)
        contract.signingPeriod = period
        contract.datePaid = None
        contract.validate()
