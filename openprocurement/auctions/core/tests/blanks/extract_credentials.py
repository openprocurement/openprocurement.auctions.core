from openprocurement.auctions.core.utils import get_forbidden_users


def get_extract_credentials(self):
    expected_keys = ('owner', 'transfer_token')
    self.app.authorization = ('Basic', (self.valid_user, ''))
    path = '/auctions/{}/extract_credentials'.format(self.auction_id)
    response = self.app.get(path)
    response_data_keys = response.json['data'].keys()
    _ = [self.assertIn(key, response_data_keys) for key in expected_keys]


def forbidden_users(self):
    forbidden_users = get_forbidden_users(allowed_levels=('3'))
    for user in forbidden_users:
        self.app.authorization = ('Basic', (user, ''))
        self.app.get('/auctions/{}/extract_credentials'.format(self.auction_id), status=403)
