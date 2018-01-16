# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests import auctions


def suite():
    suite = unittest.TestSuite()
    suite.addTest(auctions.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
