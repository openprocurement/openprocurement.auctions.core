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


class TestContractingV3Validators(BaseWebTest):

    contract_data = {
        'awardID': '774f344a615692604de040918a72b149' # random md5
    }

    def test_datePaid_good_date(self):
        contract = Contract(self.contract_data)
        period = Period()
        period.startDate = datetime(2000, 1, 1)
        period.endDate = datetime(2000, 1, 10)
        contract.signingPeriod = period
        period.validate()
        contract.datePaid = datetime(2000, 1, 5)
        contract.validate()
        self.db.commit()
        self.assertEqual(contract.signingPeriod.startDate, datetime(2000, 1, 1))

    def test_datePaid_wrong_date(self):
        contract = Contract(self.contract_data)
        period = Period()
        period.startDate = datetime(2000, 1, 1)
        period.endDate = datetime(2000, 1, 10)
        contract.signingPeriod = period
        self.db.commit()
        with self.assertRaises(ValidationError) as context:
            contract.datePaid = datetime(1999, 12, 31)
            contract.validate()

    def test_datePaid_when_signingPeriod_None(self):
        contract = Contract(self.contract_data)
        period = Period()
        period.startDate = datetime(2000, 1, 1)
        period.endDate = datetime(2000, 1, 10)
        contract.signingPeriod = period
        contract.datePaid = None
        contract.validate()

