# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    update_file_content_type, get_file, upload_file
)
from openprocurement.auctions.core.interfaces import IAuctionManager
from openprocurement.auctions.core.constants import STATUS4ROLE
from openprocurement.auctions.core.utils import (
    APIResource,
    apply_patch,
    check_auction_status,
    cleanup_bids_for_cancelled_lots,
    context_unpack,
    check_status,
    get_now,
    json_view,
    save_auction,
    set_ownership,
)
from openprocurement.auctions.core.validation import (
    validate_auction_auction_data,
    validate_patch_bid_data,
    validate_bid_data,
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
    validate_patch_cancellation_data,
    validate_cancellation_data,
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_lot_data,
    validate_patch_lot_data,
    validate_question_data,
    validate_patch_question_data,
    validate_patch_auction_data
)


class AuctionAuctionResource(APIResource):

    @json_view(permission='auction')
    def collection_get(self):
        """Get auction info.

        Get auction auction info
        -----------------------

        Example request to get auction auction information:

        .. sourcecode:: http

            GET /auctions/4879d3f8ee2443169b5fbbc9f89fa607/auction HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "bids": [
                        {
                            "value": {
                                "amount": 500,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        },
                        {
                            "value": {
                                "amount": 485,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        }
                    ],
                    "minimalStep":{
                        "amount": 35,
                        "currency": "UAH"
                    },
                    "tenderPeriod":{
                        "startDate": "2014-11-04T08:00:00"
                    }
                }
            }

        """
        if self.request.validated['auction_status'] != 'active.auction':
            self.request.errors.add('body', 'data', 'Can\'t get auction info in current ({}) auction status'.format(
                self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        return {'data': self.request.validated['auction'].serialize("auction_view")}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def collection_patch(self):
        """Set urls for access to auction.
        """
        if apply_patch(self.request, src=self.request.validated['auction_src']):
            self.LOGGER.info('Updated auction urls',
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_auction_patch'}))
            return {'data': self.request.validated['auction'].serialize("auction_view")}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def collection_post(self):
        """Report auction results.

        Report auction results
        ----------------------

        Example request to report auction results:

        .. sourcecode:: http

            POST /auctions/4879d3f8ee2443169b5fbbc9f89fa607/auction HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "bids": [
                        {
                            "value": {
                                "amount": 400,
                                "currency": "UAH"
                            }
                        },
                        {
                            "value": {
                                "amount": 385,
                                "currency": "UAH"
                            }
                        }
                    ]
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "bids": [
                        {
                            "value": {
                                "amount": 400,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        },
                        {
                            "value": {
                                "amount": 385,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        }
                    ],
                    "minimalStep":{
                        "amount": 35,
                        "currency": "UAH"
                    },
                    "tenderPeriod":{
                        "startDate": "2014-11-04T08:00:00"
                    }
                }
            }

        """
        apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
        if all([i.auctionPeriod and i.auctionPeriod.endDate for i in self.request.validated['auction'].lots if
                i.numberOfBids > 1 and i.status == 'active']):
            self.request.content_configurator.start_awarding()
        if save_auction(self.request):
            self.LOGGER.info('Report auction results',
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_auction_post'}))
            return {'data': self.request.validated['auction'].serialize(self.request.validated['auction'].status)}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def patch(self):
        """Set urls for access to auction for lot.
        """
        if apply_patch(self.request, src=self.request.validated['auction_src']):
            self.LOGGER.info('Updated auction urls',
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_auction_patch'}))
            return {'data': self.request.validated['auction'].serialize("auction_view")}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def post(self):
        """Report auction results for lot.
        """
        apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
        if all([i.auctionPeriod and i.auctionPeriod.endDate for i in self.request.validated['auction'].lots if
                i.numberOfBids > 1 and i.status == 'active']):
            cleanup_bids_for_cancelled_lots(self.request.validated['auction'])
            self.request.content_configurator.start_awarding()
        if save_auction(self.request):
            self.LOGGER.info('Report auction results',
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_auction_post'}))
            return {'data': self.request.validated['auction'].serialize(self.request.validated['auction'].status)}


class AuctionBidResource(APIResource):

    @json_view(content_type="application/json", permission='create_bid', validators=(validate_bid_data,))
    def collection_post(self):
        """Registration of new bid proposal

        Creating new Bid proposal
        -------------------------

        Example request to create bid proposal:

        .. sourcecode:: http

            POST /auctions/4879d3f8ee2443169b5fbbc9f89fa607/bids HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "tenderers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "status": "registration",
                    "date": "2014-10-28T11:44:17.947Z",
                    "tenderers": [
                        {
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
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        # See https://github.com/open-contracting/standard/issues/78#issuecomment-59830415
        # for more info upon schema
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] != 'active.tendering':
            self.request.errors.add('body', 'data', 'Can\'t add bid in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if auction.tenderPeriod.startDate and get_now() < auction.tenderPeriod.startDate or get_now() > auction.tenderPeriod.endDate:
            self.request.errors.add('body', 'data', 'Bid can be added only during the tendering period: from ({}) to ({}).'.format(auction.tenderPeriod.startDate and auction.tenderPeriod.startDate.isoformat(), auction.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        bid = self.request.validated['bid']
        set_ownership(bid, self.request)
        auction.bids.append(bid)
        auction.modified = False
        if save_auction(self.request):
            self.LOGGER.info('Created auction bid {}'.format(bid.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_create'}, {'bid_id': bid.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route, bid_id=bid.id, _query={})
            return {
                'data': bid.serialize('view'),
                'access': {
                    'token': bid.owner_token
                }
            }

    @json_view(permission='view_auction')
    def collection_get(self):
        """Bids Listing

        Get Bids List
        -------------

        Example request to get bids list:

        .. sourcecode:: http

            GET /auctions/4879d3f8ee2443169b5fbbc9f89fa607/bids HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                        "value": {
                            "amount": 489,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": true
                        }
                    }
                ]
            }

        """
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] in ['active.tendering', 'active.auction']:
            self.request.errors.add('body', 'data', 'Can\'t view bids in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        return {'data': [i.serialize(self.request.validated['auction_status']) for i in auction.bids]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the proposal

        Example request for retrieving the proposal:

        .. sourcecode:: http

            GET /auctions/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "value": {
                        "amount": 600,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        if self.request.authenticated_role == 'bid_owner':
            return {'data': self.request.context.serialize('view')}
        if self.request.validated['auction_status'] in ['active.tendering', 'active.auction']:
            self.request.errors.add('body', 'data', 'Can\'t view bid in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        return {'data': self.request.context.serialize(self.request.validated['auction_status'])}

    @json_view(content_type="application/json", permission='edit_bid', validators=(validate_patch_bid_data,))
    def patch(self):
        """Update of proposal

        Example request to change bid proposal:

        .. sourcecode:: http

            PATCH /auctions/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "value": {
                        "amount": 600
                    }
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "value": {
                        "amount": 600,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """

        if self.request.authenticated_role != 'Administrator' and self.request.validated['auction_status'] != 'active.tendering':
            self.request.errors.add('body', 'data', 'Can\'t update bid in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        auction = self.request.validated['auction']
        if self.request.authenticated_role != 'Administrator' and (auction.tenderPeriod.startDate and get_now() < auction.tenderPeriod.startDate or get_now() > auction.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Bid can be updated only during the tendering period: from ({}) to ({}).'.format(auction.tenderPeriod.startDate and auction.tenderPeriod.startDate.isoformat(), auction.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if self.request.authenticated_role != 'Administrator':
            bid_status_to = self.request.validated['data'].get("status")
            if bid_status_to != self.request.context.status and bid_status_to != "active":
                self.request.errors.add('body', 'bid', 'Can\'t update bid to ({}) status'.format(bid_status_to))
                self.request.errors.status = 403
                return
        value = self.request.validated['data'].get("value") and self.request.validated['data']["value"].get("amount")
        if value and value != self.request.context.get("value", {}).get("amount"):
            self.request.validated['data']['date'] = get_now().isoformat()
        if self.request.context.lotValues:
            lotValues = dict([(i.relatedLot, i.value.amount) for i in self.request.context.lotValues])
            for lotvalue in self.request.validated['data'].get("lotValues", []):
                if lotvalue['relatedLot'] in lotValues and lotvalue.get("value", {}).get("amount") != lotValues[lotvalue['relatedLot']]:
                    lotvalue['date'] = get_now().isoformat()
        self.request.validated['auction'].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info('Updated auction bid {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_patch'}))
            return {'data': self.request.context.serialize("view")}

    @json_view(permission='edit_bid')
    def delete(self):
        """Cancelling the proposal

        Example request for cancelling the proposal:

        .. sourcecode:: http

            DELETE /auctions/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        bid = self.request.context
        if self.request.validated['auction_status'] != 'active.tendering':
            self.request.errors.add('body', 'data', 'Can\'t delete bid in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        auction = self.request.validated['auction']
        if auction.tenderPeriod.startDate and get_now() < auction.tenderPeriod.startDate or get_now() > auction.tenderPeriod.endDate:
            self.request.errors.add('body', 'data', 'Bid can be deleted only during the tendering period: from ({}) to ({}).'.format(auction.tenderPeriod.startDate and auction.tenderPeriod.startDate.isoformat(), auction.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        res = bid.serialize("view")
        self.request.validated['auction'].bids.remove(bid)
        self.request.validated['auction'].modified = False
        if save_auction(self.request):
            self.LOGGER.info('Deleted auction bid {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_delete'}))
            return {'data': res}


class AuctionBidDocumentResource(APIResource):

    def validate_bid_document(self, operation):
        auction = self.request.validated['auction']
        if auction.status not in ['active.tendering', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) auction status'.format(operation, auction.status))
            self.request.errors.status = 403
            return
        if auction.status == 'active.tendering' and not (auction.tenderPeriod.startDate < get_now() < auction.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be {} only during the tendering period: from ({}) to ({}).'.format('added' if operation == 'add' else 'updated', auction.tenderPeriod.startDate.isoformat(), auction.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if auction.status == 'active.qualification' and not [i for i in auction.awards if i.status == 'pending' and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t {} document because award of bid is not in pending state'.format(operation))
            self.request.errors.status = 403
            return
        documentType = self.request.validated.get('data', {}).get('documentType', None)
        if documentType and documentType in ['auctionProtocol']:
            self.request.errors.add('body', 'data', 'Can\'t {} document with {} documentType'.format(operation, documentType))
            self.request.errors.status = 403
        return True

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Bid Documents List"""
        if self.request.validated['auction_status'] in ['active.tendering', 'active.auction'] and self.request.authenticated_role != 'bid_owner':
            self.request.errors.add('body', 'data', 'Can\'t view bid documents in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload,), permission='edit_bid')
    def collection_post(self):
        """Auction Bid Document Upload
        """
        if not self.validate_bid_document('add'):
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if self.request.validated['auction_status'] == 'active.tendering':
            self.request.validated['auction'].modified = False
        if save_auction(self.request):
            self.LOGGER.info('Created auction bid document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Bid Document Read"""
        if self.request.validated['auction_status'] in ['active.tendering', 'active.auction'] and self.request.authenticated_role != 'bid_owner':
            self.request.errors.add('body', 'data', 'Can\'t view bid document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}

    @json_view(validators=(validate_file_update,), permission='edit_bid')
    def put(self):
        """Auction Bid Document Update"""
        if not self.validate_bid_document('update'):
            return
        document = upload_file(self.request)
        self.request.validated['bid'].documents.append(document)
        if self.request.validated['auction_status'] == 'active.tendering':
            self.request.validated['auction'].modified = False
        if save_auction(self.request):
            self.LOGGER.info('Updated auction bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_bid')
    def patch(self):
        """Auction Bid Document Update"""
        if not self.validate_bid_document('update'):
            return
        if self.request.validated['auction_status'] == 'active.tendering':
            self.request.validated['auction'].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_document_patch'}))
            return {'data': self.request.context.serialize("view")}


class AuctionCancellationResource(APIResource):

    def cancel_auction(self):
        auction = self.request.validated['auction']
        if auction.status in ['active.tendering', 'active.auction']:
            auction.bids = []
        auction.status = 'cancelled'

    def cancel_lot(self, cancellation=None):
        if not cancellation:
            cancellation = self.context
        auction = self.request.validated['auction']
        _ = [setattr(i, 'status', 'cancelled') for i in auction.lots if i.id == cancellation.relatedLot]
        statuses = set([lot.status for lot in auction.lots])
        if statuses == set(['cancelled']):
            self.cancel_auction()
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            auction.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            auction.status = 'complete'
        if auction.status == 'active.auction' and all([
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in self.request.validated['auction'].lots
            if i.numberOfBids > 1 and i.status == 'active'
        ]):
            self.request.content_configurator.back_to_awarding()

    @json_view(content_type="application/json", validators=(validate_cancellation_data,), permission='edit_auction')
    def collection_post(self):
        """Post a cancellation
        """
        auction = self.request.validated['auction']
        if auction.status in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data',
                                    'Can\'t add cancellation in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        cancellation = self.request.validated['cancellation']
        cancellation.date = get_now()
        if any([i.status != 'active' for i in auction.lots if i.id == cancellation.relatedLot]):
            self.request.errors.add('body', 'data', 'Can add cancellation only in active lot status')
            self.request.errors.status = 403
            return
        if cancellation.relatedLot and cancellation.status == 'active':
            self.cancel_lot(cancellation)
        elif cancellation.status == 'active':
            self.cancel_auction()
        auction.cancellations.append(cancellation)
        if save_auction(self.request):
            self.LOGGER.info('Created auction cancellation {}'.format(cancellation.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_create'},
                                                  {'cancellation_id': cancellation.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route,
                                                                                       cancellation_id=cancellation.id,
                                                                                       _query={})
            return {'data': cancellation.serialize("view")}

    @json_view(permission='view_auction')
    def collection_get(self):
        """List cancellations
        """
        return {'data': [i.serialize("view") for i in self.request.validated['auction'].cancellations]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the cancellation
        """
        return {'data': self.request.validated['cancellation'].serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_cancellation_data,),
               permission='edit_auction')
    def patch(self):
        """Post a cancellation resolution
        """
        auction = self.request.validated['auction']
        if auction.status in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data',
                                    'Can\'t update cancellation in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in auction.lots if i.id == self.request.context.relatedLot]):
            self.request.errors.add('body', 'data', 'Can update cancellation only in active lot status')
            self.request.errors.status = 403
            return
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if self.request.context.relatedLot and self.request.context.status == 'active':
            self.cancel_lot()
        elif self.request.context.status == 'active':
            self.cancel_auction()
        if save_auction(self.request):
            self.LOGGER.info('Updated auction cancellation {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_patch'}))
            return {'data': self.request.context.serialize("view")}


class AuctionCancellationDocumentResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Cancellation Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload,), permission='edit_auction')
    def collection_post(self):
        """Auction Cancellation Document Upload
        """
        if self.request.validated['auction_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction cancellation document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Cancellation Document Read"""
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}

    @json_view(validators=(validate_file_update,), permission='edit_auction')
    def put(self):
        """Auction Cancellation Document Update"""
        if self.request.validated['auction_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.request.validated['cancellation'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction cancellation document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_auction')
    def patch(self):
        """Auction Cancellation Document Update"""
        if self.request.validated['auction_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction cancellation document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_document_patch'}))
            return {'data': self.request.context.serialize("view")}


class AuctionComplaintResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_complaint_data,), permission='create_complaint')
    def collection_post(self):
        """Post a complaint
        """
        auction = self.context
        if auction.status not in ['active.enquiries', 'active.tendering']:
            self.request.errors.add('body', 'data',
                                    'Can\'t add complaint in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        complaint = self.request.validated['complaint']
        complaint.date = get_now()
        if complaint.status == 'claim':
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = 'draft'
        complaint.complaintID = '{}.{}{}'.format(auction.auctionID, self.server_id,
                                                 sum([len(i.complaints) for i in auction.awards],
                                                     len(auction.complaints)) + 1)
        set_ownership(complaint, self.request)
        auction.complaints.append(complaint)
        if save_auction(self.request):
            self.LOGGER.info('Created auction complaint {}'.format(complaint.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_complaint_create'},
                                                  {'complaint_id': complaint.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route,
                                                                                       complaint_id=complaint.id,
                                                                                       _query={})
            return {
                'data': complaint.serialize(auction.status),
                'access': {
                    'token': complaint.owner_token
                }
            }

    @json_view(permission='view_auction')
    def collection_get(self):
        """List complaints
        """
        return {'data': [i.serialize("view") for i in self.context.complaints]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the complaint
        """
        return {'data': self.context.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_complaint_data,),
               permission='edit_complaint')
    def patch(self):
        """Post a complaint resolution
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.enquiries', 'active.tendering', 'active.auction', 'active.qualification',
                                  'active.awarded']:
            self.request.errors.add('body', 'data',
                                    'Can\'t update complaint in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        if self.context.status not in ['draft', 'claim', 'answered', 'pending']:
            self.request.errors.add('body', 'data',
                                    'Can\'t update complaint in current ({}) status'.format(self.context.status))
            self.request.errors.status = 403
            return
        data = self.request.validated['data']
        # complaint_owner
        if self.request.authenticated_role == 'complaint_owner' and self.context.status in ['draft', 'claim',
                                                                                            'answered',
                                                                                            'pending'] and data.get(
                'status', self.context.status) == 'cancelled':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and auction.status in ['active.enquiries',
                                                                                         'active.tendering'] and self.context.status == 'draft' and data.get(
                'status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and auction.status in ['active.enquiries',
                                                                                         'active.tendering'] and self.context.status == 'draft' and data.get(
                'status', self.context.status) == 'claim':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateSubmitted = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get(
                'status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get(
                'satisfied', self.context.satisfied) is True and data.get('status', self.context.status) == 'resolved':
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get(
                'satisfied', self.context.satisfied) is False and data.get('status', self.context.status) == 'pending':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.type = 'complaint'
            self.context.dateEscalated = get_now()
        elif self.request.authenticated_role == 'auction_owner' and self.context.status == 'claim' and data.get(
                'status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'auction_owner' and self.context.status == 'claim' and data.get(
                'resolution', self.context.resolution) and data.get('resolutionType',
                                                                    self.context.resolutionType) and data.get('status',
                                                                                                              self.context.status) == 'answered':
            if len(data.get('resolution', self.context.resolution)) < 20:
                self.request.errors.add('body', 'data', 'Can\'t update complaint: resolution too short')
                self.request.errors.status = 403
                return
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAnswered = get_now()
        elif self.request.authenticated_role == 'auction_owner' and self.context.status == 'pending':
            apply_patch(self.request, save=False, src=self.context.serialize())
        # reviewers
        elif self.request.authenticated_role == 'reviewers' and self.context.status == 'pending' and data.get('status',
                                                                                                              self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'reviewers' and self.context.status == 'pending' and data.get('status',
                                                                                                              self.context.status) in [
            'resolved', 'invalid', 'declined']:
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
        else:
            self.request.errors.add('body', 'data', 'Can\'t update complaint')
            self.request.errors.status = 403
            return
        if self.context.tendererAction and not self.context.tendererActionDate:
            self.context.tendererActionDate = get_now()
        if self.context.status not in ['draft', 'claim', 'answered', 'pending'] and auction.status in [
            'active.qualification', 'active.awarded']:
            check_auction_status(self.request)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction complaint {}'.format(self.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_complaint_patch'}))
            return {'data': self.context.serialize("view")}


class AuctionComplaintDocumentResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Complaint Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload,), permission='edit_complaint')
    def collection_post(self):
        """Auction Complaint Document Upload
        """
        if self.request.validated['auction_status'] not in ['active.enquiries', 'active.tendering', 'active.auction',
                                                            'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(
                self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if self.context.status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            self.request.errors.add('body', 'data',
                                    'Can\'t add document in current ({}) complaint status'.format(self.context.status))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction complaint document {}'.format(document.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_complaint_document_create'},
                                                  {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route,
                                                                                       document_id=document.id,
                                                                                       _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Complaint Document Read"""
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}

    @json_view(validators=(validate_file_update,), permission='edit_complaint')
    def put(self):
        """Auction Complaint Document Update"""
        if self.request.authenticated_role != self.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] not in ['active.enquiries', 'active.tendering', 'active.auction',
                                                            'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(
                self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if self.request.validated['complaint'].status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) complaint status'.format(
                self.request.validated['complaint'].status))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.request.validated['complaint'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction complaint document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_complaint_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_complaint')
    def patch(self):
        """Auction Complaint Document Update"""
        if self.request.authenticated_role != self.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] not in ['active.enquiries', 'active.tendering', 'active.auction',
                                                            'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(
                self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if self.request.validated['complaint'].status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) complaint status'.format(
                self.request.validated['complaint'].status))
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction complaint document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_complaint_document_patch'}))
            return {'data': self.request.context.serialize("view")}


class AuctionLotResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_lot_data,), permission='edit_auction')
    def collection_post(self):
        """Add a lot
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.enquiries']:
            self.request.errors.add('body', 'data',
                                    'Can\'t add lot in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        lot = self.request.validated['lot']
        lot.date = get_now()
        auction.lots.append(lot)
        if save_auction(self.request):
            self.LOGGER.info('Created auction lot {}'.format(lot.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_create'},
                                                  {'lot_id': lot.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route, lot_id=lot.id,
                                                                                       _query={})
            return {'data': lot.serialize("view")}

    @json_view(permission='view_auction')
    def collection_get(self):
        """Lots Listing
        """
        return {'data': [i.serialize("view") for i in self.request.validated['auction'].lots]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the lot
        """
        return {'data': self.request.context.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_lot_data,), permission='edit_auction')
    def patch(self):
        """Update of lot
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.enquiries']:
            self.request.errors.add('body', 'data',
                                    'Can\'t update lot in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info('Updated auction lot {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_patch'}))
            return {'data': self.request.context.serialize("view")}

    @json_view(permission='edit_auction')
    def delete(self):
        """Lot deleting
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.enquiries']:
            self.request.errors.add('body', 'data',
                                    'Can\'t delete lot in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        lot = self.request.context
        res = lot.serialize("view")
        auction.lots.remove(lot)
        if save_auction(self.request):
            self.LOGGER.info('Deleted auction lot {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_delete'}))
            return {'data': res}


class AuctionQuestionResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_question_data,), permission='create_question')
    def collection_post(self):
        """Post a question
        """
        auction = self.request.validated['auction']
        if auction.status != 'active.enquiries' or get_now() < auction.enquiryPeriod.startDate or get_now() > auction.enquiryPeriod.endDate:
            self.request.errors.add('body', 'data', 'Can add question only in enquiryPeriod')
            self.request.errors.status = 403
            return
        question = self.request.validated['question']
        if any([i.status != 'active' for i in auction.lots if i.id == question.relatedItem]):
            self.request.errors.add('body', 'data', 'Can add question only in active lot status')
            self.request.errors.status = 403
            return
        auction.questions.append(question)
        if save_auction(self.request):
            self.LOGGER.info('Created auction question {}'.format(question.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_question_create'},
                                                  {'question_id': question.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route,
                                                                                       question_id=question.id,
                                                                                       _query={})
            return {'data': question.serialize("view")}

    @json_view(permission='view_auction')
    def collection_get(self):
        """List questions
        """
        return {'data': [i.serialize(self.request.validated['auction'].status) for i in
                         self.request.validated['auction'].questions]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the question
        """
        return {'data': self.request.validated['question'].serialize(self.request.validated['auction'].status)}

    @json_view(content_type="application/json", permission='edit_auction', validators=(validate_patch_question_data,))
    def patch(self):
        """Post an Answer
        """
        auction = self.request.validated['auction']
        if auction.status != 'active.enquiries':
            self.request.errors.add('body', 'data',
                                    'Can\'t update question in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in auction.lots if i.id == self.request.context.relatedItem]):
            self.request.errors.add('body', 'data', 'Can update question only in active lot status')
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info('Updated auction question {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_question_patch'}))
            return {'data': self.request.context.serialize(auction.status)}


class AuctionResource(APIResource):

    @json_view(permission='view_auction')
    def get(self):
        if self.request.authenticated_role == 'chronograph':
            auction_data = self.context.serialize('chronograph_view')
        else:
            auction_data = self.context.serialize(self.context.status)
        return {'data': auction_data}

    #@json_view(content_type="application/json", validators=(validate_auction_data, ), permission='edit_auction')
    #def put(self):
        #"""Auction Edit (full)"""
        #auction = self.request.validated['auction']
        #if auction.status in ['complete', 'unsuccessful', 'cancelled']:
            #self.request.errors.add('body', 'data', 'Can\'t update auction in current ({}) status'.format(auction.status))
            #self.request.errors.status = 403
            #return
        #apply_patch(self.request, src=self.request.validated['auction_src'])
        #return {'data': auction.serialize(auction.status)}

    @json_view(content_type="application/json", validators=(validate_patch_auction_data, ), permission='edit_auction')
    def patch(self):
        self.request.registry.getAdapter(
            self.request.context,
            IAuctionManager
        ).change_auction(self.request)
        auction = self.context
        if self.request.authenticated_role != 'Administrator' and auction.status in ['complete', 'unsuccessful', 'cancelled']:
            self.request.errors.add('body', 'data', 'Can\'t update auction in current ({}) status'.format(auction.status))
            self.request.errors.status = 403
            return
        if self.request.authenticated_role == 'chronograph':
            apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
            check_status(self.request)
            save_auction(self.request)
        else:
            apply_patch(self.request, src=self.request.validated['auction_src'])
        self.LOGGER.info('Updated auction {}'.format(auction.id),
                    extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_patch'}))
        return {'data': auction.serialize(auction.status)}


class AuctionDocumentResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='upload_auction_documents', validators=(validate_file_upload,))
    def collection_post(self):
        """Auction Document Upload"""
        if self.request.authenticated_role != 'auction' and self.request.validated['auction_status'] != 'active.enquiries' or \
           self.request.authenticated_role == 'auction' and self.request.validated['auction_status'] not in ['active.auction', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Document Read"""
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}

    @json_view(permission='upload_auction_documents', validators=(validate_file_update,))
    def put(self):
        """Auction Document Update"""
        if self.request.authenticated_role != 'auction' and self.request.validated['auction_status'] != 'active.enquiries' or \
           self.request.authenticated_role == 'auction' and self.request.validated['auction_status'] not in ['active.auction', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.request.validated['auction'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", permission='upload_auction_documents', validators=(validate_patch_document_data,))
    def patch(self):
        """Auction Document Update"""
        if self.request.authenticated_role != 'auction' and self.request.validated['auction_status'] != 'active.enquiries' or \
           self.request.authenticated_role == 'auction' and self.request.validated['auction_status'] not in ['active.auction', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_document_patch'}))
            return {'data': self.request.context.serialize("view")}
