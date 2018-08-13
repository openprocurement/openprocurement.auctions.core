# -*- coding: utf-8 -*-
import unittest

from copy import deepcopy
from openprocurement.auctions.core.models import (
    SwiftsureItem,
    swiftsureDocument,
)
from openprocurement.auctions.core.tests.fixtures.items import (
    swiftsure_item,
)


class SwiftsureDocumentTest(unittest.TestCase):

    def test_x_PlatformLegalDetails_validation(self):
        data = {
            'title': u'Перелік та реквізити авторизованих електронних майданчиків',
            'description': u'Перелік та реквізити авторизованих електронних майданчиків '
                           u'(найменування установи банку, її адреса та номери рахунків, '
                           u'відкритих для внесення гарантійного внеску, реєстраційного внеску)',
            'url': 'https://prozorro.sale/info/elektronni-majdanchiki-ets-prozorroprodazhi-cbd2',
            'documentOf': 'lot',
            'documentType': 'x_PlatformLegalDetails',
            'relatedItem': '1' * 32
        }
        document = swiftsureDocument(data)
        document.validate()


class SwiftsureItemTest(unittest.TestCase):

    def test_quiantity_4_decimal_places(self):
        data = deepcopy(swiftsure_item)
        data['quantity'] = 5.0123456789  # 10 decimal places
        item = SwiftsureItem(data)
        item.validate()
        assert str(item.quantity) == '5.0123'  # 4 decimal places


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(SwiftsureDocumentTest))
    tests.addTest(unittest.makeSuite(SwiftsureItemTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
