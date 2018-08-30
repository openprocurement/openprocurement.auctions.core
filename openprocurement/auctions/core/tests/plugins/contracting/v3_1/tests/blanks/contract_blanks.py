from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import JSON_RENDERER_ERROR
# AuctionContractResourceTest


def create_auction_contract_invalid(self):
    response = self.app.post_json('/auctions/some_id/contracts', {
        'data': {
            'title': 'contract title',
            'description': 'contract description',
            'awardID': self.award_id
        }
    }, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found',
         u'location': u'url',
         u'name': u'auction_id'}
    ])

    request_path = '/auctions/{}/contracts'.format(self.auction_id)

    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"Content-Type header should be" 
                         u" one of ['application/json']",
         u'location': u'header',
         u'name': u'Content-Type'}
    ])

    response = self.app.post(
        request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        JSON_RENDERER_ERROR
    ])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(
        request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {
        'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(
        request_path, {'data': {'awardID': 'invalid_value'}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'awardID should be one of awards'],
         u'location': u'body',
         u'name': u'awardID'}
    ])


def create_auction_contract(self):
    auction = self.db.get(self.auction_id)
    # Contract was created on setUp stage
    contract = auction['contracts'][0]
    self.assertIn('id', contract)
    self.assertIn('value', contract)
    self.assertIn('suppliers', contract)

    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "terminated"
    self.db.save(auction)

    self.set_status('unsuccessful')

    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id
    ), {'data': {
            'title': 'contract title',
            'description': 'contract description',
            'awardID': self.award_id
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't add contract in current (unsuccessful) auction status"
    )

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(
        self.auction_id, contract['id']
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update contract in current (unsuccessful) auction status"
    )


def create_auction_contract_in_complete_status(self):
    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "terminated"
    self.db.save(auction)

    self.set_status('complete')

    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id
    ), {'data': {
            'title': 'contract title',
            'description': 'contract description',
        'awardID': self.award_id
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(
        self.auction_id, self.award_contract_id
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update contract in current (complete) auction status"
    )


def patch_auction_contract_invalid(self):
    response = self.app.patch_json('/auctions/{}/contracts/some_id'.format(
        self.auction_id
    ), {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.patch_json('/auctions/some_id/contracts/some_id',
                                   {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])


def patch_auction_contract_blacklisted_fields(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    # Trying to patch fields, that are blacklisted for editing.
    self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"contractID": "myselfID",
                 "items": [{"description": "New Description"}],
                 "suppliers": [{"name": "New Name"}]
                 }})

    # Checking fields values, that shouldn't have changed.
    response = self.app.get('/auctions/{}/contracts/{}'.format(
        self.auction_id, contract['id']
    ))
    self.assertEqual(
        response.json['data']['contractID'], contract['contractID']
    )
    self.assertEqual(response.json['data']['items'], contract['items'])
    self.assertEqual(response.json['data']['suppliers'], contract['suppliers'])


def patch_auction_contract_value(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"value": {"currency": "USD"}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update currency for contract value"
    )

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"value": {"valueAddedTaxIncluded": False}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can\'t update valueAddedTaxIncluded for contract value")

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"value": {"amount": 99}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Value amount should be greater or equal to awarded amount (479)"
    )

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"value": {"amount": 500}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['value']['amount'], 500)


def patch_auction_contract_to_active(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    # Trying to patch contract to active status
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': u"Can't sign contract without contractSigned document",
         u'location': u'body',
         u'name': u'data'}
    ])

    self.upload_contract_document(contract, 'contract')

    # Trying to patch contract to active status again
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': u"Can't sign contract without "
                         u"specified dateSigned field",
         u'location': u'body',
         u'name': u'data'}])

    # Trying to patch contract's dateSigned field with invalid value
    one_hour_in_future = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"dateSigned": one_hour_in_future}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Contract signature date can't be in the future"],
         u'location': u'body',
         u'name': u'dateSigned'}
    ])

    # Trying to patch contract's dateSigned field with valid value
    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"dateSigned": custom_signature_date}})
    self.assertEqual(response.status, '200 OK')

    # Trying to patch contract to active status again
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.get('/auctions/{}/contracts/{}'.format(
        self.auction_id, contract['id'])
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertEqual(response.json['data']["value"]['amount'], 479)
    self.assertEqual(
        response.json['data']['contractID'], contract['contractID']
    )
    self.assertEqual(response.json['data']['items'], contract['items'])
    self.assertEqual(response.json['data']['suppliers'], contract['suppliers'])
    self.assertEqual(response.json['data']['dateSigned'], custom_signature_date)


def patch_auction_contract_to_active_date_signed_burst(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    self.upload_contract_document(contract, 'contract')

    # Trying to patch contract's status to 'active' with invalid dateSigned field value
    one_hour_in_future = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {
        "dateSigned": one_hour_in_future,
        "status": 'active'
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Contract signature date can't be in the future"],
         u'location': u'body',
         u'name': u'dateSigned'}
    ])

    # Assuring that contract's has not changed during previous patch
    response = self.app.get('/auctions/{}/contracts/{}'.format(
        self.auction_id, contract['id'])
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "pending")

    # Trying to patch contract's status to 'active' with valid dateSigned field value
    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {
        "dateSigned": custom_signature_date,
        "status": 'active'
    }})
    self.assertEqual(response.status, '200 OK')

    # Assuring that contract patched properly
    response = self.app.get('/auctions/{}/contracts/{}'.format(
        self.auction_id, contract['id'])
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertEqual(response.json['data']["value"]['amount'], 479)
    self.assertEqual(
        response.json['data']['contractID'], contract['contractID']
    )
    self.assertEqual(response.json['data']['items'], contract['items'])
    self.assertEqual(response.json['data']['suppliers'], contract['suppliers'])
    self.assertEqual(response.json['data']['dateSigned'], custom_signature_date)


def patch_auction_contract_to_cancelled_invalid_no_rejection_or_act(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    # Trying to patch contract to cancelled status
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "cancelled"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': u"Can't switch contract status to (cancelled) "
                         u"before auction owner load reject protocol or act",
         u'location': u'body',
         u'name': u'data'}])

    self.check_related_award_status(contract, 'active')


def patch_auction_contract_to_cancelled_invalid_signed(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    self.upload_contract_document(contract, 'contract')
    self.upload_contract_document(contract, 'rejection')

    # Trying to patch contract to cancelled status
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "cancelled"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': u"Bidder contract for whom has already" 
                         u" been uploaded cannot be disqualified.",
         u'location': u'body',
         u'name': u'data'}])

    self.check_related_award_status(contract, 'active')


def patch_auction_contract_to_cancelled_rejection_protocol(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    self.upload_contract_document(contract, 'rejection')

    # Trying to patch contract to cancelled status
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'cancelled')

    self.check_related_award_status(contract, 'unsuccessful')


def patch_auction_contract_to_cancelled_act(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    self.upload_contract_document(contract, 'act')

    # Trying to patch contract to cancelled status
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'cancelled')

    self.check_related_award_status(contract, 'unsuccessful')


def patch_auction_contract_in_auction_complete_status(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    self.set_status('complete')

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"value": {"amount": 232}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update contract in current (complete) auction status"
    )

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"contractID": "myselfID"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update contract in current (complete) auction status"
    )

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"items": [{"description": "New Description"}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update contract in current (complete) auction status"
    )

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"suppliers": [{"name": "New Name"}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update contract in current (complete) auction status"
    )

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update contract in current (complete) auction status"
    )


def get_auction_contract(self):
    response = self.app.get('/auctions/{}/contracts/{}'.format(
        self.auction_id, self.award_contract_id
    ))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/auctions/{}/contracts/some_id'.format(
        self.auction_id
    ), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.get('/auctions/some_id/contracts/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])


def get_auction_contracts(self):

    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('id', response.json['data'][0])

    response = self.app.get('/auctions/some_id/contracts', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])


# Auction2LotContractResourceTest

def patch_auction_contract_2_lots(self):
    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id
    ),
        {'data':
            {'title': 'contract title',
             'description': 'contract description',
             'awardID': self.award_id}
         }
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    contract = response.json['data']

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(
        self.auction_id, contract['id']
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn(
        "Can't sign contract before stand-still period end (",
        response.json['errors'][0]["description"]
    )

    self.set_status('complete', {'status': 'active.awarded'})

    self.app.post_json('/auctions/{}/cancellations'.format(
        self.auction_id
    ), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(
        self.auction_id, contract['id']
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can update contract only in active lot status"
    )
