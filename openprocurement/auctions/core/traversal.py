# -*- coding: utf-8 -*-

from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Deny,
    Everyone,
)


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        # (Allow, Everyone, ALL_PERMISSIONS),
        (Allow, Everyone, 'view_listing'),
        (Allow, Everyone, 'view_auction'),
        (Deny, 'broker05', 'create_bid'),
        (Deny, 'broker05', 'create_complaint'),
        (Deny, 'broker05', 'create_question'),
        (Deny, 'broker05', 'create_auction'),
        (Deny, 'broker05', 'create_tender'),
        (Allow, 'g:brokers', 'create_bid'),
        (Allow, 'g:brokers', 'create_complaint'),
        (Allow, 'g:brokers', 'create_question'),
        (Allow, 'g:brokers', 'create_auction'),
        (Allow, 'g:brokers', 'create_tender'),
        (Allow, 'g:auction', 'auction'),
        (Allow, 'g:auction', 'upload_auction_documents'),
        (Allow, 'g:auction', 'upload_tender_documents'),
        (Allow, 'g:contracting', 'extract_credentials'),
        (Allow, 'g:chronograph', 'edit_auction'),
        (Allow, 'g:chronograph', 'edit_tender'),
        (Allow, 'g:convoy', 'edit_auction'),
        (Allow, 'g:convoy', 'extract_credentials'),
        (Allow, 'g:concierge', 'create_auction'),
        (Allow, 'g:concierge', 'edit_auction'),
        (Allow, 'g:Administrator', 'edit_auction'),
        (Allow, 'g:Administrator', 'edit_tender'),
        (Allow, 'g:Administrator', 'edit_auction_award'),
        (Allow, 'g:Administrator', 'edit_bid'),
        (Deny, 'g:admins', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db


def get_item(parent, key, request):
    request.validated['{}_id'.format(key)] = request.matchdict['{}_id'.format(key)]
    items = [i for i in getattr(parent, '{}s'.format(key), []) if i.id == request.matchdict['{}_id'.format(key)]]
    if not items:
        from openprocurement.auctions.core.utils import error_handler
        request.errors.add('url', '{}_id'.format(key), 'Not Found')
        request.errors.status = 404
        raise error_handler(request)
    else:
        if key == 'document':
            request.validated['{}s'.format(key)] = items
        item = items[-1]
        request.validated[key] = item
        request.validated['id'] = request.matchdict['{}_id'.format(key)]
        item.__parent__ = parent
        return item


def factory(request):

    request.validated['auction_src'] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('auction_id'):
        return root
    request.validated['auction_id'] = request.matchdict['auction_id']
    auction = request.auction
    auction.__parent__ = root
    request.validated['auction'] = request.validated['db_doc'] = auction
    request.validated['auction_status'] = auction.status
    if request.method != 'GET':
        request.validated['auction_src'] = auction.serialize('plain')
        if auction._initial.get('next_check'):
            request.validated['auction_src']['next_check'] = auction._initial.get('next_check')
    #  Award branch
    if request.matchdict.get('award_id'):
        award = get_item(auction, 'award', request)
        if request.matchdict.get('complaint_id'):
            complaint = get_item(award, 'complaint', request)
            if request.matchdict.get('document_id'):
                return get_item(complaint, 'document', request)
            else:
                return complaint
        elif request.matchdict.get('document_id'):
            return get_item(award, 'document', request)
        return award
    #  Contract branch
    elif request.matchdict.get('contract_id'):
        contract = get_item(auction, 'contract', request)
        if request.matchdict.get('document_id') and not \
                request.matchdict.get('prolongation_id'):
            return get_item(contract, 'document', request)
        if request.matchdict.get('prolongation_id'):
            prolongation = get_item(contract, 'prolongation', request)
            if request.matchdict.get('document_id'):
                return get_item(prolongation, 'document', request)
            else:
                return prolongation
        return contract
    #  Bid branch
    elif request.matchdict.get('bid_id'):
        bid = get_item(auction, 'bid', request)
        if request.matchdict.get('document_id'):
            return get_item(bid, 'document', request)
        return bid
    #  Item branch
    elif request.matchdict.get('item_id'):
        item = get_item(auction, 'item', request)
        return item
    #  Complaint branch
    elif request.matchdict.get('complaint_id'):
        complaint = get_item(auction, 'complaint', request)
        if request.matchdict.get('document_id'):
            return get_item(complaint, 'document', request)
        return complaint
    #  Cancellation branch
    elif request.matchdict.get('cancellation_id'):
        cancellation = get_item(auction, 'cancellation', request)
        if request.matchdict.get('document_id'):
            return get_item(cancellation, 'document', request)
        return cancellation
    #  Document branch
    elif request.matchdict.get('document_id'):
        return get_item(auction, 'document', request)
    #  question branch
    elif request.matchdict.get('question_id'):
        return get_item(auction, 'question', request)
    #  Lot branch
    elif request.matchdict.get('lot_id'):
        return get_item(auction, 'lot', request)
    request.validated['id'] = request.matchdict['auction_id']
    return auction
