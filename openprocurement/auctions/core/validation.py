# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now, SANDBOX_MODE
from openprocurement.api.utils import update_logging_context
from openprocurement.api.validation import validate_json_data, validate_data
from openprocurement.auctions.core.constants import ENGLISH_AUCTION_PROCUREMENT_METHOD_TYPES


def validate_auction_data(request):
    update_logging_context(request, {'auction_id': '__new__'})

    data = validate_json_data(request)
    if data is None:
        return

    model = request.auction_from_data(data, create=False)
    if not request.check_accreditation(model.create_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit auction creation')
        request.errors.status = 403
        return
    data = validate_data(request, model, data=data)
    if data and data.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit auction creation')
        request.errors.status = 403
        return


def validate_patch_auction_data(request):
    data = validate_json_data(request)
    if data is None:
        return
    if request.context.status != 'draft':
        return validate_data(request, type(request.auction), True, data)
    default_status = type(request.auction).fields['status'].default
    if data.get('status') != default_status:
        request.errors.add('body', 'data', 'Can\'t update auction in current (draft) status')
        request.errors.status = 403
        return
    request.validated['data'] = {'status': default_status}
    request.context.status = default_status


def validate_auction_auction_data(request):
    data = validate_patch_auction_data(request)
    auction = request.validated['auction']
    if auction.status != 'active.auction':
        request.errors.add('body', 'data', 'Can\'t {} in current ({}) auction status'.format('report auction results' if request.method == 'POST' else 'update auction urls', auction.status))
        request.errors.status = 403
        return
    lot_id = request.matchdict.get('auction_lot_id')
    if auction.lots and any([i.status != 'active' for i in auction.lots if i.id == lot_id]):
        request.errors.add('body', 'data', 'Can {} only in active lot status'.format('report auction results' if request.method == 'POST' else 'update auction urls'))
        request.errors.status = 403
        return
    if data is not None:
        bids = data.get('bids', [])
        auction_bids_ids = [i.id for i in auction.bids]
        if len(bids) != len(auction.bids):
            request.errors.add('body', 'bids', "Number of auction results did not match the number of auction bids")
            request.errors.status = 422
            return
        if set([i['id'] for i in bids]) != set(auction_bids_ids):
            request.errors.add('body', 'bids', "Auction bids should be identical to the auction bids")
            request.errors.status = 422
            return
        data['bids'] = [x for (y, x) in sorted(zip([auction_bids_ids.index(i['id']) for i in bids], bids))]
        if data.get('lots'):
            auction_lots_ids = [i.id for i in auction.lots]
            if len(data.get('lots', [])) != len(auction.lots):
                request.errors.add('body', 'lots', "Number of lots did not match the number of auction lots")
                request.errors.status = 422
                return
            if set([i['id'] for i in data.get('lots', [])]) != set([i.id for i in auction.lots]):
                request.errors.add('body', 'lots', "Auction lots should be identical to the auction lots")
                request.errors.status = 422
                return
            data['lots'] = [
                x if x['id'] == lot_id else {}
                for (y, x) in sorted(zip([auction_lots_ids.index(i['id']) for i in data.get('lots', [])], data.get('lots', [])))
            ]
        if auction.lots:
            for index, bid in enumerate(bids):
                if (getattr(auction.bids[index], 'status', 'active') or 'active') == 'active':
                    if len(bid.get('lotValues', [])) != len(auction.bids[index].lotValues):
                        request.errors.add('body', 'bids', [{u'lotValues': [u'Number of lots of auction results did not match the number of auction lots']}])
                        request.errors.status = 422
                        return
                    for lot_index, lotValue in enumerate(auction.bids[index].lotValues):
                        if lotValue.relatedLot != bid.get('lotValues', [])[lot_index].get('relatedLot', None):
                            request.errors.add('body', 'bids', [{u'lotValues': [{u'relatedLot': ['relatedLot should be one of lots of bid']}]}])
                            request.errors.status = 422
                            return
            for bid_index, bid in enumerate(data['bids']):
                if 'lotValues' in bid:
                    bid['lotValues'] = [
                        x if x['relatedLot'] == lot_id and (getattr(auction.bids[bid_index].lotValues[lotValue_index], 'status', 'active') or 'active') == 'active' else {}
                        for lotValue_index, x in enumerate(bid['lotValues'])
                    ]

    else:
        data = {}
    if request.method == 'POST':
        now = get_now().isoformat()
        if SANDBOX_MODE and auction.submissionMethodDetails and \
                auction.submissionMethodDetails in [u'quick(mode:no-auction)', u'quick(mode:fast-forward)'] and \
                auction.procurementMethodType in ENGLISH_AUCTION_PROCUREMENT_METHOD_TYPES:
            if auction.lots:
                data['lots'] = [{'auctionPeriod':
                                     {'startDate': now, 'endDate': now}}
                                if i.id == lot_id else {} for i in auction.lots]
            else:
                data['auctionPeriod'] = {'startDate': now, 'endDate': now}
        else:
            if auction.lots:
                data['lots'] = [{'auctionPeriod': {'endDate': now}}
                                if i.id == lot_id else {} for i in auction.lots]
            else:
                data['auctionPeriod'] = {'endDate': now}
    request.validated['data'] = data


def validate_bid_data(request):
    if not request.check_accreditation(request.auction.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        return
    if request.auction.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        return
    update_logging_context(request, {'bid_id': '__new__'})
    model = type(request.auction).bids.model_class
    return validate_data(request, model)


def validate_patch_bid_data(request):
    model = type(request.auction).bids.model_class
    return validate_data(request, model, True)


def validate_award_data(request):
    update_logging_context(request, {'award_id': '__new__'})
    model = type(request.auction).awards.model_class
    return validate_data(request, model)


def validate_patch_award_data(request):
    model = type(request.auction).awards.model_class
    return validate_data(request, model, True)


def validate_question_data(request):
    if not request.check_accreditation(request.auction.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit question creation')
        request.errors.status = 403
        return
    if request.auction.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit question creation')
        request.errors.status = 403
        return
    update_logging_context(request, {'question_id': '__new__'})
    model = type(request.auction).questions.model_class
    return validate_data(request, model)


def validate_patch_question_data(request):
    model = type(request.auction).questions.model_class
    return validate_data(request, model, True)


def validate_complaint_data(request):
    if not request.check_accreditation(request.auction.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        return
    if request.auction.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        return
    update_logging_context(request, {'complaint_id': '__new__'})
    model = type(request.auction).complaints.model_class
    return validate_data(request, model)


def validate_patch_complaint_data(request):
    model = type(request.auction).complaints.model_class
    return validate_data(request, model, True)


def validate_cancellation_data(request):
    update_logging_context(request, {'cancellation_id': '__new__'})
    model = type(request.auction).cancellations.model_class
    return validate_data(request, model)


def validate_patch_cancellation_data(request):
    model = type(request.auction).cancellations.model_class
    return validate_data(request, model, True)


def validate_contract_data(request):
    update_logging_context(request, {'contract_id': '__new__'})
    model = type(request.auction).contracts.model_class
    return validate_data(request, model)


def validate_patch_contract_data(request):
    model = type(request.auction).contracts.model_class
    return validate_data(request, model, True)


def validate_lot_data(request):
    update_logging_context(request, {'lot_id': '__new__'})
    model = type(request.auction).lots.model_class
    return validate_data(request, model)


def validate_patch_lot_data(request):
    model = type(request.auction).lots.model_class
    return validate_data(request, model, True)
