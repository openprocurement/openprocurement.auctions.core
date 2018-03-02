# -*- coding: utf-8 -*-

# AuctionQuestionResourceTest


def create_auction_question_invalid(self):
    response = self.app.post_json('/auctions/some_id/questions', {
        'data': {'title': 'question title', 'description': 'question description',
                 'author': self.initial_organization}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'auction_id'}
    ])

    request_path = '/auctions/{}/questions'.format(self.auction_id)

    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
             u"Content-Type header should be one of ['application/json']", u'location': u'header',
         u'name': u'Content-Type'}
    ])

    response = self.app.post(
        request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Expecting value: line 1 column 1 (char 0)',
         u'location': u'body', u'name': u'data'}
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

    response = self.app.post_json(request_path, {'data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(len(response.json['errors']), 2)
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
                  response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'author'},
                  response.json['errors'])

    response = self.app.post_json(request_path, {'data': {
        'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'author': {'identifier': 'invalid_value'}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {
            u'identifier': [u'Please use a mapping for this field or Identifier instance instead of unicode.']},
         u'location': u'body', u'name': u'author'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'title': 'question title', 'description': 'question description', 'author': {'identifier': {}}}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'contactPoint': [u'This field is required.'],
                          u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.']},
                          u'name': [u'This field is required.'], u'address': [u'This field is required.']},
         u'location': u'body', u'name': u'author'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'title': 'question title', 'description': 'question description', 'author': {
            'name': 'name', 'identifier': {'uri': 'invalid_value'}}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'contactPoint': [u'This field is required.'],
                          u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.'],
                                          u'uri': [u'Not a well formed URL.']},
                          u'address': [u'This field is required.']}, u'location': u'body', u'name': u'author'}
    ])

    response = self.app.post_json('/auctions/{}/questions'.format(self.auction_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        'author': self.initial_organization,
        "questionOf": "lot"
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'}
    ])

    response = self.app.post_json('/auctions/{}/questions'.format(self.auction_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        'author': self.initial_organization,
        "questionOf": "lot",
        "relatedItem": '0' * 32
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
    ])

    response = self.app.post_json('/auctions/{}/questions'.format(self.auction_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        'author': self.initial_organization,
        "questionOf": "item",
        "relatedItem": '0' * 32
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'relatedItem should be one of items'], u'location': u'body', u'name': u'relatedItem'}
    ])


def create_auction_question(self):
    response = self.app.post_json('/auctions/{}/questions'.format(
        self.auction_id), {'data': {'title': 'question title', 'description': 'question description',
                                    'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']
    self.assertEqual(question['author']['name'], self.initial_organization['name'])
    self.assertIn('id', question)
    self.assertIn(question['id'], response.headers['Location'])

    self.set_status('active.auction')

    response = self.app.post_json('/auctions/{}/questions'.format(
        self.auction_id), {'data': {'title': 'question title', 'description': 'question description',
                                    'author': self.initial_organization}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")


def patch_auction_question(self):
    response = self.app.post_json('/auctions/{}/questions'.format(
        self.auction_id), {'data': {'title': 'question title', 'description': 'question description',
                                    'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.patch_json('/auctions/{}/questions/{}'.format(self.auction_id, question['id']),
                                   {"data": {"answer": "answer"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["answer"], "answer")

    response = self.app.patch_json('/auctions/{}/questions/some_id'.format(self.auction_id),
                                   {"data": {"answer": "answer"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'question_id'}
    ])

    response = self.app.patch_json('/auctions/some_id/questions/some_id', {"data": {"answer": "answer"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.get('/auctions/{}/questions/{}'.format(self.auction_id, question['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["answer"], "answer")

    self.set_status('active.auction')

    response = self.app.patch_json('/auctions/{}/questions/{}'.format(self.auction_id, question['id']),
                                   {"data": {"answer": "answer"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update question in current (active.auction) auction status")


def get_auction_question(self):
    response = self.app.post_json('/auctions/{}/questions'.format(
        self.auction_id), {'data': {'title': 'question title', 'description': 'question description',
                                    'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.get('/auctions/{}/questions/{}'.format(self.auction_id, question['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set([u'id', u'date', u'title', u'description', u'questionOf']))

    self.set_status('active.qualification')

    response = self.app.get('/auctions/{}/questions/{}'.format(self.auction_id, question['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], question)

    response = self.app.get('/auctions/{}/questions/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'question_id'}
    ])

    response = self.app.get('/auctions/some_id/questions/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])


def get_auction_questions(self):
    response = self.app.post_json('/auctions/{}/questions'.format(
        self.auction_id), {'data': {'title': 'question title', 'description': 'question description',
                                    'author': self.initial_organization}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.get('/auctions/{}/questions'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'date', u'title', u'description', u'questionOf']))

    self.set_status('active.qualification')

    response = self.app.get('/auctions/{}/questions'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][0], question)

    response = self.app.get('/auctions/some_id/questions', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

# AuctionLotQuestionResourceTest


def create_auction_question_lot(self):
    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.post_json('/auctions/{}/questions'.format(self.auction_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        "questionOf": "lot",
        "relatedItem": self.initial_lots[0]['id'],
        'author': self.initial_organization
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add question only in active lot status")

    response = self.app.post_json('/auctions/{}/questions'.format(self.auction_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        "questionOf": "lot",
        "relatedItem": self.initial_lots[1]['id'],
        'author': self.initial_organization
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']
    self.assertEqual(question['author']['name'], self.initial_organization['name'])
    self.assertIn('id', question)
    self.assertIn(question['id'], response.headers['Location'])


def patch_auction_question_lot(self):
    response = self.app.post_json('/auctions/{}/questions'.format(self.auction_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        "questionOf": "lot",
        "relatedItem": self.initial_lots[0]['id'],
        'author': self.initial_organization
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.post_json('/auctions/{}/cancellations'.format(self.auction_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json('/auctions/{}/questions/{}'.format(self.auction_id, question['id']),
                                   {"data": {"answer": "answer"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update question only in active lot status")

    response = self.app.post_json('/auctions/{}/questions'.format(self.auction_id), {'data': {
        'title': 'question title',
        'description': 'question description',
        "questionOf": "lot",
        "relatedItem": self.initial_lots[1]['id'],
        'author': self.initial_organization
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    question = response.json['data']

    response = self.app.patch_json('/auctions/{}/questions/{}'.format(self.auction_id, question['id']),
                                   {"data": {"answer": "answer"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["answer"], "answer")

    response = self.app.get('/auctions/{}/questions/{}'.format(self.auction_id, question['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["answer"], "answer")
