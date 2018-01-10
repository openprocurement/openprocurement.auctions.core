# -*- coding: utf-8 -*-


def submission_method_details_no_auction(self):
    self.initial_data['submissionMethodDetails'] = u'quick(mode:no-auction)'
    self.create_auction()
    self.app.authorization = ('Basic', ('auction', ''))
    auction = self.app.post_json('/auctions/{}/auction'.format(self.auction_id),
                                {'data': {'bids': self.initial_bids}}).json['data']
    self.assertEqual(auction['auctionPeriod']['startDate'],
                     auction['auctionPeriod']['endDate'])
    self.assertEqual(auction['status'], "active.qualification")


def submission_method_details_fast_forward(self):
    self.initial_data['submissionMethodDetails'] = u'quick(mode:fast-forward)'
    self.create_auction()
    self.app.authorization = ('Basic', ('auction', ''))
    auction = self.app.post_json('/auctions/{}/auction'.format(self.auction_id),
                                {'data': {'bids': self.initial_bids}}).json['data']
    self.assertEqual(auction['auctionPeriod']['startDate'],
                     auction['auctionPeriod']['endDate'])
    self.assertEqual(auction['status'], "active.qualification")