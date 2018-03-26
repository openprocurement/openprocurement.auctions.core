def awarded_predicate(auction):
    if (
        not auction.lots
        and auction.status == 'active.awarded'
        and not any([i.status in auction.block_complaint_status for i in auction.complaints])
        and not any([i.status in auction.block_complaint_status for a in auction.awards for i in a.complaints])
    ):
        return True

def awarded_and_lots_predicate(auction):
    if (
        auction.lots
        and auction.status in ['active.qualification', 'active.awarded']
        and not any([i.status in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints])
    ):
        return True
