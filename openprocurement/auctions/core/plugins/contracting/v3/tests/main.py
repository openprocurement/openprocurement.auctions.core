import unittest

from openprocurement.auctions.core.plugins.\
        contracting.v3.tests.prolongation_manager import (
    TestContractingV3ProlongationManager,
)
from openprocurement.auctions.core.plugins.\
        contracting.v3.tests.contract_validation import (
    TestContractingV3ContractValidation,
)


def contracting_v3_test_suite():
    """Test Suite for ContractingV3
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContractingV3ProlongationManager))
    suite.addTest(unittest.makeSuite(TestContractingV3ContractValidation))
    return suite
