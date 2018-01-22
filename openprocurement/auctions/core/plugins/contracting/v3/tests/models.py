from datetime import datetime
from schematics.exceptions import ValidationError

from openprocurement.auctions.core.tests.base import BaseWebTest
from openprocurement.auctions.core.plugins.awarding.v3.models import (
    Award
)
from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Contract
)
from openprocurement.api.models import Period


contract_data = {
    'awardID': '774f344a615692604de040918a72b149' # random md5
}

class TestContractingV3Prolongation(BaseWebTest):

    def test_datePublished(self):
        pass


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
        with self.assertRaises(ValidationError) as context:
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


