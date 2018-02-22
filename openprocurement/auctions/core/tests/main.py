# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests import auctions
from openprocurement.auctions.core.plugins.contracting.v3.tests import validators

def suite():
    tests = unittest.TestSuite()
    tests.addTest(auctions.suite())
    tests.addTest(validators.suite())
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
