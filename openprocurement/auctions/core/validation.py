# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError
from schematics.types import BaseType
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.auctions.core.constants import (
    ENGLISH_AUCTION_PROCUREMENT_METHOD_TYPES,
    CPVS_CODES_DGF_CDB2
)
from openprocurement.api.utils import (
    error_handler,
    get_now,
    update_logging_context,
    get_resource_accreditation
)
from openprocurement.api.validation import (
    validate_accreditations,
    validate_data, # noqa forwarded import
    validate_json_data, # noqa forwarded import
    validate_patch_document_data,  # noqa forwarded import
    validate_t_accreditation,
)

from openprocurement.auctions.core.constants import STATUS4ROLE


def validate_document_data(request, **kwargs):
    context = request.context if 'documents' in request.context else request.context.__parent__
    model = type(context).documents.model_class
    return validate_data(request, model, "document")


def validate_file_upload(request, **kwargs):
    update_logging_context(request, {'document_id': '__new__'})
    if request.registry.use_docservice and request.content_type == "application/json":
        return validate_document_data(request)
    if 'file' not in request.POST or not hasattr(request.POST['file'], 'filename'):
        request.errors.add('body', 'file', 'Not Found')
        request.errors.status = 404
        raise error_handler(request)
    else:
        request.validated['file'] = request.POST['file']


def validate_file_update(request, **kwargs):
    if request.registry.use_docservice and request.content_type == "application/json":
        return validate_document_data(request)
    if request.content_type == 'multipart/form-data':
        validate_file_upload(request)


def validate_auction_data(request, **kwargs):
    update_logging_context(request, {'auction_id': '__new__'})

    data = validate_json_data(request)
    if data is None:
        return

    model = request.auction_from_data(data, create=False)
    validate_accreditations(request, model, 'auction')
    data = validate_data(request, model, "auction", data=data)
    validate_t_accreditation(request, data, 'auction')


def validate_patch_auction_data(request, **kwargs):
    data = validate_json_data(request)
    if data is None:
        return
    if request.context.status != 'draft':
        return validate_data(request, type(request.auction), data=data)
    default_status = type(request.auction).fields['status'].default
    if data.get('status') != default_status:
        request.errors.add('body', 'data', 'Can\'t update auction in current (draft) status')
        request.errors.status = 403
        return
    request.validated['data'] = {'status': default_status}
    request.context.status = default_status


def validate_auction_auction_data(request, **kwargs):
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
        data['bids'] = [x for (_, x) in sorted(zip([auction_bids_ids.index(i['id']) for i in bids], bids))]
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
        if SANDBOX_MODE \
        and auction.submissionMethodDetails \
        and auction.submissionMethodDetails in [u'quick(mode:no-auction)', u'quick(mode:fast-forward)'] \
        and auction._internal_type in ENGLISH_AUCTION_PROCUREMENT_METHOD_TYPES:
            if auction.lots:
                data['lots'] = [{'auctionPeriod': {'startDate': now, 'endDate': now}} if i.id == lot_id else {} for i in auction.lots]
            else:
                data['auctionPeriod'] = {'startDate': now, 'endDate': now}
        else:
            if auction.lots:
                data['lots'] = [{'auctionPeriod': {'endDate': now}} if i.id == lot_id else {} for i in auction.lots]
            else:
                data['auctionPeriod'] = {'endDate': now}
    request.validated['data'] = data


def validate_bid_data(request, **kwargs):
    accreditation = get_resource_accreditation(request, 'auction', request.context, 'edit')
    if not request.check_accreditation(accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        return
    if request.auction.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('body', 'mode', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        return
    update_logging_context(request, {'bid_id': '__new__'})
    model = type(request.auction).bids.model_class
    return validate_data(request, model, "bid")


def validate_patch_bid_data(request, **kwargs):
    model = type(request.auction).bids.model_class
    return validate_data(request, model)


def validate_award_data(request, **kwargs):
    update_logging_context(request, {'award_id': '__new__'})
    model = type(request.auction).awards.model_class
    return validate_data(request, model, "award")


def validate_patch_award_data(request, **kwargs):
    model = type(request.auction).awards.model_class
    return validate_data(request, model)


def validate_award_data_post_common(request, **kwargs):
    auction = request.validated['auction']
    award = request.validated['award']
    if auction.status != 'active.qualification':
        request.errors.add('body', 'data',
                           'Can\'t create award in current ({})'
                           ' auction status'.format(auction.status))
    elif any([i.status != 'active' for i in auction.lots if i.id == award.lotID]):
        request.errors.add('body', 'data',
                           'Can create award only in active lot status')
    else:
        return
    request.errors.status = 403
    raise error_handler(request)


def validate_patch_award_data_patch_common(request, **kwargs):
    auction = request.validated['auction']
    if auction.status not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data',
                           'Can\'t update award in current ({}) auction status'.format(auction.status))
        request.errors.status = 403
        raise error_handler(request)


def validate_complaint_data_post_common(request, **kwargs):
    auction = request.validated['auction']
    context = request.context
    condition_start_date = context.complaintPeriod.startDate and context.complaintPeriod.startDate > get_now()
    condition_end_date = context.complaintPeriod.endDate and context.complaintPeriod.endDate < get_now()
    condition_date = condition_start_date or condition_end_date
    if auction.status not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data',
                           'Can\'t add complaint in current ({}) auction status'.format(auction.status))
    elif any([i.status != 'active' for i in auction.lots if
            i.id == context.lotID]):
        request.errors.add('body', 'data', 'Can add complaint only in active lot status')
    elif context.complaintPeriod and condition_date:
        request.errors.add('body', 'data','Can add complaint only in complaintPeriod')
    else:
        return
    request.errors.status = 403
    raise error_handler(request)


def validate_file_upload_post_common(request, **kwargs):
    if request.validated['auction_status'] not in ['active.qualification',
                                                   'active.awarded']:
        request.errors.add('body', 'data',
                           'Can\'t add document in current ({})'
                           ' auction status'.format(request.validated['auction_status']))
    elif any([i.status != 'active' for i in request.validated['auction'].lots
              if i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data',
                           'Can add document only in active lot status')
    elif request.context.status not in STATUS4ROLE.get(request.authenticated_role, []):
        request.errors.add('body', 'data',
                           'Can\'t add document in current ({})'
                           ' complaint status'.format(request.context.status))
    else:
        return
    request.errors.status = 403
    raise error_handler(request)


def validate_file_update_put_common(request, **kwargs):
    if request.authenticated_role != request.context.author:
        request.errors.add('url', 'role', 'Can update document only author')
    elif request.validated['auction_status'] not in ['active.qualification',
                                                   'active.awarded']:
        request.errors.add('body', 'data',
                           'Can\'t update document in current ({})'
                           ' auction status'.format(request.validated['auction_status']))
    elif any([i.status != 'active' for i in request.validated['auction'].lots
            if i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data',
                           'Can update document only in active lot status')
    elif request.validated['complaint'].status not in STATUS4ROLE.get(request.authenticated_role, []):
        request.errors.add('body', 'data',
                           'Can\'t update document in current ({})'
                           ' complaint status'.format(request.validated['complaint'].status))
    else:
        return
    request.errors.status = 403
    raise error_handler(request)


def validate_patch_document_data_patch_common(request, **kwargs):
    if request.authenticated_role != request.context.author:
        request.errors.add('url', 'role', 'Can update document only author')
    elif request.validated['auction_status'] not in ['active.qualification',
                                                   'active.awarded']:
        request.errors.add('body', 'data',
                           'Can\'t update document in current ({})'
                           ' auction status'.format(request.validated['auction_status']))
    elif any([i.status != 'active' for i in request.validated['auction'].lots
            if i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data',
                           'Can update document only in active lot status')
    elif request.validated['complaint'].status not in STATUS4ROLE.get(
            request.authenticated_role, []):
        request.errors.add('body', 'data',
                           'Can\'t update document in current ({})'
                           ' complaint status'.format(request.validated['complaint'].status))
    else:
        return
    request.errors.status = 403
    raise error_handler(request)


def validate_award_document(request, operation):
    if request.validated['auction_status'] != 'active.qualification':
        request.errors.add('body', 'data',
                           'Can\'t {} document in current ({})'
                           ' auction status'.format(operation, request.validated['auction_status']))
    elif any([i.status != 'active' for i in request.validated['auction'].lots if
              i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data',
                           'Can {} document only in active lot status'.format(operation))
    else:
        return True
    request.errors.status = 403
    raise error_handler(request)


def validate_file_upload_award_post_common(request, **kwargs):
    validate_award_document(request, 'add')


def validate_file_update_award_put_common(request, **kwargs):
    validate_award_document(request, 'update')


def validate_patch_document_data_award_patch_common(request, **kwargs):
    validate_award_document(request, 'update')


def validate_patch_complaint_data_patch_common(request, **kwargs):
    auction = request.validated['auction']
    if auction.status not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t update complaint in current'
                                           ' ({}) auction status'.format(auction.status))
    elif any([i.status != 'active' for i in auction.lots if
            i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data', 'Can update complaint only'
                                          ' in active lot status')
    elif request.context.status not in ['draft', 'claim', 'answered', 'pending']:
        request.errors.add('body', 'data', 'Can\'t update complaint in current'
                                           ' ({}) status'.format(request.context.status))
    else:
        return
    request.errors.status = 403
    raise error_handler(request)


def validate_question_data(request, **kwargs):
    accreditation = get_resource_accreditation(request, 'auction', request.context, 'edit')
    if not request.check_accreditation(accreditation):
        msg = 'Broker Accreditation level does not permit question creation'
        request.errors.add('procurementMethodType', 'accreditation', msg)
        request.errors.status = 403
        return
    if request.auction.get('mode', None) is None and request.check_accreditation('t'):
        msg = 'Broker Accreditation level does not permit question creation'
        request.errors.add('procurementMethodType', 'mode', msg)
        request.errors.status = 403
        return
    update_logging_context(request, {'question_id': '__new__'})
    model = type(request.auction).questions.model_class
    return validate_data(request, model, "question")


def validate_patch_question_data(request, **kwargs):
    model = type(request.auction).questions.model_class
    return validate_data(request, model)


def validate_complaint_data(request, **kwargs):
    accreditation = get_resource_accreditation(request, 'auction', request.auction, 'edit')
    if not request.check_accreditation(accreditation):
        msg = 'Broker Accreditation level does not permit complaint creation'
        request.errors.add('procurementMethodType', 'accreditation', msg)
        request.errors.status = 403
        return
    if request.auction.get('mode', None) is None and request.check_accreditation('t'):
        msg = 'Broker Accreditation level does not permit complaint creation'
        request.errors.add('procurementMethodType', 'mode', msg)
        request.errors.status = 403
        return
    update_logging_context(request, {'complaint_id': '__new__'})
    model = type(request.auction).complaints.model_class
    return validate_data(request, model, "complaint")


def validate_patch_complaint_data(request, **kwargs):
    model = type(request.auction).complaints.model_class
    return validate_data(request, model)


def validate_cancellation_data(request, **kwargs):
    update_logging_context(request, {'cancellation_id': '__new__'})
    model = type(request.auction).cancellations.model_class
    return validate_data(request, model, "cancellation")


def validate_patch_cancellation_data(request, **kwargs):
    model = type(request.auction).cancellations.model_class
    return validate_data(request, model)


def validate_contract_data(request, **kwargs):
    update_logging_context(request, {'contract_id': '__new__'})
    model = type(request.auction).contracts.model_class
    return validate_data(request, model, "contract")


def validate_prolongation_data(request, **kwargs):
    if request.json_body['data'].get('status') == 'applied':
        request.errors.add(
            'body',
            'data',
            'Can\'t create prolongation in {0} status'.format(request.validated['auction_status'])
        )
        request.errors.status = 403
        return
    if (request.validated['auction_status'] not in ['active.qualification', 'active.awarded']):
        request.errors.add(
            'body',
            'data',
            'Can\'t create prolongation in current ({}) auction status'.format(request.validated['auction_status'])
        )
        request.errors.status = 403
        return
    update_logging_context(request, {'prolongation_id': '__new__'})
    model = type(request.auction).contracts.model_class.prolongations.model_class
    return validate_data(request, model, "prolongation")


def validate_patch_prolongation_data(request, **kwargs):
    if (request.validated['auction_status'] not in ['active.qualification', 'active.awarded']):
        request.errors.add(
            'body',
            'data',
            'Can\'t update prolongation in current ({}) auction status'.format(
                request.validated['auction_status']
            )
        )
        request.errors.status = 403
        return
    # Don't allow to patch active Prolongation
    current_prolongation_status = request.validated['prolongation']['status']
    if current_prolongation_status == 'applied':
        request.errors.add(
            'body',
            'data',
            'Can\'t patch prolongation in current {0} status'.format(current_prolongation_status)
        )
        request.errors.status = 403
        return

    model = type(request.auction).contracts.model_class.prolongations.model_class
    return validate_data(request, model)


def validate_patch_contract_data(request, **kwargs):
    model = type(request.auction).contracts.model_class
    return validate_data(request, model)


def validate_lot_data(request, **kwargs):
    update_logging_context(request, {'lot_id': '__new__'})
    model = type(request.auction).lots.model_class
    return validate_data(request, model, "lot")


def validate_patch_lot_data(request, **kwargs):
    model = type(request.auction).lots.model_class
    return validate_data(request, model)


def validate_disallow_dgfPlatformLegalDetails(docs, *args):
    if any([i.documentType == 'x_dgfPlatformLegalDetails' for i in docs]):
        raise ValidationError(u"Disallow documents with x_dgfPlatformLegalDetails documentType")



# additional_classification_validators

def cpvs_validator(data, code):
    if data.get('scheme') == u'CPVS' and code not in CPVS_CODES_DGF_CDB2:
        raise ValidationError(BaseType.MESSAGES['choices'].format(unicode(CPVS_CODES_DGF_CDB2)))
    return True


def validate_rectification_period(request, **kwargs):
    """Forbid to use view if auction is out of it's rectificationPeriod"""
    from openprocurement.auctions.core.models.schema import get_auction
    auction = get_auction(request.context)
    if get_now() not in auction.rectificationPeriod:
        request.errors.add(
            'body',
            'data',
            'Can\'t edit resource, because it\'s related auction\'s rectification period has expired.'
        )
        request.errors.status = 403
        raise error_handler(request)
