# -*- coding: utf-8 -*-
from datetime import datetime, time, timedelta
from functools import partial
from logging import getLogger
from re import compile as re_compile
from time import sleep

from couchdb.http import ResourceConflict
from jsonpointer import resolve_pointer
from cornice.resource import resource
from pkg_resources import get_distribution
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError
from schematics.exceptions import ModelValidationError

from openprocurement.api.constants import (
    TZ, SANDBOX_MODE,
    AUCTIONS_COMPLAINT_STAND_STILL_TIME,
    DOCUMENT_BLACKLISTED_FIELDS as API_DOCUMENT_BLACKLISTED_FIELDS,
    SESSION  # noqa forwarded import
)
from openprocurement.api.interfaces import (
    IProjectConfigurator  # noqa forwarded import
)
from openprocurement.api.validation import error_handler

from openprocurement.api.utils import (
    get_now,
    calculate_business_date,
    apply_data_patch,
    get_revision_changes,
    set_modetest_titles,
    update_logging_context,
    context_unpack,
    log_auction_status_change,
    json_view,  # noqa forwarded import
    APIResource,  # noqa forwarded import
    set_specific_hour, # noqa forwarded import
    get_file,
    upload_file,
    connection_mock_config,  # noqa forwarded import
    update_file_content_type,  # noqa forwarded import
    set_ownership,  # noqa forwarded import
    get_request_from_root,  # noqa forwarded import
    get_content_configurator,  # noqa forwarded import
    get_plugin_aliases,  # noqa forwarded import
    get_evenly_plugins,  # noqa forwarded import
    get_plugins,  # noqa forwarded import
    get_forbidden_users, # noqa forwarded import
    utcoffset_difference, # noqa forwarded import
    validate_with, # noqa forwarded import
    time_dependent_value  # noqa forwarded import
)

from openprocurement.auctions.core.constants import (
    DOCUMENT_TYPE_URL_ONLY,
    DOCUMENT_TYPE_OFFLINE,
    MINIMAL_PERIOD_FROM_RECTIFICATION_END,
)
from openprocurement.auctions.core.interfaces import IAuction, IAuctionManager
from openprocurement.auctions.core.plugins.awarding import includeme as awarding
from openprocurement.auctions.core.plugins.contracting import includeme as contracting
from openprocurement.auctions.core.traversal import factory
from openprocurement.auctions.core.configurator import project_configurator


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)
ACCELERATOR_RE = re_compile(r'.accelerator=(?P<accelerator>\d+)')
VERSION = '{}.{}'.format(
    int(PKG.parsed_version[0]),
    int(PKG.parsed_version[1]) if PKG.parsed_version[1].isdigit() else 0
)
ROUTE_PREFIX = '/api/{}'.format(VERSION)
DOCUMENT_BLACKLISTED_FIELDS = (
    'title',
    'format',
    '__parent__',
    'id',
    'url',
    'dateModified',
)


class awardingTypePredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'awardingType = {value}'.format(value=self.val)

    phash = text

    def __call__(self, context, request):
        if request.auction is not None:
            procurement_method_type = getattr(
                request.auction,
                'procurementMethodType',
                None
            )
            if not procurement_method_type:
                return False

            desirable_awarding_version = request.content_configurator.awarding_type
            return desirable_awarding_version == self.val

        return False


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
    return project_configurator.AUCTION_PREFIX + '-{:04}-{:02}-{:02}-{:06}{}'.format(
        ctime.year,
        ctime.month,
        ctime.day,
        index,
        server_id and '-' + server_id
    )


def auction_serialize(request, auction_data, fields):
    auction = request.auction_from_data(auction_data, raise_error=False)
    if auction is None:
        return dict([(i, auction_data.get(i, '')) for i in ['procurementMethodType', 'dateModified', 'id']])
    auction.__parent__ = request.context
    return dict([(i, j) for i, j in auction.serialize(auction.status).items() if i in fields])


def save_auction(request):

    auction = request.validated['auction']
    if request.authenticated_role == 'Administrator':
        can_be_changed = ['procurementMethodDetails']
        for field in can_be_changed:
            if field in request.json['data']:
                auction[field] = request.json['data'][field]

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
        except ModelValidationError as e:
            for i in e.message:
                request.errors.add('body', i, e.message[i])
            request.errors.status = 422
        except ResourceConflict as e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
            request.errors.status = 409
        except Exception as e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
        else:
            predict = old_dateModified and old_dateModified.isoformat()
            LOGGER.info('Saved auction %s: dateModified %s -> %s', auction.id, predict, auction.dateModified.isoformat(),
                        extra=context_unpack(request, {'MESSAGE_ID': 'save_auction'}, {'RESULT': auction.rev}))
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated['data'] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_auction(request)
        return True


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
    adapter = request.registry.getAdapter(auction, IAuctionManager)
    if auction.lots:
        _ = [setattr(i.auctionPeriod, 'startDate', None) for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate]
        _ = [setattr(i, 'status', 'unsuccessful') for i in auction.lots if i.numberOfBids == 0 and i.status == 'active']
        cleanup_bids_for_cancelled_lots(auction)
        if not set([i.status for i in auction.lots]).difference(set(['unsuccessful', 'cancelled'])):
            adapter.pendify_auction_status('unsuccessful')
        elif max([i.numberOfBids for i in auction.lots if i.status == 'active']) < 2:
            request.content_configurator.start_awarding()

    else:
        if auction.numberOfBids < 2 and auction.auctionPeriod and auction.auctionPeriod.startDate:
            auction.auctionPeriod.startDate = None
        if auction.numberOfBids == 0:
            adapter.pendify_auction_status('unsuccessful')
        if auction.numberOfBids == 1:
            # auction.status = 'active.qualification'
            request.content_configurator.start_awarding()


def check_complaint_status(request, complaint, now=None):
    if not now:
        now = get_now()
    if complaint.status == 'claim' and calculate_business_date(complaint.dateSubmitted, AUCTIONS_COMPLAINT_STAND_STILL_TIME, request.auction) < now:
        complaint.status = 'pending'
        complaint.type = 'complaint'
        complaint.dateEscalated = now
    elif complaint.status == 'answered' and calculate_business_date(complaint.dateAnswered, AUCTIONS_COMPLAINT_STAND_STILL_TIME, request.auction) < now:
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
        auction.status = 'active.tendering'
        log_auction_status_change(request, auction, auction.status)
        return True
    elif auction.status == 'active.enquiries' and auction.tenderPeriod.startDate and auction.tenderPeriod.startDate.astimezone(TZ) <= now:
        auction.status = 'active.tendering'
        log_auction_status_change(request, auction, auction.status)
        return True
    elif not auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        if auction.numberOfBids < 2 and auction.auctionPeriod:
            auction.auctionPeriod.startDate = None
        log_auction_status_change(request, auction, auction.status)
        return True
    elif auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        _ = [setattr(i.auctionPeriod, 'startDate', None) for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod]
        log_auction_status_change(request, auction, auction.status)
        return True
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
    adapter = request.registry.getAdapter(auction, IAuctionManager)
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
                LOGGER.info('Switched lot %s of auction %s to %s', lot.id, auction.id, 'unsuccessful',
                            extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_unsuccessful'}, {'LOT_ID': lot.id}))
                lot.status = 'unsuccessful'
                continue
            elif last_award.status == 'active' and any([i.status == 'active' and i.awardID == last_award.id for i in auction.contracts]):
                LOGGER.info('Switched lot %s of auction %s to %s', lot.id, auction.id, 'complete',
                            extra=context_unpack(request, {'MESSAGE_ID': 'switched_lot_complete'}, {'LOT_ID': lot.id}))
                lot.status = 'complete'
        statuses = set([lot.status for lot in auction.lots])
        if statuses == set(['cancelled']):
            adapter.pendify_auction_status('cancelled')
            log_auction_status_change(request, auction, auction.status)
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            adapter.pendify_auction_status('unsuccessful')
            log_auction_status_change(request, auction, auction.status)
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            adapter.pendify_auction_status('complete')
            log_auction_status_change(request, auction, auction.status)
    else:
        if auction.contracts and auction.contracts[-1].status == 'active':
            adapter.pendify_auction_status('complete')
            log_auction_status_change(request, auction, auction.status)


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
    if 'auction' in request.validated and IAuction.providedBy(request.validated['auction']):
        params['AUCTION_REV'] = request.validated['auction'].rev
        params['AUCTIONID'] = request.validated['auction'].auctionID
        params['AUCTION_STATUS'] = request.validated['auction'].status
    update_logging_context(request, params)


def get_procurement_method_types(registry, procedure_types):
    pmtConfigurator = registry.pmtConfigurator
    procurement_method_types = [
        pmt for pmt in pmtConfigurator
        if pmtConfigurator[pmt] in procedure_types
    ]
    return procurement_method_types


def auction_from_data(request, data, raise_error=True, create=True):
    procurementMethodType = data.get('procurementMethodType')
    if not procurementMethodType:
        pmts = get_procurement_method_types(request.registry, ('belowThreshold',))
        procurementMethodType = pmts[0] if pmts else 'belowThreshold'
    model = request.registry.auction_procurementMethodTypes.get(procurementMethodType)
    if model is None and raise_error:
        request.errors.add('body', 'data', 'procurementMethodType is not implemented')
        request.errors.status = 415
        raise error_handler(request)
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
        raise error_handler(request)

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
        pmt = getattr(request.auction, 'procurementMethodType', None)
        if request.auction is not None:
            return request.registry.pmtConfigurator.get(pmt) == self.val
        return False


class SubscribersPicker(isAuction):
    """ Subscriber predicate. """

    def __call__(self, event):
        pmt = getattr(event.request.auction, 'procurementMethodType', None)
        if event.request.auction is not None:
            return event.request.registry.pmtConfigurator.get(pmt) == self.val
        return False


def register_auction_procurementMethodType(config, model, pmt):
    """Register a auction procurementMethodType.
    :param config:
        The pyramid configuration object that will be populated.
    :param model:
        The auction model class
    :param pmt:
        Procurement method type associated with procedure type
    """
    config.registry.pmtConfigurator[pmt] = model._internal_type
    config.registry.auction_procurementMethodTypes[pmt] = model


def get_related_contract_of_award(award_id, auction):
    for contract in auction['contracts']:
        if contract['awardID'] == award_id:
            return contract


def get_related_award_of_contract(contract, auction):
    for award in auction['awards']:
        if contract['awardID'] == award['id']:
            return award


def init_plugins(config):
    awarding.includeme(config)
    contracting.includeme(config)


def get_auction_creation_date(data):
    if data.get('doc_type') != u'Auction':
        while data.get('doc_type') == u"Auction":
            data = data['__parent__']
    auction_creation_date = (data.get('revisions')[0].date if data.get('revisions') else get_now())
    return auction_creation_date


def rounding_shouldStartAfter_after_midnigth(start_after, auction, use_from=datetime(2016, 6, 1, tzinfo=TZ)):
    if (auction.enquiryPeriod and auction.enquiryPeriod.startDate or get_now()) > use_from and not (SANDBOX_MODE and auction.submissionMethodDetails and u'quick' in auction.submissionMethodDetails):
        midnigth = datetime.combine(start_after.date(), time(0, tzinfo=start_after.tzinfo))
        if start_after >= midnigth:
            start_after = midnigth + timedelta(1)
    return start_after


def get_auction_route_name(request, auction):
    pmtConfigurator = request.registry.pmtConfigurator
    procedure_type = pmtConfigurator[auction.procurementMethodType]
    return '{}:Auction'.format(procedure_type)


def dgf_upload_file(request, blacklisted_fields=API_DOCUMENT_BLACKLISTED_FIELDS):
    first_document = request.validated['documents'][0] if 'documents' in request.validated and request.validated['documents'] else None
    if 'data' in request.validated and request.validated['data']:
        document = request.validated['document']
        if document.documentType in (DOCUMENT_TYPE_URL_ONLY + DOCUMENT_TYPE_OFFLINE):
            if first_document:
                for attr_name in type(first_document)._fields:
                    if attr_name not in blacklisted_fields:
                        setattr(document, attr_name, getattr(first_document, attr_name))
            if document.documentType in DOCUMENT_TYPE_OFFLINE:
                document.format = 'offline/on-site-examination'
            return document
    return upload_file(request, blacklisted_fields)


def dgf_get_file(request):
    document = request.validated['document']
    if document.documentType in DOCUMENT_TYPE_URL_ONLY:
        request.response.status = '302 Moved Temporarily'
        request.response.location = document.url
        return document.url
    return get_file(request)


def get_auction(model):
    while not IAuction.providedBy(model):
        model = getattr(model, '__parent__', None)
        if model is None:
            return None
    return model


def remove_bid(request, auction, bid):
    auction.bids.remove(bid)
    extra = context_unpack(request, {'MESSAGE_ID': 'remove_bid: {}'.format(bid.id)})
    LOGGER.info('Remove bid', extra=extra)


def generate_rectificationPeriod_tender_period_margin(auction, tp_margin=MINIMAL_PERIOD_FROM_RECTIFICATION_END):
    """Generate rectificationPeriod for an auction basing on margin from the end of the tenderPeriod

        :param auction: auction model
        :param tp_margin: timedelta; margin from the end of
            the tenderPertiod to the end of rectificationPeriod.
            It's default value is 5 days.
    """
    now = get_now()
    period = auction.rectificationPeriod
    if not period:
        period = type(auction).rectificationPeriod.model_class()

    period.startDate = period.startDate or now
    if not period.endDate:
        calculated_endDate = TZ.localize(
            calculate_business_date(
                auction.tenderPeriod.endDate,
                -tp_margin,
                auction
            ).replace(tzinfo=None))
        period.endDate = calculated_endDate if calculated_endDate > now else now
    period.invalidationDate = None
    return period
