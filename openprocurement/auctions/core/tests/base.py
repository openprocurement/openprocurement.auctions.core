# -*- coding: utf-8 -*-
import os
import unittest
import webtest
from types import FunctionType
from uuid import uuid4
from copy import deepcopy
from datetime import datetime, timedelta
from requests.models import Response
from base64 import b64encode
from urllib import urlencode

from openprocurement.api.config import DS
from openprocurement.api.constants import VERSION
from openprocurement.api.design import sync_design
from openprocurement.api.tests.base import (
    JSON_RENDERER_ERROR,  # noqa forwarded import
    test_config_data
)
from openprocurement.auctions.core.utils import (
    apply_data_patch,
    SESSION,
)


now = datetime.now()
test_organization = {
    "name": u"Державне управління справами",
    "identifier": {
        "scheme": u"UA-EDR",
        "id": u"00037256",
        "uri": u"http://www.dus.gov.ua/"
    },
    "address": {
        "countryName": u"Україна",
        "postalCode": u"01220",
        "region": u"м. Київ",
        "locality": u"м. Київ",
        "streetAddress": u"вул. Банкова, 11, корпус 1"
    },
    "contactPoint": {
        "name": u"Державне управління справами",
        "telephone": u"0440000000"
    }
}
test_procuringEntity = test_organization.copy()
test_auction_data = {
    "title": u"футляри до державних нагород",
    "dgfID": u"219560",
    "dgfDecisionDate": u"2016-11-17",
    "dgfDecisionID": u"219560",
    "tenderAttempts": 1,
    "procuringEntity": test_procuringEntity,
    "value": {
        "amount": 100,
        "currency": u"UAH"
    },
    "minimalStep": {
        "amount": 35,
        "currency": u"UAH"
    },
    "items": [
        {
            "description": u"Земля для військовослужбовців",
            "classification": {
                "scheme": u"CAV",
                "id": u"06000000-2",
                "description": u"Земельні ділянки"
            },
            "unit": {
                "name": u"item",
                "code": u"44617100-9"
            },
            "quantity": 5,
            "address": {
                "countryName": u"Україна",
                "postalCode": "79000",
                "region": u"м. Київ",
                "locality": u"м. Київ",
                "streetAddress": u"вул. Банкова 1"
            }
        }
    ],
    "auctionPeriod": {
        "startDate": (now.date() + timedelta(days=14)).isoformat()
    }
}
base_test_bids = [
    {
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 469,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    },
    {
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 479,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    }
]

def snitch(func):
    """
        This method is used to add test function to TestCase classes.
        snitch method gets test function and returns a copy of this function
        with 'test_' prefix at the beginning (to identify this function as
        an executable test).
        It provides a way to implement a storage (python module that
        contains non-executable test functions) for tests and to include
        different set of functions into different test cases.
    """
    return FunctionType(func.func_code, func.func_globals,
                        'test_' + func.func_name, closure=func.func_closure)


class PrefixedRequestClass(webtest.app.TestRequest):

    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = '/api/%s%s' % (VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseWebTest(unittest.TestCase):

    """Base Web Test to test openprocurement.auctions.flash.

    It setups the database before each test and delete it after.
    """

    relative_to = os.path.dirname(__file__)

    @classmethod
    def setUpClass(cls):
        if not getattr(cls, 'app', None) or getattr(cls, 'docservice', True):
            cls.app = webtest.TestApp("config:tests.ini", relative_to=cls.relative_to)
        cls.app.RequestClass = PrefixedRequestClass
        if getattr(cls.app.app.registry, 'admin_couchdb_server', None):
            cls.couchdb_server = cls.app.app.registry.admin_couchdb_server
        else:
            cls.couchdb_server = cls.app.app.registry.couchdb_server
        cls.db = cls.app.app.registry.db
        cls.db_name = cls.db.name

    @classmethod
    def tearDownClass(cls):
        try:
            cls.couchdb_server.delete(cls.db_name)
        except:
            pass

    def setUp(self):
        self.db_name += uuid4().hex
        self.couchdb_server.create(self.db_name)
        db = self.couchdb_server[self.db_name]
        sync_design(db)
        self.app.app.registry.db = db
        self.db = self.app.app.registry.db
        self.db_name = self.db.name
        self.app.authorization = ('Basic', ('token', ''))
        #self.app.authorization = ('Basic', ('broker', ''))

    def tearDown(self):
        self.couchdb_server.delete(self.db_name)

    def setUpDS(self):
        self.app.app.registry.use_docservice = True
        ds_config = deepcopy(test_config_data['config']['ds'])
        docservice = DS(ds_config)
        self.app.app.registry.docservice_url = docservice.download_url
        self.app.app.registry.docservice_upload_url = docservice.upload_url
        self.app.app.registry.docservice_username = docservice.user.name
        self.app.app.registry.docservice_password = docservice.user.password
        self.app.app.registry.docservice_key = dockey = docservice.signer
        self.app.app.registry.keyring = docservice.init_keyring(dockey)

        test = self
        def request(method, url, **kwargs):
            response = Response()
            if method == 'POST' and '/upload' in url:
                url = test.generate_docservice_url()
                response.status_code = 200
                response.encoding = 'application/json'
                response._content = '{{"data":{{"url":"{url}","hash":"md5:{md5}","format":"application/msword","title":"name.doc"}},"get_url":"{url}"}}'.format(url=url, md5='0'*32)
                response.reason = '200 OK'
            return response

        self._srequest = SESSION.request
        SESSION.request = request

    def generate_docservice_url(self):
        uuid = uuid4().hex
        key = self.app.app.registry.docservice_key
        keyid = key.hex_vk()[:8]
        signature = b64encode(key.signature("{}\0{}".format(uuid, '0' * 32)))
        query = {'Signature': signature, 'KeyID': keyid}
        return "http://localhost/get/{}?{}".format(uuid, urlencode(query))


class BaseAuctionWebTest(BaseWebTest):
    initial_data = None
    initial_status = None
    initial_bids = None
    initial_lots = None
    docservice = False

    def set_status(self, status, extra=None):
        data = {'status': status}
        if status == 'active.enquiries':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now + timedelta(days=7)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now + timedelta(days=7)).isoformat(),
                    "endDate": (now + timedelta(days=14)).isoformat()
                }
            })
        elif status == 'active.tendering':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=10)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now + timedelta(days=7)).isoformat()
                }
            })
        elif status == 'active.auction':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=14)).isoformat(),
                    "endDate": (now - timedelta(days=7)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=7)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now).isoformat()
                            }
                        }
                        for _ in self.initial_lots
                    ]
                })
        elif status == 'active.qualification':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=15)).isoformat(),
                    "endDate": (now - timedelta(days=8)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=8)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=1)).isoformat(),
                                "endDate": (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'active.awarded':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=15)).isoformat(),
                    "endDate": (now - timedelta(days=8)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=8)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=1)).isoformat(),
                                "endDate": (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'complete':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=25)).isoformat(),
                    "endDate": (now - timedelta(days=18)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=18)).isoformat(),
                    "endDate": (now - timedelta(days=11)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=11)).isoformat(),
                    "endDate": (now - timedelta(days=10)).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now - timedelta(days=10)).isoformat(),
                    "endDate": (now - timedelta(days=10)).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=11)).isoformat(),
                                "endDate": (now - timedelta(days=10)).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        if extra:
            data.update(extra)
        auction = self.db.get(self.auction_id)
        auction.update(apply_data_patch(auction, data))
        self.db.save(auction)
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        #response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        response = self.app.get('/auctions/{}'.format(self.auction_id))
        self.app.authorization = authorization
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        return response

    def setUp(self):
        super(BaseAuctionWebTest, self).setUp()
        self.create_auction()
        if self.docservice:
            self.setUpDS()

    def create_auction(self):
        data = deepcopy(self.initial_data)
        if self.initial_lots:
            lots = []
            for i in self.initial_lots:
                lot = deepcopy(i)
                lot['id'] = uuid4().hex
                lots.append(lot)
            data['lots'] = self.initial_lots = lots
            for i, item in enumerate(data['items']):
                item['relatedLot'] = lots[i % len(lots)]['id']
        response = self.app.post_json('/auctions', {'data': data})
        auction = response.json['data']
        self.auction_token = response.json['access']['token']
        self.auction_id = auction['id']
        status = auction['status']
        if self.initial_bids:
            self.initial_bids_tokens = {}
            response = self.set_status('active.tendering')
            status = response.json['data']['status']
            bids = []
            for i in self.initial_bids:
                if self.initial_lots:
                    i = i.copy()
                    value = i.pop('value')
                    i['lotValues'] = [
                        {
                            'value': value,
                            'relatedLot': l['id'],
                        }
                        for l in self.initial_lots
                    ]
                response = self.app.post_json('/auctions/{}/bids'.format(self.auction_id), {'data': i})
                self.assertEqual(response.status, '201 Created')
                bids.append(response.json['data'])
                self.initial_bids_tokens[response.json['data']['id']] = response.json['access']['token']
            self.initial_bids = bids
        if self.initial_status != status:
            self.set_status(self.initial_status)

    def tearDownDS(self):
        SESSION.request = self._srequest

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        del self.db[self.auction_id]
        super(BaseAuctionWebTest, self).tearDown()
