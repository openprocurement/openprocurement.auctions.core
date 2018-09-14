# AuctionBidderDocumentResourceTestMixin


def not_found(self):
    response = self.app.post('/auctions/some_id/bids/some_id/documents', status=404, upload_files=[
                             ('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.post('/auctions/{}/bids/some_id/documents'.format(self.auction_id), status=404, upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.post('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token),
        status=404, upload_files=[('invalid_value', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.get('/auctions/some_id/bids/some_id/documents', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/bids/some_id/documents'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.get('/auctions/some_id/bids/some_id/documents/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/bids/some_id/documents/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.get('/auctions/{}/bids/{}/documents/some_id'.format(self.auction_id, self.bid_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'document_id'}
    ])

    response = self.app.put('/auctions/some_id/bids/some_id/documents/some_id', status=404,
                            upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.put('/auctions/{}/bids/some_id/documents/some_id'.format(self.auction_id), status=404, upload_files=[
                            ('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.put('/auctions/{}/bids/{}/documents/some_id'.format(
        self.auction_id, self.bid_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
    ])

    self.app.authorization = ('Basic', ('invalid', ''))
    response = self.app.put('/auctions/{}/bids/{}/documents/some_id'.format(
        self.auction_id, self.bid_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
    ])


def create_auction_bidder_document(self):
    response = self.app.post('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    response = self.app.get('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid documents in current (active.tendering) auction status")

    response = self.app.get('/auctions/{}/bids/{}/documents?acc_token={}'.format(self.auction_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/bids/{}/documents?all=true&acc_token={}'.format(self.auction_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?download=some_id&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}'.format(
        self.auction_id, self.bid_id, doc_id, key), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) auction status")

    if self.docservice:
        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)
    else:
        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/bids/{}/documents/{}'.format(
        self.auction_id, self.bid_id, doc_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) auction status")

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    self.set_status('active.awarded', {'status': 'active.tendering'})

    response = self.app.post('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn("Document can be added only during the tendering period: from", response.json['errors'][0]["description"])

    self.set_status('active.awarded')

    response = self.app.post('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.awarded) auction status")

    response = self.app.get('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    if self.docservice:
        self.assertIn('http://localhost/get/', response.json['data']['url'])
        self.assertIn('Signature=', response.json['data']['url'])
        self.assertIn('KeyID=', response.json['data']['url'])
        self.assertNotIn('Expires=', response.json['data']['url'])
    else:
        self.assertIn('download=', response.json['data']['url'])

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, key, self.bid_token))
    if self.docservice:
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)
    else:
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')


def put_auction_bidder_document(self):
    response = self.app.post('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ), status=404, upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, key, self.bid_token))
    if self.docservice:
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)
    else:
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, key, self.bid_token))
    if self.docservice:
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)
    else:
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

    self.set_status('active.awarded')

    response = self.app.put('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.awarded) auction status")


def patch_auction_bidder_document(self):
    response = self.app.post('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ), {"data": {
        "documentOf": "lot"
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
    ])

    response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ), {"data": {
            "documentOf": "lot",
            "relatedItem": '0' * 32
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
    ])

    response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    self.set_status('active.awarded')

    response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.awarded) auction status")

# AuctionBidderDocumentWithDSResourceTest


def create_auction_bidder_document_json(self):
    response = self.app.post_json('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    response = self.app.get('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid documents in current (active.tendering) auction status")

    response = self.app.get('/auctions/{}/bids/{}/documents?acc_token={}'.format(self.auction_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/bids/{}/documents?all=true&acc_token={}'.format(self.auction_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?download=some_id&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}'.format(
        self.auction_id, self.bid_id, doc_id, key), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) auction status")

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, key, self.bid_token))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertIn('Expires=', response.location)

    response = self.app.get('/auctions/{}/bids/{}/documents/{}'.format(
        self.auction_id, self.bid_id, doc_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) auction status")

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.post_json('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn(response.json["data"]['id'], response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])

    self.set_status('active.awarded')

    response = self.app.post_json('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.awarded) auction status")

    response = self.app.get('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('http://localhost/get/', response.json['data']['url'])
    self.assertIn('Signature=', response.json['data']['url'])
    self.assertIn('KeyID=', response.json['data']['url'])
    self.assertNotIn('Expires=', response.json['data']['url'])

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, key, self.bid_token))
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertIn('Expires=', response.location)


def put_auction_bidder_document_json(self):
    response = self.app.post_json('/auctions/{}/bids/{}/documents?acc_token={}'.format(
        self.auction_id, self.bid_id, self.bid_token
    ),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put_json('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, key, self.bid_token))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertIn('Expires=', response.location)

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put_json('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/auctions/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, key, self.bid_token))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertIn('Expires=', response.location)

    self.set_status('active.awarded')

    response = self.app.put_json('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.auction_id, self.bid_id, doc_id, self.bid_token
    ),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.awarded) auction status")

# AuctionBidderResourceTest


def create_auction_bidder(self):
    dateModified = self.db.get(self.auction_id).get('dateModified')

    if getattr(self, 'test_financial_organization', None) and self.initial_organization == self.test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True,
                     'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id),
            {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']
    self.assertEqual(bidder['tenderers'][0]['name'], self.initial_organization['name'])
    self.assertIn('id', bidder)
    self.assertIn(bidder['id'], response.headers['Location'])

    self.assertEqual(self.db.get(self.auction_id).get('dateModified'), dateModified)

    self.set_status('complete')

    if getattr(self, 'test_financial_organization', None) and self.initial_organization == self.test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True,
                     'eligible': True}}, status=403)
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id),
            {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}},
            status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (complete) auction status")

# AuctionBidderFeaturesResourceTest


def features_bidder_invalid(self):
    data = {
        "tenderers": [
            self.initial_organization
        ],
        "value": {
            "amount": 469,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    }
    response = self.app.post_json('/auctions/{}/bids'.format(self.auction_id), {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'parameters'}
    ])
    data["parameters"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "value": 0.1,
        }
    ]
    response = self.app.post_json('/auctions/{}/bids'.format(self.auction_id), {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])
    data["parameters"].append({
        "code": "OCDS-123454-AIR-INTAKE",
        "value": 0.1,
    })
    response = self.app.post_json('/auctions/{}/bids'.format(self.auction_id), {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Parameter code should be uniq for all parameters'], u'location': u'body',
         u'name': u'parameters'}
    ])
    data["parameters"][1]["code"] = "OCDS-123454-YEARS"
    data["parameters"][1]["value"] = 0.2
    response = self.app.post_json('/auctions/{}/bids'.format(self.auction_id), {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'value should be one of feature value.']}], u'location': u'body',
         u'name': u'parameters'}
    ])
