# -*-coding: utf-8 -*-
from hashlib import sha512

from copy import deepcopy


def change_resource_ownership(self):
    change_ownership_url = '/auctions/{}/ownership'
    post = self.app.post_json

    req_data = {"data": {"id": 1984}}
    response = post(change_ownership_url.format(self.auction_id), req_data, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['errors'], [
        {u'description': u'This field is required.',
         u'location': u'body', u'name': u'transfer'}
    ])

    auction = self.get_auction(self.auction_id)
    self.assertEqual(auction['data']['owner'], self.first_owner)

    self.app.authorization = ('Basic', (self.second_owner, ''))

    transfer = self.create_transfer()

    req_data = {"data": {"id": transfer['data']['id'],
                         'transfer': self.auction_transfer}}

    response = post(change_ownership_url.format(self.auction_id), req_data)
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('transfer', response.json['data'])
    self.assertNotIn('transfer_token', response.json['data'])
    self.assertEqual(self.second_owner, response.json['data']['owner'])


def resource_location_in_transfer(self):

    used_transfer = self.use_transfer(self.not_used_transfer,
                                      self.auction_id,
                                      self.auction_transfer)

    transfer_creation_date = self.not_used_transfer['data']['date']
    transfer_modification_date = used_transfer['data']['date']

    self.assertEqual(used_transfer['data']['usedFor'], '/auctions/' + self.auction_id)
    self.assertNotEqual(transfer_creation_date, transfer_modification_date)


def already_applied_transfer(self):
    auth = ('Basic', (self.first_owner, ''))
    auction_wich_use_transfer = self.create_auction_unit(auth=auth)
    auction_wich_want_to_use_transfer = self.create_auction_unit(auth=auth)
    transfer = self.create_transfer()
    self.use_transfer(transfer,
                      auction_wich_use_transfer['data']['id'],
                      auction_wich_use_transfer['access']['transfer'])

    req_data = {"data": {"id": transfer['data']['id'],
                         'transfer': auction_wich_want_to_use_transfer['access']['transfer']}}
    req_url = '/auctions/{}/ownership'.format(auction_wich_want_to_use_transfer['data']['id'])
    response = self.app.post_json(req_url, req_data, status=403)

    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Transfer already used',
         u'location': u'body',
         u'name': u'transfer'}])


def half_applied_transfer(self):
    # simulate half-applied transfer activation process (i.e. transfer
    # is successfully applied to a auction and relation is saved in transfer,
    # but tender is not stored with new credentials)


    auth = ('Basic', (self.first_owner, ''))
    auction = self.create_auction_unit(auth=auth)

    self.app.authorization = ('Basic', (self.second_owner, ''))
    transfer = self.create_transfer()
    transfer_doc = self.db.get(transfer['data']['id'])

    transfer_doc['usedFor'] = '/auctions/' + auction['data']['id']
    self.db.save(transfer_doc)

    self.use_transfer(transfer,
                      auction['data']['id'],
                      auction['access']['transfer'])

    auction_wich_used_transfer = self.get_auction(auction['data']['id'])
    self.assertEqual(self.second_owner, auction_wich_used_transfer['data']['owner'])


def new_owner_can_change(self):
    auth = ('Basic', (self.first_owner, ''))
    auction = self.create_auction_unit(auth=auth)

    self.app.authorization = ('Basic', (self.second_owner, ''))
    transfer = self.create_transfer()
    self.use_transfer(transfer,
                      auction['data']['id'],
                      auction['access']['transfer'])

    new_access_token = transfer['access']['token']

    # second_owner can change the auction
    desc = "second_owner now can change the tender"
    req_data = {"data": {"description": desc}}
    req_url = '/auctions/{}?acc_token={}'.format(auction['data']['id'], new_access_token)
    response = self.app.patch_json(req_url, req_data)

    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('transfer', response.json['data'])
    self.assertNotIn('transfer_token', response.json['data'])
    self.assertIn('owner', response.json['data'])
    self.assertEqual(response.json['data']['description'], desc)
    self.assertEqual(response.json['data']['owner'], self.second_owner)


def old_owner_cant_change(self):
    auth = ('Basic', (self.first_owner, ''))
    auction = self.create_auction_unit(auth=auth)

    self.app.authorization = ('Basic', (self.second_owner, ''))
    transfer = self.create_transfer()
    self.use_transfer(transfer,
                      auction['data']['id'],
                      auction['access']['transfer'])

    # fist_owner can`t change the auction
    desc = "make auction greate again"
    req_data = {"data": {"description": desc}}
    req_url = '/auctions/{}?acc_token={}'.format(
        auction['data']['id'], auction['access']['token']
    )
    response = self.app.patch_json(req_url, req_data, status=403)
    self.assertEqual(response.status, '403 Forbidden')


def broker_not_accreditation_level(self):
    # try to use transfer by broker without appropriate accreditation level
    self.app.authorization = ('Basic', (self.invalid_owner, ''))

    transfer = self.create_transfer()
    req_data = {"data": {"id": transfer['data']['id'],
                         'transfer': self.auction_transfer}}
    req_url = '/auctions/{}/ownership'.format(self.auction_id)

    response = self.app.post_json(req_url, req_data, status=403)

    self.assertEqual(response.json['errors'], [
        {u'description': u'Broker Accreditation level does not permit ownership change',
         u'location': u'body', u'name': u'data'}])


def level_permis(self):
    # test level permits to change ownership for 'test' auctions

    self.app.authorization = ('Basic', (self.test_owner, ''))
    transfer = self.create_transfer()

    req_data = {"data": {"id": transfer['data']['id'],
                         'transfer': self.auction_transfer}}
    req_url = '/auctions/{}/ownership'.format(self.auction_id)

    response = self.app.post_json(req_url, req_data, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Broker Accreditation level does not permit ownership change',
         u'location': u'body', u'name': u'data'}])


def switch_mode(self):
    # set test mode and try to change ownership

    auth = ('Basic', (self.first_owner, ''))
    auction = self.create_auction_unit(auth=auth)

    self.set_auction_mode(auction['data']['id'], 'test')

    self.app.authorization = ('Basic', (self.test_owner, ''))
    transfer = self.create_transfer()

    req_data = {"data": {"id": transfer['data']['id'],
                         'transfer': auction['access']['transfer']}}
    req_url = '/auctions/{}/ownership'.format(auction['data']['id'])

    response = self.app.post_json(req_url, req_data)

    self.assertEqual(response.status, '200 OK')
    self.assertIn('owner', response.json['data'])
    self.assertEqual(response.json['data']['owner'], self.test_owner)


def create_auction_by_concierge(self):
    self.app.authorization = ('Basic', (self.concierge, ''))
    transfer_token = sha512(self.not_used_transfer['access']['transfer']).hexdigest()
    headers = {'X-Transfer-Token': transfer_token}
    data = deepcopy(self.initial_data)

    # passing SHA-512 hash of transfer token as a header
    response = self.app.post_json('/auctions', {'data': data}, headers=headers)
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('transfer', response.json['access'])
    auction_id = response.json['data']['id']

    self.app.authorization = ('Basic', (self.first_owner, ''))

    transfer = self.create_transfer()

    # trying to change ownership
    self.use_transfer(transfer,
                      auction_id,
                      self.not_used_transfer['access']['transfer'])

    # assuring that transfer is used properly
    response = self.app.get('/transfers/{}'.format(transfer['data']['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['data']['usedFor'], '/auctions/{}'.format(auction_id)
    )

    # assuring that ownership changed successfully
    auction = self.db.get(auction_id)
    self.assertEqual(auction['owner'], self.app.authorization[1][0])
