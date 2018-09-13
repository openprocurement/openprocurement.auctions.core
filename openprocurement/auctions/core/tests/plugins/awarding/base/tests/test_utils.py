# -*- coding: utf-8 -*-
import unittest
import uuid
import mock
import munch
import random
from openprocurement.api.utils import get_now
from openprocurement.api.constants import TZ
from openprocurement.auctions.core.plugins.awarding.base.constants import (
    NUMBER_OF_BIDS_TO_BE_QUALIFIED
)
from openprocurement.auctions.core.plugins.awarding.base.utils import (
    check_document_existence,
    invalidate_bids_under_threshold,
    check_pending_awards_complaints,
    check_pending_complaints,
    set_stand_still_ends,
    check_lots_awarding,
    set_award_status_unsuccessful,
    set_unsuccessful_award,
    get_bids_to_qualify
)


BASE_UTILS_PATH = 'openprocurement.auctions.core.plugins.awarding.base.utils'


class Test(unittest.TestCase):

    def test_check_auction_protocol(self):
        def get_document(documentType, author):
            return {
                'documentType': documentType,
                'author': author}

        document = get_document('auctionProtocol', 'auction_owner')
        award = munch.Munch({'documents': [document]})
        result = check_document_existence(award, 'auctionProtocol')
        self.assertEqual(result, True)

        document = get_document('auctionProtocol', 'not_auction_owner')
        award = munch.Munch({'documents': [document]})
        result = check_document_existence(award, 'auctionProtocol')
        self.assertEqual(result, False)

        award = munch.Munch({'documents': []})
        result = check_document_existence(award, 'auctionProtocol')
        self.assertEqual(result, False)

        document = get_document('not_auctionProtocol', 'auction_owner')
        award = munch.Munch({'documents': [document]})
        result = check_document_existence(award, 'auctionProtocol')
        self.assertEqual(result, False)

    def test_invalidate_bids_under_threshold(self):
        def get_auction(value, minimal_step, bids):
            return {
                'value': {'amount': value},
                'minimalStep': {'amount': minimal_step},
                'bids': bids
            }
        need_bid_statuses = ('valid', 'invalid')
        amount = random.randint(50, 100)
        small_amount = random.randint(1, (amount - 1) / 2)
        big_amount = random.randint(amount, (amount * 2))
        bid = munch.Munch({'value': {'amount': amount},
                           'status': need_bid_statuses[0]})

        auction = get_auction(small_amount, small_amount, [])
        invalidate_bids_under_threshold(auction)
        self.assertEqual(bid.status, need_bid_statuses[0])

        auction = get_auction(small_amount, small_amount, [bid])
        invalidate_bids_under_threshold(auction)
        self.assertEqual(bid.status, need_bid_statuses[0])

        auction = get_auction(big_amount, big_amount, [bid])
        invalidate_bids_under_threshold(auction)
        self.assertEqual(bid.status, need_bid_statuses[1])

    def test_check_pending_awards_complaints(self):
        need_status = 'status'
        need_lot_id = uuid.uuid4().hex
        differ_lot_id = uuid.uuid4().hex

        lot_awards = munch.Munch({'id': need_lot_id})

        complain = munch.Munch({'status': need_status,
                                'relatedLot': need_lot_id})

        auction = munch.Munch({'complaints': [complain],
                               'block_complaint_status': need_status})

        result = check_pending_awards_complaints(auction, lot_awards)
        self.assertEqual(result, True)

        lot_awards.id = differ_lot_id
        result = check_pending_awards_complaints(auction, lot_awards)
        self.assertEqual(result, None)

        complain.status = 'differ'
        result = check_pending_awards_complaints(auction, lot_awards)
        self.assertEqual(result, None)

    def test_check_pending_complaints(self):
        need_status = 'status'
        complaints = munch.Munch({'status': need_status})
        award = munch.Munch({'complaints': [complaints]})
        lot_awards = [award]
        auction = munch.Munch({'block_complaint_status': need_status})

        result = check_pending_complaints(auction, lot_awards)
        self.assertEqual(result, True)

        complaints.status = 'differ'
        result = check_pending_complaints(auction, lot_awards)
        self.assertEqual(result, None)

        result = check_pending_complaints(auction, [])
        self.assertEqual(result, None)

        award.comlaints = []
        result = check_pending_complaints(auction, [award])
        self.assertEqual(result, None)

    def test_set_stand_still_ends(self):
        need_end_date = get_now()
        complaint_period = munch.Munch({'endDate': need_end_date})
        award = munch.Munch({'complaintPeriod': complaint_period})

        result = set_stand_still_ends([award])
        self.assertEqual(result[0], need_end_date.astimezone(TZ))

        award.complaintPeriod.endDate = None
        result = set_stand_still_ends([award])
        self.assertEqual(0, len(result))

        result = set_stand_still_ends([])
        self.assertEqual(0, len(result))

    @mock.patch('{}.{}'.format(BASE_UTILS_PATH, 'check_pending_complaints'))
    @mock.patch('{}.{}'.format(BASE_UTILS_PATH, 'check_pending_awards_complaints'))
    @mock.patch('{}.{}'.format(BASE_UTILS_PATH, 'set_stand_still_ends'))
    def test_check_lots_awarding(self, mock_set_stand_still_ends,
                                 mock_check_pending_awards_complaints,
                                 mock_check_pending_complaints):
        need_status = 'active'
        need_status_award = 'unsuccessful'
        need_lot_id = uuid.uuid4().hex
        lot = munch.Munch({'status': need_status,
                           'id': need_lot_id})
        award = munch.Munch({'lotID': need_lot_id,
                             'status': need_status_award})

        auction = munch.Munch({'lots': [lot],
                               'awards': [award]})

        mock_check_pending_complaints.return_value = None
        mock_check_pending_awards_complaints.return_value = None
        mock_set_stand_still_ends.return_value = [0, 1]
        result = check_lots_awarding(auction)
        self.assertEqual(result, [1])

        mock_check_pending_complaints.return_value = True
        mock_set_stand_still_ends.return_value = [0, 1]
        result = check_lots_awarding(auction)
        self.assertEqual(result, [])

        mock_check_pending_complaints.return_value = None
        mock_check_pending_awards_complaints.return_value = True
        mock_set_stand_still_ends.return_value = [0, 1]
        result = check_lots_awarding(auction)
        self.assertEqual(result, [])

    def test_set_award_status_unsuccessful(self):
        need_end_date = get_now()
        end_data = munch.Munch({'endDate': None})
        award = munch.Munch({'status': 'successfull',
                             'complaintPeriod': end_data})

        set_award_status_unsuccessful(award, need_end_date)
        self.assertEqual(award.status, 'unsuccessful')
        self.assertEqual(need_end_date.isoformat(),
                         end_data.endDate.isoformat())

    def test_unsuccessful_award(self):
        contract_status = 'status'
        need_status = 'active'
        need_award_id = uuid.uuid4().hex
        differ_id = uuid.uuid4().hex
        complain_end_date = get_now()
        end_data_award = munch.Munch({'endDate': True})
        end_data_action = munch.Munch({'endDate': True})

        contract = munch.Munch({'awardID': need_award_id,
                                'status': contract_status})

        auction = munch.Munch({'status': True,
                               'awardPeriod': end_data_action,
                               'contracts': [contract]})

        award = munch.Munch({'id': need_award_id,
                             'status': need_status,
                             'complaintPeriod': end_data_award})
        request = mock.MagicMock()

        set_unsuccessful_award(request, auction, award, complain_end_date)
        self.assertEqual(1, request.content_configurator.back_to_awarding.call_count)
        self.assertEqual(contract.status, 'cancelled')
        self.assertEqual(auction.status, 'active.qualification')
        self.assertEqual(auction.awardPeriod.endDate, None)
        self.assertEqual(award.status, 'unsuccessful')
        self.assertEqual(award.complaintPeriod.endDate.isoformat(),
                         end_data_award.endDate.isoformat())

        award.status = 'not_active'
        auction.awardPeriod.endDate = True
        auction.status = 'not_changed'
        contract.status = 'not_cancelled'
        set_unsuccessful_award(request, auction, award, complain_end_date)
        self.assertEqual(auction.awardPeriod.endDate, True)
        self.assertEqual(auction.status, 'not_changed')
        self.assertEqual(contract.status, 'not_cancelled')
        self.assertEqual(2, request.content_configurator.back_to_awarding.call_count)

        award.status = 'active'
        award.id = differ_id
        set_unsuccessful_award(request, auction, award, complain_end_date)
        self.assertEqual(contract.status, 'not_cancelled')
        self.assertEqual(auction.status, 'active.qualification')
        self.assertEqual(auction.awardPeriod.endDate, None)

    def test_get_bids_to_qualify(self):
        bids = range(NUMBER_OF_BIDS_TO_BE_QUALIFIED + 1)
        result = get_bids_to_qualify(bids)
        self.assertEqual(result, NUMBER_OF_BIDS_TO_BE_QUALIFIED)

        bids = range(NUMBER_OF_BIDS_TO_BE_QUALIFIED - 1)
        result = get_bids_to_qualify(bids)
        self.assertEqual(result, len(bids))


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(Test))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
