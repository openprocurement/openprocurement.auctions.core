import unittest

from openprocurement.auctions.core.tests.base import snitch
from blanks.award_blanks import (
    # AuctionAwardProcessTest
    invalid_patch_auction_award,
    patch_auction_award,
    patch_auction_award_admin,
    complate_auction_with_second_award1,
    complate_auction_with_second_award2,
    complate_auction_with_second_award3,
    unsuccessful_auction3,
    unsuccessful_auction4,
    unsuccessful_auction5,
    get_auction_awards,
    successful_second_auction_award,
    # CreateAuctionAwardTest
    create_auction_award_invalid,
    create_auction_award,
    patch_auction_award_participant_disqualification,
    award_activation_creates_contract,
    created_award_have_periods_set,
    created_awards_statuses,
    verification_period_length,
)


class AuctionAwardProcessTestMixin(object):
    test_invalid_patch_auction_award = snitch(invalid_patch_auction_award)
    test_patch_auction_award = snitch(patch_auction_award)
    test_patch_auction_award_admin = snitch(patch_auction_award_admin)

    test_complate_auction_with_second_award1 = snitch(
        complate_auction_with_second_award1
    )

    test_complate_auction_with_second_award2 = snitch(
        complate_auction_with_second_award2
    )

    test_complate_auction_with_second_award3 = snitch(
        complate_auction_with_second_award3
    )

    test_successful_second_auction_award = snitch(
        successful_second_auction_award
    )

    test_unsuccessful_auction3 = snitch(unsuccessful_auction3)
    test_unsuccessful_auction4 = snitch(unsuccessful_auction4)
    test_unsuccessful_auction5 = snitch(unsuccessful_auction5)
    test_get_auction_awards = snitch(get_auction_awards)

    test_patch_auction_award_participant_disqualification = snitch(
        patch_auction_award_participant_disqualification
    )

    test_created_award_have_periods_set = snitch(
        created_award_have_periods_set
    )
    test_created_awards_statuses = snitch(
        created_awards_statuses
    )
    test_verification_period_length = snitch(
        verification_period_length
    )


class CreateAuctionAwardTestMixin(object):
    test_create_auction_award_invalid = unittest.skip('option not available')(
        snitch(create_auction_award_invalid)
    )
    test_create_auction_award = unittest.skip('option not available')(
        snitch(create_auction_award)
    )
    test_award_activation_creates_contract = snitch(
        award_activation_creates_contract
    )
