from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.core.tests.blanks.question_blanks import (
    # AuctionQuestionResourceTest
    create_auction_question_invalid,
    create_auction_question,
    patch_auction_question,
    get_auction_question,
    get_auction_questions,
)


class AuctionQuestionResourceTestMixin(object):

    test_create_auction_question_invalid = snitch(create_auction_question_invalid)
    test_create_auction_question = snitch(create_auction_question)
    test_patch_auction_question = snitch(patch_auction_question)
    test_get_auction_question = snitch(get_auction_question)
    test_get_auction_questions = snitch(get_auction_questions)
