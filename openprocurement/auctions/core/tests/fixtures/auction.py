# -*- coding: utf-8 -*-
import os
from zope.interface import implementer

from openprocurement.auctions.core.models import IAuction


def fixture_auction():
    """Stub for Auction

    Mocks some logic, needed for SANDBOX_MODE operating.
    """
    @implementer(IAuction)
    class MockAuction(object):
        """Auction mock for sandbox mode compatibility
        """
        def __init__(self):
            if os.environ.get('SANDBOX_MODE'):
                self.procurementMethodDetails = 'quick, accelerator=1440'

        def __contains__(self, item):
            if item in dir(self):
                return True

        def __getitem__(self, key):
            return getattr(self, key, None)

    return MockAuction()
