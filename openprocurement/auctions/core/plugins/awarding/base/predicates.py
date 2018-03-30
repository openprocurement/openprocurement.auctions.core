# -*- coding: utf-8 -*-
def awarded_predicate(auction):
    return (
        not auction.lots
        and auction.status == 'active.awarded'
        and not any([i.status in auction.block_complaint_status for i in auction.complaints])
        and not any([i.status in auction.block_complaint_status for a in auction.awards for i in a.complaints])
    )


def awarded_and_lots_predicate(auction):
    return (
        auction.lots
        and auction.status in ['active.qualification', 'active.awarded']
        and not any([i.status in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints])
    )


def contract_overdue_predicate(item, need_status, now):
    return (
        item.status == need_status
        and item['signingPeriod']['endDate'] < now
    )


def protocol_overdue_predicate(award, need_status, now):
    return (
        award.status == need_status
        and award['verificationPeriod']['endDate'] < now
    )
