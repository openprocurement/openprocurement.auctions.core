# -*- coding: utf-8 -*-


def not_active_lots_predicate(request):
    predicate = []

    def get_awards_lot_ids(request):
        for award in request.validated['auction'].awards:
            if award.id == request.validated['contract'].awardID:
                yield award.lotID

    for item in request.validated['auction'].lots:
        if item.id in get_awards_lot_ids(request):
            predicate.append(item.status != 'active')
    return any(predicate)
