# -*- coding: utf-8 -*-


def submission_method_details_no_auction(self):
    self.initial_data['submissionMethodDetails'] = u'quick(mode:no-auction)'
    self.create_auction()
    self.app.authorization = ('Basic', ('auction', ''))
    result = self.app.post_json('/auctions/{}/auction'.format(self.auction_id),
                                {'data': {'bids': self.initial_bids}})
    self.assertEqual(result['auctionPeriod']['startDate'],
                     result['auctionPeriod']['endDate'])
    self.assertEqual(result['status'], "active.qualification")


def submission_method_details_fast_forward(self):
    self.initial_data['submissionMethodDetails'] = u'quick(mode:fast-forward)'
    self.create_auction()
    self.app.authorization = ('Basic', ('auction', ''))
    result = self.app.post_json('/auctions/{}/auction'.format(self.auction_id),
                                {'data': {'bids': self.initial_bids}})
    self.assertEqual(result['auctionPeriod']['startDate'],
                     result['auctionPeriod']['endDate'])
    self.assertEqual(result['status'], "active.qualification")