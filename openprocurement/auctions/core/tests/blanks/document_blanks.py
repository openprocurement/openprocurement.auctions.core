# -*- coding: utf-8 -*-
from email.header import Header

from openprocurement.api.utils import get_now

# AuctionDocumentResourceTest


def not_found(self):
    response = self.app.get('/auctions/some_id/documents', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.post('/auctions/some_id/documents', status=404, upload_files=[
        ('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.post('/auctions/{}/documents'.format(self.auction_id), status=404, upload_files=[
        ('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/some_id/documents/some_id', status=404, upload_files=[
        ('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.put('/auctions/{}/documents/some_id'.format(
        self.auction_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
    ])

    response = self.app.get('/auctions/some_id/documents/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/documents/some_id'.format(
        self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
    ])


def create_auction_document(self):
    if hasattr(self, 'dgf_platform_legal_details_from') and get_now() > self.dgf_platform_legal_details_from:
        response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 1)

    response = self.app.post('/auctions/{}/documents'.format(
        self.auction_id), upload_files=[('file', u'укр.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    if self.docservice:
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        auction = self.db.get(self.auction_id)
        self.assertIn(key, auction['documents'][-1]["url"])
        self.assertIn('Signature=', auction['documents'][-1]["url"])
        self.assertIn('KeyID=', auction['documents'][-1]["url"])
        self.assertNotIn('Expires=', auction['documents'][-1]["url"])
    else:
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual(u'укр.doc', response.json["data"][-1]["title"])

    response = self.app.get('/auctions/{}/documents/{}?download=some_id'.format(
        self.auction_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    if self.docservice:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)
    else:
        response = self.app.get('/auctions/{}/documents/{}?download=some_id'.format(
            self.auction_id, doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])

    response = self.app.post('/auctions/{}/documents?acc_token=acc_token'.format(
        self.auction_id), upload_files=[('file', u'укр.doc'.encode("ascii", "xmlcharrefreplace"), 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertNotIn('acc_token', response.headers['Location'])

    self.set_status('active.auction')

    response = self.app.post('/auctions/{}/documents'.format(
        self.auction_id), upload_files=[('file', u'укр.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add document in current (active.auction) auction status")


def put_auction_document(self):
    from six import BytesIO
    from urllib import quote
    body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n'''.format(
        u'\uff07')
    environ = self.app._make_environ()
    environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
    environ['REQUEST_METHOD'] = 'POST'
    req = self.app.RequestClass.blank(self.app._remove_fragment('/auctions/{}/documents'.format(self.auction_id)),
                                      environ)
    req.environ['wsgi.input'] = BytesIO(body.encode('utf8'))
    req.content_length = len(body)
    response = self.app.do_request(req, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "could not decode params")

    body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename*=utf-8''{}\nContent-Type: application/msword\n\ncontent\n'''.format(
        quote('укр.doc'))
    environ = self.app._make_environ()
    environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
    environ['REQUEST_METHOD'] = 'POST'
    req = self.app.RequestClass.blank(self.app._remove_fragment('/auctions/{}/documents'.format(self.auction_id)),
                                      environ)
    req.environ['wsgi.input'] = BytesIO(body.encode(req.charset or 'utf8'))
    req.content_length = len(body)
    response = self.app.do_request(req)
    # response = self.app.post('/auctions/{}/documents'.format(
    # self.auction_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    datePublished = response.json["data"]['datePublished']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id), upload_files=[('file', 'name  name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    if self.docservice:
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        auction = self.db.get(self.auction_id)
        self.assertIn(key, auction['documents'][-1]["url"])
        self.assertIn('Signature=', auction['documents'][-1]["url"])
        self.assertIn('KeyID=', auction['documents'][-1]["url"])
        self.assertNotIn('Expires=', auction['documents'][-1]["url"])
    else:
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    if self.docservice:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)
    else:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name name.doc', response.json["data"]["title"])
    dateModified2 = response.json["data"]['dateModified']
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])
    self.assertEqual(response.json["data"]['datePublished'], datePublished)

    response = self.app.get('/auctions/{}/documents?all=true'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified2, response.json["data"][-1]['dateModified'])

    response = self.app.post('/auctions/{}/documents'.format(
        self.auction_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified2, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified, response.json["data"][-1]['dateModified'])

    response = self.app.put('/auctions/{}/documents/{}'.format(self.auction_id, doc_id), status=404, upload_files=[
        ('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    if self.docservice:
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        auction = self.db.get(self.auction_id)
        self.assertIn(key, auction['documents'][-1]["url"])
        self.assertIn('Signature=', auction['documents'][-1]["url"])
        self.assertIn('KeyID=', auction['documents'][-1]["url"])
        self.assertNotIn('Expires=', auction['documents'][-1]["url"])
    else:
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    if self.docservice:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)
    else:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

    self.set_status('active.auction')

    response = self.app.put('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update document in current (active.auction) auction status")


def patch_auction_document(self):
    if hasattr(self, 'dgf_platform_legal_details_from') and get_now() > self.dgf_platform_legal_details_from:
        response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(
            u'Місце та форма прийому заяв на участь в аукціоні та банківські реквізити для зарахування гарантійних внесків',
            response.json["data"][0]["title"])
        self.assertEqual('x_dgfPlatformLegalDetails', response.json["data"][0]["documentType"])
        doc_id = response.json["data"][0]['id']

        response = self.app.patch_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id), {"data": {
            'format': 'application/msword',
            "documentType": 'auctionNotice'
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'First document should be document with x_dgfPlatformLegalDetails documentType'],
             u'location': u'body', u'name': u'documents'}
        ])

    response = self.app.post('/auctions/{}/documents'.format(
        self.auction_id), upload_files=[('file', str(Header(u'укр.doc', 'utf-8')), 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    # dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id), {"data": {
        "documentOf": "lot"
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
    ])

    response = self.app.patch_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id), {"data": {
        "documentOf": "lot",
        "relatedItem": '0' * 32
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
    ])

    response = self.app.patch_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id), {"data": {
        "documentOf": "item",
        "relatedItem": '0' * 32
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'relatedItem should be one of items'], u'location': u'body', u'name': u'relatedItem'}
    ])

    response = self.app.patch_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id), {"data": {
        "description": "document description",
        "documentType": 'auctionNotice'
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("documentType", response.json["data"])
    self.assertEqual(response.json["data"]["documentType"], 'auctionNotice')

    response = self.app.patch_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id), {"data": {
        "documentType": None
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.get('/auctions/{}/documents/{}'.format(self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])
    # self.assertTrue(dateModified < response.json["data"]["dateModified"])

    self.set_status('active.auction')

    response = self.app.patch_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
                                   {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update document in current (active.auction) auction status")

# AuctionDocumentWithDSResourceTest


def create_auction_document_json_invalid(self):
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "This field is required.")

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': '0' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Hash type is not supported.'], u'location': u'body', u'name': u'hash'}
    ])

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': 'sha2048:' + '0' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Hash type is not supported.'], u'location': u'body', u'name': u'hash'}
    ])

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': 'sha512:' + '0' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Hash value is wrong length.'], u'location': u'body', u'name': u'hash'}
    ])

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + 'O' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Hash value is not hexadecimal.'], u'location': u'body', u'name': u'hash'}
    ])

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': 'http://invalid.docservice.url/get/uuid',
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': '/'.join(self.generate_docservice_url().split('/')[:4]),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url().split('?')[0],
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add document only from document service.")

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url().replace(self.app.app.registry.keyring.keys()[-1], '0' * 8),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Document url expired.")

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url().replace("Signature=", "Signature=ABC"),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Document url signature invalid.")

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url().replace("Signature=", "Signature=bw%3D%3D"),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Document url invalid.")


def create_auction_document_json(self):
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    self.assertIn('Signature=', response.json["data"]["url"])
    self.assertIn('KeyID=', response.json["data"]["url"])
    self.assertNotIn('Expires=', response.json["data"]["url"])
    key = response.json["data"]["url"].split('/')[-1].split('?')[0]
    auction = self.db.get(self.auction_id)
    self.assertIn(key, auction['documents'][-1]["url"])
    self.assertIn('Signature=', auction['documents'][-1]["url"])
    self.assertIn('KeyID=', auction['documents'][-1]["url"])
    self.assertNotIn('Expires=', auction['documents'][-1]["url"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual(u'укр.doc', response.json["data"][-1]["title"])

    response = self.app.get('/auctions/{}/documents/{}?download=some_id'.format(
        self.auction_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
        self.auction_id, doc_id, key))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertNotIn('Expires=', response.location)

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])

    self.set_status('active.auction')

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.auction) auction status")


def put_auction_document_json(self):
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    datePublished = response.json["data"]['datePublished']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn('Signature=', response.json["data"]["url"])
    self.assertIn('KeyID=', response.json["data"]["url"])
    self.assertNotIn('Expires=', response.json["data"]["url"])
    key = response.json["data"]["url"].split('/')[-1].split('?')[0]
    auction = self.db.get(self.auction_id)
    self.assertIn(key, auction['documents'][-1]["url"])
    self.assertIn('Signature=', auction['documents'][-1]["url"])
    self.assertIn('KeyID=', auction['documents'][-1]["url"])
    self.assertNotIn('Expires=', auction['documents'][-1]["url"])

    response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
        self.auction_id, doc_id, key))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertNotIn('Expires=', response.location)

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'name.doc', response.json["data"]["title"])
    dateModified2 = response.json["data"]['dateModified']
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])
    self.assertEqual(response.json["data"]['datePublished'], datePublished)

    response = self.app.get('/auctions/{}/documents?all=true'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified2, response.json["data"][-1]['dateModified'])

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id, doc_id),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified2, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified, response.json["data"][-1]['dateModified'])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn('Signature=', response.json["data"]["url"])
    self.assertIn('KeyID=', response.json["data"]["url"])
    self.assertNotIn('Expires=', response.json["data"]["url"])
    key = response.json["data"]["url"].split('/')[-1].split('?')[0]
    auction = self.db.get(self.auction_id)
    self.assertIn(key, auction['documents'][-1]["url"])
    self.assertIn('Signature=', auction['documents'][-1]["url"])
    self.assertIn('KeyID=', auction['documents'][-1]["url"])
    self.assertNotIn('Expires=', auction['documents'][-1]["url"])

    response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
        self.auction_id, doc_id, key))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertNotIn('Expires=', response.location)

    self.set_status('active.auction')

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'укр.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.auction) auction status")


def create_auction_document_pas(self):
    pas_url = 'http://torgi.fg.gov.ua/id_of_lot'
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
                                  {'data': {
                                      'title': u'PAS for auction lot',
                                      'url': pas_url,
                                      'documentType': 'x_dgfPublicAssetCertificate',
                                  }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('PAS for auction lot', response.json["data"]["title"])
    self.assertEqual(pas_url, response.json["data"]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual('PAS for auction lot', auction['documents'][-1]["title"])
    self.assertEqual(pas_url, auction['documents'][-1]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual('PAS for auction lot', response.json["data"][-1]["title"])
    self.assertEqual(pas_url, response.json["data"][-1]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', response.json["data"][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents/{}?download=1'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertEqual(pas_url, response.location)

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('PAS for auction lot', response.json["data"]["title"])
    self.assertEqual(pas_url, response.json["data"]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', response.json["data"]["documentType"])

    self.set_status('active.auction')

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
                                  {'data': {
                                      'title': u'PAS for auction lot',
                                      'url': pas_url,
                                      'documentType': 'x_dgfPublicAssetCertificate',
                                  }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                 "Can't add document in current (active.auction) auction status")


def put_auction_document_pas(self):
    pas_url = 'http://torgi.fg.gov.ua/id_of_lot'
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'PAS for auction lot',
            'url': pas_url,
            'documentType': 'x_dgfPublicAssetCertificate',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual('PAS for auction lot', response.json["data"]["title"])
    self.assertEqual(pas_url, response.json["data"]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', response.json["data"]["documentType"])
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    dateModified = response.json["data"]['dateModified']
    datePublished = response.json["data"]['datePublished']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'name.doc',
            'url': self.generate_docservice_url(),
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'format'}
    ])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'url': [u'Not a well formed URL.'], u'hash': [u'This field is not required.'], u'format': [u'This field is not required.']}], u'location': u'body', u'name': u'documents'}
    ])

    pas_url = 'http://torgi.fg.gov.ua/new_id_of_lot'
    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'PAS for auction lot #2',
            'url': pas_url,
            'documentType': 'x_dgfPublicAssetCertificate',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('PAS for auction lot #2', response.json["data"]["title"])
    self.assertEqual(pas_url, response.json["data"]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual('PAS for auction lot #2', auction['documents'][-1]["title"])
    self.assertEqual(pas_url, auction['documents'][-1]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual('PAS for auction lot #2', response.json["data"][-1]["title"])
    self.assertEqual(pas_url, response.json["data"][-1]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', response.json["data"][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents/{}?download=1'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertEqual(pas_url, response.location)

    response = self.app.get('/auctions/{}/documents/{}'.format(self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('PAS for auction lot #2', response.json["data"]["title"])
    dateModified2 = response.json["data"]['dateModified']
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])
    self.assertEqual(response.json["data"]['datePublished'], datePublished)

    response = self.app.get('/auctions/{}/documents?all=true'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified2, response.json["data"][-1]['dateModified'])

    pas_url = 'http://torgi.fg.gov.ua/new_new_id_of_lot'
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'PAS for auction lot #3',
            'url': pas_url,
            'documentType': 'x_dgfPublicAssetCertificate',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified2, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified, response.json["data"][-1]['dateModified'])

    pas_url = 'http://torgi.fg.gov.ua/new_new_new_id_of_lot'
    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'PAS for auction lot #4',
            'url': pas_url,
            'documentType': 'x_dgfPublicAssetCertificate',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('PAS for auction lot #4', response.json["data"]["title"])
    self.assertEqual(pas_url, response.json["data"]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual('PAS for auction lot #4', auction['documents'][-1]["title"])
    self.assertEqual(pas_url, auction['documents'][-1]["url"])
    self.assertEqual('x_dgfPublicAssetCertificate', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents/{}?download=1'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertEqual(pas_url, response.location)

    self.set_status('active.auction')

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'PAS for auction lot #5',
            'url': pas_url,
            'documentType': 'x_dgfPublicAssetCertificate',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.auction) auction status")


def create_auction_offline_document(self):
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних', response.json["data"]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual(u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних', auction['documents'][-1]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', auction['documents'][-1]["accessDetails"])
    self.assertEqual('offline/on-site-examination', auction['documents'][-1]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних', response.json["data"][-1]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"][-1]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"][-1]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"][-1]["documentType"])


    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних', response.json["data"]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])

    self.set_status('active.auction')

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.auction) auction status")


def put_auction_offline_document(self):
    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних', response.json["data"]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])
    dateModified = response.json["data"]['dateModified']
    datePublished = response.json["data"]['datePublished']

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Новий порядок ознайомлення',
            'documentType': 'x_dgfAssetFamiliarization',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'accessDetails'}
    ])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Новий порядок ознайомлення',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс',
            'hash': 'md5:' + '0' * 32,
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [{'description': [u'This field is not required.'], u'location': u'body', u'name': u'hash'}])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном #2',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном #2', response.json["data"]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual(u'Порядок ознайомлення з майном #2', auction['documents'][-1]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', auction['documents'][-1]["accessDetails"])
    self.assertEqual('offline/on-site-examination', auction['documents'][-1]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном #2', response.json["data"][-1]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"][-1]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"][-1]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents/{}'.format(self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном #2', response.json["data"]["title"])
    dateModified2 = response.json["data"]['dateModified']
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])
    self.assertEqual(response.json["data"]['datePublished'], datePublished)

    response = self.app.get('/auctions/{}/documents?all=true'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified2, response.json["data"][-1]['dateModified'])

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном #3',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified2, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified, response.json["data"][-1]['dateModified'])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном #4',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном #4', response.json["data"]["title"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual(u'Порядок ознайомлення з майном #4', auction['documents'][-1]["title"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])

    self.set_status('active.auction')

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном #5',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.auction) auction status")


def create_auction_document_vdr(self):
    vdr_url = 'http://virtial-data-room.com/id_of_room'
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'VDR for auction lot',
            'url': vdr_url,
            'documentType': 'virtualDataRoom',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('VDR for auction lot', response.json["data"]["title"])
    self.assertEqual(vdr_url, response.json["data"]["url"])
    self.assertEqual('virtualDataRoom', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual('VDR for auction lot', auction['documents'][-1]["title"])
    self.assertEqual(vdr_url, auction['documents'][-1]["url"])
    self.assertEqual('virtualDataRoom', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual('VDR for auction lot', response.json["data"][-1]["title"])
    self.assertEqual(vdr_url, response.json["data"][-1]["url"])
    self.assertEqual('virtualDataRoom', response.json["data"][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents/{}?download=1'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertEqual(vdr_url, response.location)

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('VDR for auction lot', response.json["data"]["title"])
    self.assertEqual(vdr_url, response.json["data"]["url"])
    self.assertEqual('virtualDataRoom', response.json["data"]["documentType"])

    self.set_status('active.auction')

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'VDR for auction lot',
            'url': vdr_url,
            'documentType': 'virtualDataRoom',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.auction) auction status")


def put_auction_document_vdr(self):
    vdr_url = 'http://virtial-data-room.com/id_of_room'
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'VDR for auction lot',
            'url': vdr_url,
            'documentType': 'virtualDataRoom',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual('VDR for auction lot', response.json["data"]["title"])
    self.assertEqual(vdr_url, response.json["data"]["url"])
    self.assertEqual('virtualDataRoom', response.json["data"]["documentType"])
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    dateModified = response.json["data"]['dateModified']
    datePublished = response.json["data"]['datePublished']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'name.doc',
            'url': self.generate_docservice_url(),
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'format'}
    ])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'url': [u'Not a well formed URL.'], u'hash': [u'This field is not required.'], u'format': [u'This field is not required.']}], u'location': u'body', u'name': u'documents'}
    ])

    vdr_url = 'http://virtial-data-room.com/new_id_of_room'
    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'VDR for auction lot #2',
            'url': vdr_url,
            'documentType': 'virtualDataRoom',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('VDR for auction lot #2', response.json["data"]["title"])
    self.assertEqual(vdr_url, response.json["data"]["url"])
    self.assertEqual('virtualDataRoom', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual('VDR for auction lot #2', auction['documents'][-1]["title"])
    self.assertEqual(vdr_url, auction['documents'][-1]["url"])
    self.assertEqual('virtualDataRoom', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual('VDR for auction lot #2', response.json["data"][-1]["title"])
    self.assertEqual(vdr_url, response.json["data"][-1]["url"])
    self.assertEqual('virtualDataRoom', response.json["data"][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents/{}?download=1'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertEqual(vdr_url, response.location)

    response = self.app.get('/auctions/{}/documents/{}'.format(self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('VDR for auction lot #2', response.json["data"]["title"])
    dateModified2 = response.json["data"]['dateModified']
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])
    self.assertEqual(response.json["data"]['datePublished'], datePublished)

    response = self.app.get('/auctions/{}/documents?all=true'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified2, response.json["data"][-1]['dateModified'])

    vdr_url = 'http://virtial-data-room.com/new_new_id_of_room'
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'VDR for auction lot #3',
            'url': vdr_url,
            'documentType': 'virtualDataRoom',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified2, response.json["data"][-2]['dateModified'])
    self.assertEqual(dateModified, response.json["data"][-1]['dateModified'])

    vdr_url = 'http://virtial-data-room.com/new_new_new_id_of_room'
    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'VDR for auction lot #4',
            'url': vdr_url,
            'documentType': 'virtualDataRoom',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('VDR for auction lot #4', response.json["data"]["title"])
    self.assertEqual(vdr_url, response.json["data"]["url"])
    self.assertEqual('virtualDataRoom', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual('VDR for auction lot #4', auction['documents'][-1]["title"])
    self.assertEqual(vdr_url, auction['documents'][-1]["url"])
    self.assertEqual('virtualDataRoom', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents/{}?download=1'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertEqual(vdr_url, response.location)

    self.set_status('active.auction')

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'VDR for auction lot #5',
            'url': vdr_url,
            'documentType': 'virtualDataRoom',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.auction) auction status")
