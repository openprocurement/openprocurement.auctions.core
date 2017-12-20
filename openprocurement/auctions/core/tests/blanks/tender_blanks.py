from uuid import uuid4


def empty_listing(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertNotIn('{\n    "', response.body)
    self.assertNotIn('callback({', response.body)
    self.assertEqual(response.json['next_page']['offset'], '')
    self.assertNotIn('prev_page', response.json)

    response = self.app.get('/auctions?opt_jsonp=callback')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertNotIn('{\n    "', response.body)
    self.assertIn('callback({', response.body)

    response = self.app.get('/auctions?opt_pretty=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)
    self.assertNotIn('callback({', response.body)

    response = self.app.get('/auctions?opt_jsonp=callback&opt_pretty=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('{\n    "', response.body)
    self.assertIn('callback({', response.body)

    response = self.app.get('/auctions?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertIn('descending=1', response.json['next_page']['uri'])
    self.assertIn('limit=10', response.json['next_page']['uri'])
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertIn('limit=10', response.json['prev_page']['uri'])

    response = self.app.get('/auctions?feed=changes')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertEqual(response.json['next_page']['offset'], '')
    self.assertNotIn('prev_page', response.json)

    response = self.app.get('/auctions?feed=changes&offset=0', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Offset expired/invalid', u'location': u'params', u'name': u'offset'}
    ])

    response = self.app.get('/auctions?feed=changes&descending=1&limit=10')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], [])
    self.assertIn('descending=1', response.json['next_page']['uri'])
    self.assertIn('limit=10', response.json['next_page']['uri'])
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertIn('limit=10', response.json['prev_page']['uri'])


def create_auction_draft_with_registry(self):
    data = self.initial_data.copy()
    items = data.pop('items')
    dgf_id = data.pop('dgfID')
    data.update({'status': 'draft', 'merchandisingObject': uuid4().hex})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'draft')

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'value': {'amount': 100}}},
                                   status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"Can't update auction in current (draft) status", u'location': u'body', u'name': u'data'}
    ])

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'pending.verification'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'pending.verification')

    self.app.authorization = ('Basic', ('convoy', ''))
    response = self.app.patch_json('/auctions/{}'.format(auction['id']),
                                   {'data': {'items': items, 'dgfID': dgf_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']['items']), len(items))
    self.assertEqual(response.json['data']['dgfID'], dgf_id)

    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'active.tendering')

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'active.tendering')


def convoy_change_status(self):
    # Check auctions list count
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    # Create auction without merchandisingObject
    data = self.initial_data.copy()
    data.update({'status': 'draft'})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner
    # without merchandisingObject
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'pending.verification'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': u"Can't switch auction to status (pending.verification) without merchandisingObject", u'location': u'body', u'name': u'data'}])

    # Create auction with items
    data.update({'merchandisingObject': uuid4().hex})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner
    # with items
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token),
                                   {'data': {'status': 'pending.verification'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"This field is not required.",
         u'location': u'body', u'name': u'items'}])


    # Create auction with merchandisingObject and without items and without dgfID
    data = self.initial_data.copy()
    data.update({'status': 'draft', 'merchandisingObject': uuid4().hex})
    items = data.pop('items')
    dgf_id = data.pop('dgfID')
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'pending.verification'}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'pending.verification')

    self.app.authorization = ('Basic', ('convoy', ''))

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'pending.verification' -> 'active.tendering' via convoy without items and dgfID
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"This field is required."],
         u'location': u'body', u'name': u'items'},
        {u'description': [u"This field is required."],
         u'location': u'body', u'name': u'dgfID'}])

    # Add items and dgfID via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'items': items, 'dgfID': dgf_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']['items']), len(items))
    self.assertEqual(response.json['data']['dgfID'], dgf_id)

    # Switch auction status 'pending.verification' -> 'active.tendering' via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'active.tendering')

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'active.tendering' -> 'invalid' via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'invalid'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': u"Can't update auction in current (active.tendering) status", u'location': u'body', u'name': u'data'}])

    # Create auction with merchandisingObject
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'pending.verification'}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'pending.verification')

    self.app.authorization = ('Basic', ('convoy', ''))
    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'pending.verification' -> 'invalid' via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'invalid'}})
    self.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    self.assertEqual(auction['status'], 'invalid')

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'invalid' -> 'active.tendering' via convoy
    response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': u"Can't update auction in current (invalid) status", u'location': u'body', u'name': u'data'}])

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Create auction with merchandisingObject and without items and with dgfID
    self.app.authorization = ('Basic', ('broker', ''))
    data = self.initial_data.copy()
    data.update({'status': 'draft', 'merchandisingObject': uuid4().hex})
    data.pop('items')
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    auction = response.json['data']
    owner_token = response.json['access']['token']

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], auction)

    # Switch auction status 'draft' -> 'pending.verification' via owner with dgfID
    response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'pending.verification'}},
                                   status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"This field is not required.",
         u'location': u'body', u'name': u'dgfID'}])
