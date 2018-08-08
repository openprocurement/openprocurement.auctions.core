# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime, timedelta, time
from string import hexdigits
from uuid import uuid4
from urlparse import (
    urlparse,
    parse_qs
)
from zope.deprecation import deprecated
from openprocurement.auctions.core.interfaces import IAuction
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import (
    blacklist,
    whitelist
)
from schematics.types import (
    StringType,
    IntType,
    URLType,
    MD5Type,
    BooleanType,
    FloatType,
    BaseType
)

from schematics.types.serializable import serializable
from schematics_flexible.schematics_flexible import FlexibleModelType
from openprocurement.schemas.dgf.schemas_store import SchemaStore

from barbecue import vnmax

from openprocurement.api.constants import TZ, SANDBOX_MODE, AUCTIONS_COMPLAINT_STAND_STILL_TIME
from openprocurement.api.interfaces import IAwardingNextCheck
from openprocurement.api.models.auction_models import (
    Address,
    CPV_CODES,
    Cancellation as BaseCancellation,
    Classification,
    ComplaintModelType,  # noqa forwarded import
    Contract as BaseContract,
    Document as BaseDocument,
    Feature,
    Identifier as BaseIdentifier,
    IsoDateTimeType,
    Item as BaseItem,
    ListType,
    Location,
    Model,
    ModelType,
    Organization as BaseOrganization,
    Value,
    schematics_default_role,
    schematics_embedded_role,
    validate_features_uniq,
    validate_lots_uniq,
)
from openprocurement.api.models.common import (
    AuctionParameters,  # noqa forwarded import
    BankAccount,  # noqa forwarded import
    BaseResourceItem,
    ContactPoint,  # noqa forwarded import
    Guarantee,
    Period,
    PeriodEndRequired as AuctionPeriodEndRequired,
    RegistrationDetails,
    Revision,
    sensitive_embedded_role,
)
from openprocurement.api.models.schematics_extender import DecimalType
from openprocurement.api.utils import get_now, get_request_from_root, serialize_document_url
from openprocurement.api.validation import validate_items_uniq  # noqa forwarded import

from openprocurement.auctions.core.constants import (
    DOCUMENT_TYPE_OFFLINE,
    DOCUMENT_TYPE_URL_ONLY,
    INFORMATION_DOCUMENT_TYPES,
    CAV_CODES_DGF,
    CAV_CODES_FLASH,
    ORA_CODES,
    CPVS_CODES_DGF_CDB2,
    CAVPS_CODES_DGF_CDB2,
    CPV_NON_SPECIFIC_LOCATION_UNITS_DGF_CDB2,
    CAV_NON_SPECIFIC_LOCATION_UNITS_DGF_CDB2,
    DGF_CDB2_ADDRESS_REQUIRED_FROM,
    DGF_CDB2_CLASSIFICATION_PRECISELY_FROM
)
from openprocurement.auctions.core.utils import get_auction_creation_date
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)


view_complaint_role = (blacklist('owner_token', 'owner') + schematics_default_role)
auction_embedded_role = sensitive_embedded_role
