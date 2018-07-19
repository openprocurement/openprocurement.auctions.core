# -*- coding: utf-8 -*-
import unittest
from openprocurement.auctions.core.models import swiftsureDocument


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


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(SwiftsureDocumentTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
