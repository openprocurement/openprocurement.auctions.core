# -*- coding: utf-8 -*-

from openprocurement.api.utils import get_now
from openprocurement.api.utils import (
    context_unpack,
    set_ownership,
    decrypt,
    encrypt,
    generate_id,
    json_view,
    APIResource,
    APIResourceListing
)

from openprocurement.auctions.core.design import (
    FIELDS,
    auctions_by_dateModified_view,
    auctions_real_by_dateModified_view,
    auctions_test_by_dateModified_view,
    auctions_by_local_seq_view,
    auctions_real_by_local_seq_view,
    auctions_test_by_local_seq_view,
)
from openprocurement.auctions.core.interfaces import (
    IAuctionManager,
    IManager,
)
from openprocurement.auctions.core.utils import (
    generate_auction_id,
    save_auction,
    auction_serialize,
    opresource,
    get_auction_route_name)
from openprocurement.auctions.core.validation import validate_auction_data


VIEW_MAP = {
    u'': auctions_real_by_dateModified_view,
    u'test': auctions_test_by_dateModified_view,
    u'_all_': auctions_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    u'': auctions_real_by_local_seq_view,
    u'test': auctions_test_by_local_seq_view,
    u'_all_': auctions_by_local_seq_view,
}
FEED = {
    u'dateModified': VIEW_MAP,
    u'changes': CHANGES_VIEW_MAP,
}


@opresource(name='Auctions',
            path='/auctions',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#auction for more info")
class AuctionsResource(APIResourceListing):

    def __init__(self, request, context):
        super(AuctionsResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = auction_serialize
        self.object_name_for_listing = 'Auctions'
        self.log_message_id = 'auction_list_custom'

    @json_view(content_type="application/json", permission='create_auction', validators=(validate_auction_data,))
    def post(self):
        """This API request is targeted to creating new Auctions by procuring organizations.

        Creating new Auction
        -------------------

        Example request to create auction:

        .. sourcecode:: http

            POST /auctions HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "procuringEntity": {
                        "id": {
                            "name": "Державне управління справами",
                            "scheme": "https://ns.openprocurement.org/ua/edrpou",
                            "uid": "00037256",
                            "uri": "http://www.dus.gov.ua/"
                        },
                        "address": {
                            "countryName": "Україна",
                            "postalCode": "01220",
                            "region": "м. Київ",
                            "locality": "м. Київ",
                            "streetAddress": "вул. Банкова, 11, корпус 1"
                        }
                    },
                    "value": {
                        "amount": 500,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    },
                    "itemsToBeProcured": [
                        {
                            "description": "футляри до державних нагород",
                            "primaryClassification": {
                                "scheme": "CAV",
                                "id": "44617100-9",
                                "description": "Cartons"
                            },
                            "additionalClassification": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "17.21.1",
                                    "description": "папір і картон гофровані, паперова й картонна тара"
                                }
                            ],
                            "unitOfMeasure": "item",
                            "quantity": 5
                        }
                    ],
                    "enquiryPeriod": {
                        "endDate": "2014-10-31T00:00:00"
                    },
                    "tenderPeriod": {
                        "startDate": "2014-11-03T00:00:00",
                        "endDate": "2014-11-06T10:00:00"
                    },
                    "awardPeriod": {
                        "endDate": "2014-11-13T00:00:00"
                    },
                    "deliveryDate": {
                        "endDate": "2014-11-20T00:00:00"
                    },
                    "minimalStep": {
                        "amount": 35,
                        "currency": "UAH"
                    }
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Location: http://localhost/api/0.1/auctions/64e93250be76435397e8c992ed4214d1
            Content-Type: application/json

            {
                "data": {
                    "id": "64e93250be76435397e8c992ed4214d1",
                    "auctionID": "UA-64e93250be76435397e8c992ed4214d1",
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "procuringEntity": {
                        "id": {
                            "name": "Державне управління справами",
                            "scheme": "https://ns.openprocurement.org/ua/edrpou",
                            "uid": "00037256",
                            "uri": "http://www.dus.gov.ua/"
                        },
                        "address": {
                            "countryName": "Україна",
                            "postalCode": "01220",
                            "region": "м. Київ",
                            "locality": "м. Київ",
                            "streetAddress": "вул. Банкова, 11, корпус 1"
                        }
                    },
                    "value": {
                        "amount": 500,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    },
                    "itemsToBeProcured": [
                        {
                            "description": "футляри до державних нагород",
                            "primaryClassification": {
                                "scheme": "CAV",
                                "id": "44617100-9",
                                "description": "Cartons"
                            },
                            "additionalClassification": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "17.21.1",
                                    "description": "папір і картон гофровані, паперова й картонна тара"
                                }
                            ],
                            "unitOfMeasure": "item",
                            "quantity": 5
                        }
                    ],
                    "enquiryPeriod": {
                        "endDate": "2014-10-31T00:00:00"
                    },
                    "tenderPeriod": {
                        "startDate": "2014-11-03T00:00:00",
                        "endDate": "2014-11-06T10:00:00"
                    },
                    "awardPeriod": {
                        "endDate": "2014-11-13T00:00:00"
                    },
                    "deliveryDate": {
                        "endDate": "2014-11-20T00:00:00"
                    },
                    "minimalStep": {
                        "amount": 35,
                        "currency": "UAH"
                    }
                }
            }

        """
        auction = self.request.validated['auction']

        if auction['_internal_type'] == 'geb':
            manager = self.request.registry.queryMultiAdapter((self.request, auction), IManager)
            applicant = self.request.validated['auction']
            auction = manager.create(applicant)
            if not auction:
                return
        else:
            self.request.registry.getAdapter(auction, IAuctionManager).create_auction(self.request)
            auction_id = generate_id()
            auction.id = auction_id
            auction.auctionID = generate_auction_id(get_now(), self.db, self.server_id)
            if hasattr(auction, "initialize"):
                auction.initialize()
            status = self.request.json_body['data'].get('status')
            if status and status in ['draft', 'pending.verification']:
                auction.status = status
        acc = set_ownership(auction, self.request)
        self.request.validated['auction'] = auction
        self.request.validated['auction_src'] = {}
        if save_auction(self.request):
            self.LOGGER.info('Created auction {} ({})'.format(auction['id'], auction.auctionID),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_create'}, {'auction_id': auction['id'], 'auctionID': auction.auctionID}))
            self.request.response.status = 201
            auction_route_name = get_auction_route_name(self.request, auction)
            self.request.response.headers['Location'] = self.request.route_url(route_name=auction_route_name, auction_id=auction['id'])
            return {'data': auction.serialize(auction.status), 'access': acc}
