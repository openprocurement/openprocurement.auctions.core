# -*- coding: utf-8 -*-
import unittest
import mock
import munch
from openprocurement.auctions.core.plugins.contracting.base.validators import (
    validate_contract_document
)


BASE_VALIDATORS_PATH = 'openprocurement.auctions.core.plugins.contracting.base.validators'


class Test(unittest.TestCase):

    @mock.patch('{}.{}'.format(BASE_VALIDATORS_PATH, 'not_active_lots_predicate'))
    def test_validate_contract_document(self, mock_not_active_lots_predicate):
        auction_status = 'auction_status'
        contract_status = 'contract_status'
        active_statuses = ['active.qualification', 'active.awarded']
        var_contract_statuses = ['pending', 'active']
        operation = 'test'
        mock_not_active_lots_predicate.return_value = True
        contract = munch.Munch({'status': contract_status})
        request = munch.Munch({'validated': {'auction_status': auction_status,
                                             'contract': contract}})

        error = "Can\'t {0} document in " \
                "current ({1}) auction status".format(operation,
                                                      request.validated['auction_status'])
        ecxpect_errors_auction_status = ('body', 'data', error)

        error = "Can {0} document only in active lot status".format(operation)
        ecxpect_errors_lot_status = ('body', 'data', error)

        error = "Can\'t {0} document in current contract status".format(operation)
        ecxpect_errors_contract_status = ('body', 'data', error)

        request.errors = mock.MagicMock()
        validate_contract_document(request, operation)
        index = request.errors.add.call_count - 1
        call_args = request.errors.add.call_args_list[index][0]
        self.assertEqual(call_args, ecxpect_errors_auction_status)
        self.assertEqual(request.errors.status, 403)

        request.errors.add.status = None
        request.validated['auction_status'] = active_statuses[0]
        validate_contract_document(request, operation)
        index = request.errors.add.call_count - 1
        call_args = request.errors.add.call_args_list[index][0]
        self.assertEqual(call_args, ecxpect_errors_lot_status)
        self.assertEqual(request.errors.status, 403)

        request.errors.status = None
        mock_not_active_lots_predicate.return_value = False
        validate_contract_document(request, operation)
        index = request.errors.add.call_count - 1
        call_args = request.errors.add.call_args_list[index][0]
        self.assertEqual(call_args, ecxpect_errors_contract_status)
        self.assertEqual(request.errors.status, 403)

        request.errors.status = None
        mock_not_active_lots_predicate.return_value = False
        request.validated['contract'].status = var_contract_statuses[0]
        result = validate_contract_document(request, operation)
        self.assertEqual(request.errors.status, None)
        self.assertEqual(request.errors.add.call_count, 3)
        self.assertEqual(result, True)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(Test))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
