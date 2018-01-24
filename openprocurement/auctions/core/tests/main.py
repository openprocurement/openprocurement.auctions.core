# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests import auctions
from openprocurement.auctions.core.plugins.contracting.v3.tests.validators import (
    TestContractingV3Validators
)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(auctions.suite())
    suite.addTest(TestContractingV3Validators.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
