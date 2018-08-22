from openprocurement.auctions.core.utils import get_forbidden_users


def get_extract_credentials(self):
    import ipdb; ipdb.set_trace()
    expected_keys = ('owner', 'transfer_token')
    self.app.authorization = ('Basic', (self.valid_user, ''))
    path = '/{}/extract_credentials'.format(self.resource_id)
    response = self.app.get(path)
    response_data_keys = response.json['data'].keys()
    _ = [self.assertIn(key, response_data_keys) for key in expected_keys]


def forbidden_users(self):
    forbidden_users = get_forbidden_users(allowed_levels=('3'))
    for user in forbidden_users:
        self.app.authorization = ('Basic', (user, ''))
        self.app.get('/{}/extract_credentials'.format(self.resource_id), status=403)
