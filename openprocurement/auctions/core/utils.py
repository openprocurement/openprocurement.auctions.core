# -*- coding: utf-8 -*-
from barbecue import chef
from base64 import b64encode
from cornice.resource import resource, view
from cornice.util import json_error
from couchdb.http import ResourceConflict
from email.header import decode_header
from functools import partial
from json import dumps
from jsonpointer import resolve_pointer
from logging import getLogger
from openprocurement.api.models import get_now, TZ, COMPLAINT_STAND_STILL_TIME
from openprocurement.api.utils import (generate_id, calculate_business_date, apply_data_patch,
                                       get_revision_changes, set_modetest_titles, update_logging_context,
                                       context_unpack)
from openprocurement.auctions.core.traversal import factory
from pkg_resources import get_distribution
from rfc6266 import build_header
from schematics.exceptions import ModelValidationError
from time import sleep
from urllib import quote
from urlparse import urlparse, parse_qs
from re import compile
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)
VERSION = '{}.{}'.format(int(PKG.parsed_version[0]), int(PKG.parsed_version[1]) if PKG.parsed_version[1].isdigit() else 0)
ROUTE_PREFIX = '/api/{}'.format(VERSION)
DOCUMENT_BLACKLISTED_FIELDS = ('title', 'format', '__parent__', 'id', 'url', 'dateModified', )
ACCELERATOR_RE = compile(r'.accelerator=(?P<accelerator>\d+)')
json_view = partial(view, renderer='json')


def generate_auction_id(ctime, db, server_id=''):
    key = ctime.date().isoformat()
    auctionIDdoc = 'auctionID_' + server_id if server_id else 'auctionID'
    while True:
        try:
            auctionID = db.get(auctionIDdoc, {'_id': auctionIDdoc})
            index = auctionID.get(key, 1)
            auctionID[key] = index + 1
            db.save(auctionID)
        except ResourceConflict:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover
            sleep(1)
        else:
            break
    return 'UA-EA-{:04}-{:02}-{:02}-{:06}{}'.format(ctime.year, ctime.month, ctime.day, index, server_id and '-' + server_id)


def auction_serialize(request, auction_data, fields):
    auction = request.auction_from_data(auction_data, raise_error=False)
    if auction is None:
        return dict([(i, auction_data.get(i, '')) for i in ['procurementMethodType', 'dateModified', 'id']])
    return dict([(i, j) for i, j in auction.serialize(auction.status).items() if i in fields])


def save_auction(request):

    auction = request.validated['auction']
    if auction.mode == u'test':
        set_modetest_titles(auction)
    patch = get_revision_changes(auction.serialize("plain"), request.validated['auction_src'])
    if patch:
        now = get_now()
        status_changes = [
            p
            for p in patch
            if not p['path'].startswith('/bids/') and p['path'].endswith("/status") and p['op'] == "replace"
        ]
        for change in status_changes:
            obj = resolve_pointer(auction, change['path'].replace('/status', ''))
            if obj and hasattr(obj, "date"):
                date_path = change['path'].replace('/status', '/date')
                if obj.date and not any([p for p in patch if date_path == p['path']]):
                    patch.append({"op": "replace", "path": date_path, "value": obj.date.isoformat()})
                elif not obj.date:
                    patch.append({"op": "remove", "path": date_path})
                obj.date = now
        auction.revisions.append(type(auction).revisions.model_class({'author': request.authenticated_userid, 'changes': patch, 'rev': auction.rev}))
        old_dateModified = auction.dateModified
        if getattr(auction, 'modified', True):
            auction.dateModified = now
        try:

            auction.store(request.registry.db)
        except ModelValidationError, e:
            for i in e.message:
                request.errors.add('body', i, e.message[i])
            request.errors.status = 422
        except ResourceConflict, e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
            request.errors.status = 409
        except Exception, e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
        else:
            LOGGER.info('Saved auction {}: dateModified {} -> {}'.format(auction.id, old_dateModified and old_dateModified.isoformat(), auction.dateModified.isoformat()),
                        extra=context_unpack(request, {'MESSAGE_ID': 'save_auction'}, {'RESULT': auction.rev}))
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated['data'] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_auction(request)


def cleanup_bids_for_cancelled_lots(auction):
    cancelled_lots = [i.id for i in auction.lots if i.status == 'cancelled']
    if cancelled_lots:
        return
    cancelled_items = [i.id for i in auction.items if i.relatedLot in cancelled_lots]
    cancelled_features = [
        i.code
        for i in (auction.features or [])
        if i.featureOf == 'lot' and i.relatedItem in cancelled_lots or i.featureOf == 'item' and i.relatedItem in cancelled_items
    ]
    for bid in auction.bids:
        bid.documents = [i for i in bid.documents if i.documentOf != 'lot' or i.relatedItem not in cancelled_lots]
        bid.parameters = [i for i in bid.parameters if i.code not in cancelled_features]
        bid.lotValues = [i for i in bid.lotValues if i.relatedLot not in cancelled_lots]
        if not bid.lotValues:
            auction.bids.remove(bid)


def remove_draft_bids(request):
    auction = request.validated['auction']
    if [bid for bid in auction.bids if getattr(bid, "status", "active") == "draft"]:
        LOGGER.info('Remove draft bids',
                    extra=context_unpack(request, {'MESSAGE_ID': 'remove_draft_bids'}))
        auction.bids = [bid for bid in auction.bids if getattr(bid, "status", "active") != "draft"]


def check_bids(request):
    auction = request.validated['auction']
    if auction.lots:
        [setattr(i.auctionPeriod, 'startDate', None) for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate]
        [setattr(i, 'status', 'unsuccessful') for i in auction.lots if i.numberOfBids == 0 and i.status == 'active']
        cleanup_bids_for_cancelled_lots(auction)
        if not set([i.status for i in auction.lots]).difference(set(['unsuccessful', 'cancelled'])):
            auction.status = 'unsuccessful'
        elif max([i.numberOfBids for i in auction.lots if i.status == 'active']) < 2:
            add_next_award(request)

    else:
        if auction.numberOfBids < 2 and auction.auctionPeriod and auction.auctionPeriod.startDate:
            auction.auctionPeriod.startDate = None
        if auction.numberOfBids == 0:
            auction.status = 'unsuccessful'
        if auction.numberOfBids == 1:
            # auction.status = 'active.qualification'
            add_next_award(request)


def check_complaint_status(request, complaint, now=None):
    if not now:
        now = get_now()
    if complaint.status == 'claim' and calculate_business_date(complaint.dateSubmitted, COMPLAINT_STAND_STILL_TIME, request.auction) < now:
        complaint.status = 'pending'
        complaint.type = 'complaint'
        complaint.dateEscalated = now
    elif complaint.status == 'answered' and calculate_business_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, request.auction) < now:
        complaint.status = complaint.resolutionType


def check_status(request):
    auction = request.validated['auction']
    now = get_now()
    for complaint in auction.complaints:
        check_complaint_status(request, complaint, now)
    for award in auction.awards:
        for complaint in award.complaints:
            check_complaint_status(request, complaint, now)
    if auction.status == 'active.enquiries' and not auction.tenderPeriod.startDate and auction.enquiryPeriod.endDate.astimezone(TZ) <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction.id, 'active.tendering'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.tendering'}))
        auction.status = 'active.tendering'
        return
    elif auction.status == 'active.enquiries' and auction.tenderPeriod.startDate and auction.tenderPeriod.startDate.astimezone(TZ) <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction.id, 'active.tendering'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.tendering'}))
        auction.status = 'active.tendering'
        return
    elif not auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        if auction.numberOfBids < 2 and auction.auctionPeriod:
            auction.auctionPeriod.startDate = None
        return
    elif auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        [setattr(i.auctionPeriod, 'startDate', None) for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return
    elif not auction.lots and auction.status == 'active.awarded':
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        if not standStillEnds:
            return
        standStillEnd = max(standStillEnds)
        if standStillEnd <= now:
            check_auction_status(request)
    elif auction.lots and auction.status in ['active.qualification', 'active.awarded']:
        if any([i['status'] in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints]):
            return
        for lot in auction.lots:
            if lot['status'] != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if a.complaintPeriod.endDate
            ]
            if not standStillEnds:
                continue
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                check_auction_status(request)
                return


def check_auction_status(request):
    auction = request.validated['auction']
    now = get_now()
    if auction.lots:
        if any([i.status in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints]):
            return
        for lot in auction.lots:
            if lot.status != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_complaints = any([
                i['status'] in auction.block_complaint_status and i.relatedLot == lot.id
                for i in auction.complaints
            ])
            pending_awards_complaints = any([
                i.status in auction.block_complaint_status
                for a in lot_awards
                for i in a.complaints
            ])
            stand_still_end = max([
                a.complaintPeriod.endDate or now
                for a in lot_awards
            ])
            if pending_complaints or pending_awards_complaints or not stand_still_end <= now:
                continue
            elif last_award.status == 'unsuccessful':
                LOGGER.info('Switched lot {} of auction {} to {}'.format(lot.id, auction.id, 'unsuccessful'),
                            extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_unsuccessful'},
                                                 {'LOT_ID': lot.id}))
                lot.status = 'unsuccessful'
                continue
            elif last_award.status == 'active' and any([i.status == 'active' and i.awardID == last_award.id for i in auction.contracts]):
                LOGGER.info('Switched lot {} of auction {} to {}'.format(lot.id, auction.id, 'complete'),
                            extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_complete'},
                                                 {'LOT_ID': lot.id}))
                lot.status = 'complete'
        statuses = set([lot.status for lot in auction.lots])
        if statuses == set(['cancelled']):
            LOGGER.info('Switched lot {} of auction {} to {}'.format(lot.id, auction.id, 'cancelled'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_cancelled'},
                                             {'LOT_ID': lot.id}))
            auction.status = 'cancelled'
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            LOGGER.info('Switched lot {} of auction {} to {}'.format(lot.id, auction.id, 'unsuccessful'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_unsuccessful'},
                                             {'LOT_ID': lot.id}))
            auction.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            LOGGER.info('Switched lot {} of auction {} to {}'.format(lot.id, auction.id, 'complete'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_complete'},
                                             {'LOT_ID': lot.id}))
            auction.status = 'complete'
    else:
        pending_complaints = any([
            i.status in auction.block_complaint_status
            for i in auction.complaints
        ])
        pending_awards_complaints = any([
            i.status in auction.block_complaint_status
            for a in auction.awards
            for i in a.complaints
        ])
        stand_still_ends = [
            a.complaintPeriod.endDate
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        stand_still_end = max(stand_still_ends) if stand_still_ends else now
        stand_still_time_expired = stand_still_end < now
        last_award_status = auction.awards[-1].status if auction.awards else ''
        if not pending_complaints and not pending_awards_complaints and stand_still_time_expired \
                and last_award_status == 'unsuccessful':
            LOGGER.info('Switched auction {} to {}'.format(auction.id, 'unsuccessful'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_unsuccessful'}))
            auction.status = 'unsuccessful'
        if auction.contracts and auction.contracts[-1].status == 'active':
            LOGGER.info('Switched auction {} to {}'.format(auction.id, 'unsuccessful'),
                        extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_complete'}))
            auction.status = 'complete'


def add_next_award(request):
    auction = request.validated['auction']
    now = get_now()
    if not auction.awardPeriod:
        auction.awardPeriod = type(auction).awardPeriod({})
    if not auction.awardPeriod.startDate:
        auction.awardPeriod.startDate = now
    if auction.lots:
        statuses = set()
        for lot in auction.lots:
            if lot.status != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            if lot_awards and lot_awards[-1].status in ['pending', 'active']:
                statuses.add(lot_awards[-1].status if lot_awards else 'unsuccessful')
                continue
            lot_items = [i.id for i in auction.items if i.relatedLot == lot.id]
            features = [
                i
                for i in (auction.features or [])
                if i.featureOf == 'tenderer' or i.featureOf == 'lot' and i.relatedItem == lot.id or i.featureOf == 'item' and i.relatedItem in lot_items
            ]
            codes = [i.code for i in features]
            bids = [
                {
                    'id': bid.id,
                    'value': [i for i in bid.lotValues if lot.id == i.relatedLot][0].value,
                    'tenderers': bid.tenderers,
                    'parameters': [i for i in bid.parameters if i.code in codes],
                    'date': [i for i in bid.lotValues if lot.id == i.relatedLot][0].date
                }
                for bid in auction.bids
                if lot.id in [i.relatedLot for i in bid.lotValues]
            ]
            if not bids:
                lot.status = 'unsuccessful'
                statuses.add('unsuccessful')
                continue
            unsuccessful_awards = [i.bid_id for i in lot_awards if i.status == 'unsuccessful']
            bids = chef(bids, features, unsuccessful_awards, True)
            if bids:
                bid = bids[0]
                award = type(auction).awards.model_class({
                    'bid_id': bid['id'],
                    'lotID': lot.id,
                    'status': 'pending',
                    'value': bid['value'],
                    'date': get_now(),
                    'suppliers': bid['tenderers'],
                    'complaintPeriod': {
                        'startDate': now.isoformat()
                    }
                })
                auction.awards.append(award)
                request.response.headers['Location'] = request.route_url('{}:Auction Awards'.format(auction.procurementMethodType), auction_id=auction.id, award_id=award['id'])
                statuses.add('pending')
            else:
                statuses.add('unsuccessful')
        if statuses.difference(set(['unsuccessful', 'active'])):
            auction.awardPeriod.endDate = None
            auction.status = 'active.qualification'
        else:
            auction.awardPeriod.endDate = now
            auction.status = 'active.awarded'
    else:
        if not auction.awards or auction.awards[-1].status not in ['pending', 'active']:
            unsuccessful_awards = [i.bid_id for i in auction.awards if i.status == 'unsuccessful']
            bids = chef(auction.bids, auction.features or [], unsuccessful_awards, True)
            if bids:
                bid = bids[0].serialize()
                award = type(auction).awards.model_class({
                    'bid_id': bid['id'],
                    'status': 'pending',
                    'date': get_now(),
                    'value': bid['value'],
                    'suppliers': bid['tenderers'],
                    'complaintPeriod': {
                        'startDate': get_now().isoformat()
                    }
                })
                auction.awards.append(award)
                request.response.headers['Location'] = request.route_url('{}:Auction Awards'.format(auction.procurementMethodType), auction_id=auction.id, award_id=award['id'])
        if auction.awards[-1].status == 'pending':
            auction.awardPeriod.endDate = None
            auction.status = 'active.qualification'
        else:
            auction.awardPeriod.endDate = now
            auction.status = 'active.awarded'


def error_handler(errors, request_params=True):
    params = {
        'ERROR_STATUS': errors.status
    }
    if request_params:
        params['ROLE'] = str(errors.request.authenticated_role)
        if errors.request.params:
            params['PARAMS'] = str(dict(errors.request.params))
    if errors.request.matchdict:
        for x, j in errors.request.matchdict.items():
            params[x.upper()] = j
    if 'auction' in errors.request.validated:
        params['AUCTION_REV'] = errors.request.validated['auction'].rev
        params['AUCTIONID'] = errors.request.validated['auction'].auctionID
        params['AUCTION_STATUS'] = errors.request.validated['auction'].status
    LOGGER.info('Error on processing request "{}"'.format(dumps(errors, indent=4)),
                extra=context_unpack(errors.request, {'MESSAGE_ID': 'error_handler'}, params))
    return json_error(errors)


opresource = partial(resource, error_handler=error_handler, factory=factory)


def set_logging_context(event):
    request = event.request
    params = {}
    params['ROLE'] = str(request.authenticated_role)
    if request.params:
        params['PARAMS'] = str(dict(request.params))
    if request.matchdict:
        for x, j in request.matchdict.items():
            params[x.upper()] = j
    if 'auction' in request.validated:
        params['AUCTION_REV'] = request.validated['auction'].rev
        params['AUCTIONID'] = request.validated['auction'].auctionID
        params['AUCTION_STATUS'] = request.validated['auction'].status
    update_logging_context(request, params)


def auction_from_data(request, data, raise_error=True, create=True):
    procurementMethodType = data.get('procurementMethodType', 'belowThreshold')
    model = request.registry.auction_procurementMethodTypes.get(procurementMethodType)
    if model is None and raise_error:
       request.errors.add('data', 'procurementMethodType', 'Not implemented')
       request.errors.status = 415
       raise error_handler(request.errors)
    update_logging_context(request, {'auction_type': procurementMethodType})
    if model is not None and create:
       model = model(data)
    return model


def extract_auction_adapter(request, auction_id):
    db = request.registry.db
    doc = db.get(auction_id)
    if doc is None or doc.get('doc_type') != 'Auction':
        request.errors.add('url', 'auction_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.auction_from_data(doc)


def extract_auction(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ['PATH_INFO'] or '/')
    except KeyError:
        path = '/'
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)

    auction_id = ""
    # extract auction id
    parts = path.split('/')
    if len(parts) < 4 or parts[3] != 'auctions':
        return

    auction_id = parts[4]
    return extract_auction_adapter(request, auction_id)


class isAuction(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'auctionsprocurementMethodType = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.auction is not None:
            return getattr(request.auction, 'procurementMethodType', None) == self.val
        return False


def register_auction_procurementMethodType(config, model):
    """Register a auction procurementMethodType.
    :param config:
        The pyramid configuration object that will be populated.
    :param model:
        The auction model class
    """
    config.registry.auction_procurementMethodTypes[model.procurementMethodType.default] = model
