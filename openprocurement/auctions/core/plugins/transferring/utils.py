# -*- coding: utf-8 -*-
from functools import partial
from hashlib import sha512
from logging import getLogger
from cornice.resource import resource
from schematics.exceptions import ModelValidationError
from openprocurement.api.utils import error_handler, context_unpack, get_now

from openprocurement.auctions.core.plugins.transferring.traversal import factory
from openprocurement.auctions.core.plugins.transferring.models import Transfer


transferresource = partial(resource, error_handler=error_handler,
                           factory=factory)

LOGGER = getLogger(__name__)


def extract_transfer(request, transfer_id=None):
    db = request.registry.db
    if not transfer_id:
        transfer_id = request.matchdict['transfer_id']
    doc = db.get(transfer_id)
    if doc is None or doc.get('doc_type') != 'Transfer':
        request.errors.add('url', 'transfer_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request)

    return request.transfer_from_data(doc)


def transfer_from_data(request, data): #pylint: disable=unused-argument
    return Transfer(data)


def save_transfer(request):
    """ Save transfer object to database
    :param request:
    :return: True if Ok
    """
    transfer = request.validated['transfer']
    transfer.date = get_now()
    try:
        transfer.store(request.registry.db)
    except ModelValidationError, err:  # pragma: no cover
        for i in err.message:
            request.errors.add('body', i, err.message[i])
        request.errors.status = 422
    except Exception, err:  # pragma: no cover
        request.errors.add('body', 'data', str(err))
    else:
        LOGGER.info('Saved transfer %s: at %s', transfer.id, get_now().isoformat(),
                    extra=context_unpack(request, {'MESSAGE_ID': 'save_transfer'}))
        return True


def set_ownership(item, request, access_token=None, transfer_token=None):
    item.owner = request.authenticated_userid
    item.access_token = sha512(access_token).hexdigest()
    item.transfer_token = sha512(transfer_token).hexdigest()


def update_ownership(auction, transfer):
    auction.owner = transfer.owner
    auction.owner_token = transfer.access_token
    auction.transfer_token = transfer.transfer_token
