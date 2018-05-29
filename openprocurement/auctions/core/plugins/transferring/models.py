# -*- coding: utf-8 -*-
from uuid import uuid4

from couchdb_schematics.document import SchematicsDocument
from schematics.types import StringType
from schematics.types.serializable import serializable
from schematics.transforms import whitelist

from openprocurement.api.models.schematics_extender import (
    IsoDateTimeType,
    Model
)
from openprocurement.api.models.auction_models import schematics_default_role
from openprocurement.api.models.roles import plain_role
from openprocurement.api.utils import get_now


class Transfer(SchematicsDocument, Model):

    class Options:
        roles = {
            'plain': plain_role,
            'default': schematics_default_role,
            'create': whitelist(),
            'view': whitelist('id', 'doc_id', 'date', 'usedFor'),
        }

    owner = StringType(min_length=1)
    access_token = StringType(min_length=1, default=lambda: uuid4().hex)
    transfer_token = StringType(min_length=1, default=lambda: uuid4().hex)
    date = IsoDateTimeType(default=get_now)
    usedFor = StringType(min_length=32)  # object path (e.g. /auctions/{id})

    def __init__(self, *args, **kwargs):
        super(Transfer, self).__init__(*args, **kwargs)
        self.doc_type = "Transfer"

    def __repr__(self):
        return '<%s:%r@%r>' % (type(self).__name__, self.id, self.rev)

    @serializable(serialized_name='id')
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id
