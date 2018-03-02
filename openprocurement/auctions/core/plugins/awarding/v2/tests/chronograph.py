# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.plugins.awarding.v2.tests.blanks.chronograph_blanks import (
    # AuctionAwardSwitchResourceTest
    switch_verification_to_unsuccessful,
    switch_payment_to_unsuccessful,
    switch_active_to_unsuccessful,
    # AuctionDontSwitchSuspendedAuctionResourceTest
    switch_suspended_verification_to_unsuccessful,
    switch_suspended_payment_to_unsuccessful,
    switch_suspended_active_to_unsuccessful
)


class AuctionAwardSwitchResourceTestMixin(object):
    test_switch_verification_to_unsuccessful = snitch(switch_verification_to_unsuccessful)
    test_switch_payment_to_unsuccessful = snitch(switch_payment_to_unsuccessful)
    test_switch_active_to_unsuccessful = snitch(switch_active_to_unsuccessful)


class AuctionDontSwitchSuspendedAuctionResourceTestMixin(object):
    test_switch_suspended_verification_to_unsuccessful = snitch(switch_suspended_verification_to_unsuccessful)
    test_switch_suspended_payment_to_unsuccessful = snitch(switch_suspended_payment_to_unsuccessful)
    test_switch_suspended_active_to_unsuccessful = snitch(switch_suspended_active_to_unsuccessful)
