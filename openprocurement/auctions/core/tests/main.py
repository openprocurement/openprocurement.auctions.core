# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests import auctions
from openprocurement.auctions.core.plugins.contracting.v3.tests.models import (
    TestContractingV3Prolongation,
    TestContractingV3Contract,
)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(auctions.suite())
    suite.addTest(TestContractingV3Contract.suite())
    suite.addTest(TestContractingV3Prolongation.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
