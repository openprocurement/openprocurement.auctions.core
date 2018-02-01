# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests import auctions
from openprocurement.auctions.core.plugins.\
        contracting.v3.tests.main import (
    contracting_v3_test_suite
)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(auctions.suite())
    suite.addTest(contracting_v3_test_suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
