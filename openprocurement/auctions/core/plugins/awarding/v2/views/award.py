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
)
from openprocurement.auctions.core.plugins.awarding.v2.utils import (
    switch_to_next_award,
    check_auction_protocol
)


@opresource(
    name='dgfInsider:Auction Awards',
    collection_path='/auctions/{auction_id}/awards',
    path='/auctions/{auction_id}/awards/{award_id}',
    awardingType='awarding_2_0',
    description="Insider auction awards"
)
@opresource(
    name='dgfFinancialAssets:Auction Awards',
    collection_path='/auctions/{auction_id}/awards',
    path='/auctions/{auction_id}/awards/{award_id}',
    awardingType='awarding_2_0',
    description="Financial auction awards"
)
@opresource(
    name='dgfOtherAssets:Auction Awards',
    collection_path='/auctions/{auction_id}/awards',
    path='/auctions/{auction_id}/awards/{award_id}',
    awardingType='awarding_2_0',
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

    @json_view(content_type="application/json", permission='create_award', validators=(validate_award_data,))
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
        auction = self.request.validated['auction']
        if auction.status != 'active.qualification':
            self.request.errors.add('body', 'data', 'Can\'t create award in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        award = self.request.validated['award']
        if any([i.status != 'active' for i in auction.lots if i.id == award.lotID]):
            self.request.errors.add('body', 'data', 'Can create award only in active lot status')
            self.request.errors.status = 403
            return
        award.complaintPeriod = award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': get_now()}
        auction.awards.append(award)
        if save_auction(self.request):
            self.LOGGER.info('Created auction award {}'.format(award.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_create'}, {'award_id': award.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route, award_id=award.id, _query={})
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

    @json_view(content_type="application/json", permission='edit_auction_award', validators=(validate_patch_award_data,))
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
        if auction.status not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update award in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        award = self.request.context
        award_status = award.status
        now = get_now()
        if award_status in ['unsuccessful', 'cancelled']:
            self.request.errors.add('body', 'data', 'Can\'t update award in current ({}) status'.format(award_status))
            self.request.errors.status = 403
            return
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if award_status == 'pending.waiting' and award.status == 'cancelled':
            if self.request.authenticated_role == 'bid_owner':
                award.complaintPeriod.endDate = now
            else:
                self.request.errors.add('body', 'data', 'Only bid owner may cancel award in current ({}) status'.format(award_status))
                self.request.errors.status = 403
                return
        elif award_status == 'pending.verification' and award.status == 'pending.payment':
            if check_auction_protocol(award):
                award.verificationPeriod.endDate = now
            else:
                self.request.errors.add('body', 'data', 'Can\'t switch award status to (pending.payment) before auction owner load auction protocol')
                self.request.errors.status = 403
                return
        elif award_status == 'pending.payment' and award.status == 'active' and award.paymentPeriod.endDate > now:
            award.complaintPeriod.endDate = award.paymentPeriod.endDate = now
            auction.contracts.append(type(auction).contracts.model_class({
                'awardID': award.id,
                'suppliers': award.suppliers,
                'value': award.value,
                'date': get_now(),
                'items': [i for i in auction.items if i.relatedLot == award.lotID],
                'contractID': '{}-{}{}'.format(auction.auctionID, self.server_id, len(auction.contracts) + 1)}))
            auction.status = 'active.awarded'
            auction.awardPeriod.endDate = now
        elif award_status != 'pending.waiting' and award.status == 'unsuccessful':
            if award_status == 'pending.verification':
                award.verificationPeriod.endDate = now
            elif award_status == 'pending.payment':
                award.paymentPeriod.endDate = now
            elif award_status == 'active':
                award.signingPeriod.endDate = now
                auction.awardPeriod.endDate = None
                auction.status = 'active.qualification'
                for i in auction.contracts:
                    if i.awardID == award.id:
                        i.status = 'cancelled'
            award.complaintPeriod.endDate = now
            switch_to_next_award(self.request)
        elif award_status != award.status:
            self.request.errors.add('body', 'data', 'Can\'t switch award ({}) status to ({}) status'.format(award_status, award.status))
            self.request.errors.status = 403
            return
        if save_auction(self.request):
            self.LOGGER.info('Updated auction award {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_patch'}))
            return {'data': award.serialize("view")}

