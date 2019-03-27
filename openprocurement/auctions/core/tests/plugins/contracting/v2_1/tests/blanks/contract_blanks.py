from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import JSON_RENDERER_ERROR
# AuctionContractResourceTest


def create_auction_contract_invalid(self):
    response = self.app.post_json('/auctions/some_id/contracts', {
        'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'auction_id'}
    ])

    request_path = '/auctions/{}/contracts'.format(self.auction_id)

    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
             u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
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

    response = self.app.post_json(request_path, {'data': {'awardID': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'awardID should be one of awards'], u'location': u'body', u'name': u'awardID'}
    ])


def create_auction_contract(self):
    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id,
                 'value': self.award_value, 'suppliers': self.award_suppliers}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    contract = response.json['data']
    self.assertIn('id', contract)
    self.assertIn('value', contract)
    self.assertIn('suppliers', contract)
    self.assertIn(contract['id'], response.headers['Location'])

    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "terminated"
    self.db.save(auction)

    self.set_status('unsuccessful')

    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}},
        status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add contract in current (unsuccessful) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (unsuccessful) auction status")



def create_auction_contract_in_complete_status(self):
    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    contract = response.json['data']
    self.assertIn('id', contract)
    self.assertIn(contract['id'], response.headers['Location'])

    auction = self.db.get(self.auction_id)
    auction['contracts'][-1]["status"] = "terminated"
    self.db.save(auction)

    self.set_status('complete')

    response = self.app.post_json('/auctions/{}/contracts'.format(
        self.auction_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}},
        status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']),
                                   {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")



def patch_auction_contract(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"contractID": "myselfID", "items": [{"description": "New Description"}],
                 "suppliers": [{"name": "New Name"}]}})

    response = self.app.get('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']))
    self.assertEqual(response.json['data']['contractID'], contract['contractID'])
    self.assertEqual(response.json['data']['items'], contract['items'])
    self.assertEqual(response.json['data']['suppliers'], contract['suppliers'])
    response = self.app.patch_json(
        '/auctions/{}/contracts/{}?acc_token={}'.format(
            self.auction_id, contract['id'], self.auction_token
        ),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(
        response.json["errors"][0]['description'],
        "Can't activate contract without value defined"
    )
    response = self.app.patch_json(
	'/auctions/{}/contracts/{}?acc_token={}'.format(
	    self.auction_id, contract['id'], self.auction_token
	),
	{
	    "data": {
		"value": {
		    "currency": "UAH",
		    "amount": 500,
		    "valueAddedTaxIncluded": True,
		}
	    }
	},
	status=200
    )
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"value": {"currency": "USD"}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"], "Can\'t update currency for contract value")

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
    self.assertEqual(response.json['errors'][0]["description"],
                     "Value amount should be greater or equal to awarded amount (479)")

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"value": {"amount": 501}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['value']['amount'], 501)

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"dateSigned": one_hour_in_furure}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Contract signature date can't be in the future"], u'location': u'body',
         u'name': u'dateSigned'}])

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"dateSigned": custom_signature_date}})
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"value": {"amount": 232}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"contractID": "myselfID"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"items": [{"description": "New Description"}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"suppliers": [{"name": "New Name"}]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update contract in current (complete) auction status")

    response = self.app.patch_json('/auctions/{}/contracts/some_id'.format(self.auction_id),
                                   {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'contract_id'}
    ])

    response = self.app.patch_json('/auctions/some_id/contracts/some_id', {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertEqual(response.json['data']["value"]['amount'], 501)
    self.assertEqual(response.json['data']['contractID'], contract['contractID'])
    self.assertEqual(response.json['data']['items'], contract['items'])
    self.assertEqual(response.json['data']['suppliers'], contract['suppliers'])
    self.assertEqual(response.json['data']['dateSigned'], custom_signature_date)


def get_auction_contract(self):
    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    contract = response.json['data'][0]

    response = self.app.get('/auctions/{}/contracts/{}'.format(self.auction_id, contract['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], contract)

    response = self.app.get('/auctions/{}/contracts/some_id'.format(self.auction_id), status=404)
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
    contract = response.json['data'][0]

    response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][-1], contract)

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
        self.auction_id),
        {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    contract = response.json['data']

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn("Can't sign contract before stand-still period end (", response.json['errors'][0]["description"])

    self.set_status('complete', {'status': 'active.awarded'})

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})

    response = self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(
        self.auction_id, contract['id'], self.auction_token
    ), {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update contract only in active lot status")
