# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
    get_now,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    save_auction,
    opresource,
)
from openprocurement.auctions.core.validation import (
    validate_award_data,
    validate_patch_award_data,
    validate_award_data_post_common,
    validate_patch_award_data_patch_common,
)
from openprocurement.auctions.core.plugins.awarding.v3.utils import (
    check_auction_protocol
)


@opresource(
    name='awarding_3_0:Auction Awards',
    collection_path='/auctions/{auction_id}/awards',
    path='/auctions/{auction_id}/awards/{award_id}',
    awardingType='awarding_3_0',
    description="Auction awards"
)
class AuctionAwardResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Awards List

        Get Awards List
        ---------------

        Example request to get awards list:

        .. sourcecode:: http

            GET /auctions/4879d3f8ee2443169b5fbbc9f89fa607/awards HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                        "status": "active",
                        "suppliers": [
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
                ]
            }

        """
        return {'data': [i.serialize("view") for i in self.request.validated['auction'].awards]}

    @json_view(content_type="application/json", permission='create_award',
               validators=(validate_award_data, validate_award_data_post_common))
    def collection_post(self):
        """Accept or reject bidder application

        Creating new Award
        ------------------

        Example request to create award:

        .. sourcecode:: http

            POST /auctions/4879d3f8ee2443169b5fbbc9f89fa607/awards HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "status": "active",
                    "suppliers": [
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
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
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
        award = self.request.validated['award']
        period = {'startDate': get_now()}
        award.complaintPeriod = award.signingPeriod = period
        award.paymentPeriod = award.verificationPeriod = period
        self.request.validated['auction'].awards.append(award)
        if save_auction(self.request):
            self.LOGGER.info('Created auction award {}'.format(award.id),
                        extra=context_unpack(self.request,
                                             {'MESSAGE_ID': 'auction_award_create'},
                                             {'award_id': award.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            headers_locations = self.request.current_route_url(_route_name=route,
                                                               award_id=award.id,
                                                               _query={})
            self.request.response.headers['Location'] = headers_locations
            return {'data': award.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the award

        Example request for retrieving the award:

        .. sourcecode:: http

            GET /auctions/4879d3f8ee2443169b5fbbc9f89fa607/awards/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
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
        return {'data': self.request.validated['award'].serialize("view")}

    @json_view(content_type="application/json", permission='edit_auction_award',
               validators=(validate_patch_award_data, validate_patch_award_data_patch_common))
    def patch(self):
        """Update of award

        Example request to change the award:

        .. sourcecode:: http

            PATCH /auctions/4879d3f8ee2443169b5fbbc9f89fa607/awards/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
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
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "date": "2014-10-28T11:44:17.947Z",
                    "status": "active",
                    "suppliers": [
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
                        "amount": 600,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        auction = self.request.validated['auction']
        award = self.request.context
        current_award_status = award.status
        now = get_now()
        if current_award_status in ['unsuccessful', 'cancelled']:
            self.request.errors.add(
                'body',
                'data',
                'Can\'t update award in current ({}) status' .format(current_award_status)
            )
            self.request.errors.status = 403
            return

        apply_patch(self.request, save=False, src=self.request.context.serialize())
        new_award_status = award.status

        if current_award_status == 'pending.waiting' and new_award_status == 'cancelled':
            if self.request.authenticated_role == 'bid_owner':
                award.complaintPeriod.endDate = now
            else:
                self.request.errors.add(
                    'body',
                    'data',
                    'Only bid owner may cancel award in current ({}) status'.format(current_award_status)
                )
                self.request.errors.status = 403
                return

        elif current_award_status == 'pending' and new_award_status == 'active':
            if check_auction_protocol(award):
                award.verificationPeriod.endDate = now
            else:
                self.request.errors.add(
                    'body',
                    'data',
                    'Can\'t switch award status to (active) before'
                    ' auction owner load auction protocol'
                )
                self.request.errors.status = 403
                return

            award.complaintPeriod.endDate = now
            auction.contracts.append(type(auction).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'value': award.value,
                'date': get_now(),
                'items': auction.items,
                'contractID': '{}-{}{}'.format(
                    auction.auctionID,
                    self.server_id,
                    len(auction.contracts) + 1
                ),
                'signingPeriod': award.signingPeriod,
            }))
            auction.status = 'active.awarded'
            auction.awardPeriod.endDate = now
        elif current_award_status != 'pending.waiting' and new_award_status == 'unsuccessful':
            if current_award_status == 'pending':
                award.verificationPeriod.endDate = now
            elif current_award_status == 'active':
                contract = None
                for contract in auction.contracts:
                    if contract.awardID == award.id:
                        break
                if getattr(contract, 'dateSigned', False):
                    err_message = 'You cannot disqualify the bidder whose' \
                                  ' contract has already been activated.'
                    self.request.errors.add('body', 'data', err_message)
                    self.request.errors.status = 403
                    return
                award.signingPeriod.endDate = now
                auction.awardPeriod.endDate = None
                auction.status = 'active.qualification'
                for i in auction.contracts:
                    if i.awardID == award.id:
                        i.status = 'cancelled'
            award.complaintPeriod.endDate = now
            self.request.content_configurator.back_to_awarding()
        elif current_award_status != new_award_status:
            self.request.errors.add(
                'body',
                'data',
                'Can\'t switch award ({0}) status to ({1}) status'.format(
                    current_award_status,
                    new_award_status
                )
            )
            self.request.errors.status = 403
            return

        if save_auction(self.request):
            self.LOGGER.info(
                'Updated auction award {}'.format(self.request.context.id),
                 extra=context_unpack(
                     self.request,
                     {'MESSAGE_ID': 'auction_award_patch'}
                 )
            )
            return {'data': award.serialize("view")}
