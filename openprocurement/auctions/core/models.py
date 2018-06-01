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
from couchdb_schematics.document import SchematicsDocument
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

from schematics.types.compound import DictType
from schematics.types.serializable import serializable
from schematics_flexible.schematics_flexible import FlexibleModelType
from openprocurement.schemas.dgf.schemas_store import SchemaStore

from barbecue import vnmax

from openprocurement.api.constants import TZ, SANDBOX_MODE, AUCTIONS_COMPLAINT_STAND_STILL_TIME
from openprocurement.api.interfaces import IAwardingNextCheck
from openprocurement.api.models.auction_models import (
    Model,
    Value,
    Contract as BaseContract,
    Document as BaseDocument,
    ListType,
    Item as BaseItem,
    Identifier as BaseIdentifier,
    ModelType,
    Classification,
    Organization as BaseOrganization,
    Address,
    Location,
    CPV_CODES,
    schematics_embedded_role,
    schematics_default_role,
    IsoDateTimeType,
    Cancellation as BaseCancellation,
    Feature,
    validate_features_uniq,
    validate_lots_uniq,
    ComplaintModelType  # noqa forwarded import
)
from openprocurement.api.models.common import (
    Period,
    Guarantee,
    PeriodEndRequired as AuctionPeriodEndRequired,
    Revision,
    BaseResourceItem,
    sensitive_embedded_role,
    BankAccount,  # noqa forwarded import
    AuctionParameters,  # noqa forwarded import
)
from openprocurement.api.models.schematics_extender import DecimalType
from openprocurement.api.utils import get_now, get_request_from_root
from openprocurement.api.validation import validate_items_uniq  # noqa forwarded import

from openprocurement.auctions.core.constants import (
    DOCUMENT_TYPE_OFFLINE,
    DOCUMENT_TYPE_URL_ONLY,
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


deprecated('IAuction', 'IAuction moved to interfaces.py')

def get_auction(model):
    while not IAuction.providedBy(model):
        model = model.__parent__
    return model


class dgfCAVClassification(Classification):
    scheme = StringType(required=True, default=u'CAV', choices=[u'CAV'])
    id = StringType(required=True, choices=CAV_CODES_DGF)


class flashCAVClassification(Classification):
    scheme = StringType(required=True, default=u'CAV', choices=[u'CAV'])
    id = StringType(required=True, choices=CAV_CODES_FLASH)


ADDITIONAL_CLASSIFICATIONS_SCHEMES = [u'ДКПП', u'NONE', u'ДК003', u'ДК015', u'ДК018']


def validate_dkpp(items, *args):
    if items and not any([i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES for i in items]):
        raise ValidationError(u"One of additional classifications should be one of [{0}].".format(', '.join(ADDITIONAL_CLASSIFICATIONS_SCHEMES)))


class flashItem(BaseItem):
    """A good, service, or work to be contracted."""
    classification = ModelType(flashCAVClassification, required=True)
    additionalClassifications = ListType(ModelType(Classification), default=list(), validators=[validate_dkpp]) # required=True, min_size=1,
    quantity = DecimalType()  # The number of units required

    def validate_relatedLot(self, data, relatedLot):
        if relatedLot and isinstance(data['__parent__'], Model) and relatedLot not in [i.id for i in get_auction(data['__parent__']).lots]:
            raise ValidationError(u"relatedLot should be one of lots")


class dgfItem(flashItem):
    """A good, service, or work to be contracted."""
    class Options:
        roles = {
            'create': blacklist('deliveryLocation', 'deliveryAddress', 'deliveryDate'),
            'edit_active.tendering': blacklist('deliveryLocation', 'deliveryAddress', 'deliveryDate'),
        }
    classification = ModelType(dgfCAVClassification, required=True)
    additionalClassifications = ListType(ModelType(Classification), default=list())
    address = ModelType(Address)
    location = ModelType(Location)
    schema_properties = FlexibleModelType(SchemaStore())

    def validate_schema_properties(self, data, new_schema_properties):
        """ Raise validation error if code in schema_properties mismatch
            with classification id """
        if new_schema_properties and not data['classification']['id'].startswith(new_schema_properties['code']):
            raise ValidationError("classification id mismatch with schema_properties code")


class dgfCDB2CPVCAVClassification(Classification):
    """
    Classification for CDB2 which use CPV and CAV-PS scheme and validate code according to them.
    """
    scheme = StringType(required=True, default=u'CPV', choices=[u'CPV', u'CAV-PS'])
    id = StringType(required=True)

    def validate_id(self, data, code):
        auction = get_auction(data['__parent__'])
        if data.get('scheme') == u'CPV' and code not in CPV_CODES:
            raise ValidationError(BaseType.MESSAGES['choices'].format(unicode(CPV_CODES)))
        elif data.get('scheme') == u'CAV-PS' and code not in CAVPS_CODES_DGF_CDB2:
            raise ValidationError(BaseType.MESSAGES['choices'].format(unicode(CAVPS_CODES_DGF_CDB2)))
        if code.find("00000-") > 0 and get_auction_creation_date(auction) > DGF_CDB2_CLASSIFICATION_PRECISELY_FROM:
            raise ValidationError('At least {} classification class (XXXX0000-Y) should be specified more precisely'.format(data.get('scheme')))


class dgfCDB2AdditionalClassification(Classification):
    def validate_id(self, data, code):
        if data.get('scheme') == u'CPVS' and code not in CPVS_CODES_DGF_CDB2:
            raise ValidationError(BaseType.MESSAGES['choices'].format(unicode(CPVS_CODES_DGF_CDB2)))


class dgfCDB2Item(flashItem):
    """A good, service, or work to be contracted."""
    class Options:
        roles = {
            'create': blacklist('deliveryLocation', 'deliveryAddress'),
            'edit_active.tendering': blacklist('deliveryLocation', 'deliveryAddress'),
        }
    classification = ModelType(dgfCDB2CPVCAVClassification, required=True)
    additionalClassifications = ListType(ModelType(dgfCDB2AdditionalClassification), default=list())
    address = ModelType(Address)
    location = ModelType(Location)
    contractPeriod = ModelType(Period)

    def __init__(self, *args, **kwargs):
        super(dgfCDB2Item, self).__init__(*args, **kwargs)
        if hasattr(self, 'deliveryDate'):
            del self.deliveryDate

    def validate_address(self, data, address):
        if not address:
            auction = get_auction(data['__parent__'])
            if get_auction_creation_date(auction) > DGF_CDB2_ADDRESS_REQUIRED_FROM:
                non_specific_location_cav = data['classification']['scheme'] == u'CAV-PS' and not data['classification']['id'].startswith(CAV_NON_SPECIFIC_LOCATION_UNITS_DGF_CDB2)
                non_specific_location_cpv = data['classification']['scheme'] == u'CPV' and not data['classification']['id'].startswith(CPV_NON_SPECIFIC_LOCATION_UNITS_DGF_CDB2)
                if non_specific_location_cav or non_specific_location_cpv:
                    raise ValidationError(u'This field is required.')


class flashDocument(BaseDocument):

    documentType = StringType(choices=[
        'auctionNotice', 'awardNotice', 'contractNotice',
        'notice', 'biddingDocuments', 'technicalSpecifications',
        'evaluationCriteria', 'clarifications', 'shortlistedFirms',
        'riskProvisions', 'billOfQuantity', 'bidders', 'conflictOfInterest',
        'debarments', 'evaluationReports', 'winningBid', 'complaints',
        'contractSigned', 'contractArrangements', 'contractSchedule',
        'contractAnnexe', 'contractGuarantees', 'subContract',
        'eligibilityCriteria', 'contractProforma', 'commercialProposal',
        'qualificationDocuments', 'eligibilityDocuments', 'tenderNotice',
    ])
    documentOf = StringType(required=True, choices=['tender', 'item', 'lot'], default='tender')

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get('documentOf') in ['item', 'lot']:
            raise ValidationError(u'This field is required.')
        if relatedItem and isinstance(data['__parent__'], Model):
            auction = get_auction(data['__parent__'])
            if data.get('documentOf') == 'lot' and relatedItem not in [i.id for i in auction.lots]:
                raise ValidationError(u"relatedItem should be one of lots")
            if data.get('documentOf') == 'item' and relatedItem not in [i.id for i in auction.items]:
                raise ValidationError(u"relatedItem should be one of items")


class dgfDocument(flashDocument):
    format = StringType(regex='^[-\w]+/[-\.\w\+]+$')
    url = StringType()
    index = IntType()
    accessDetails = StringType()
    documentType = StringType(choices=[
        'auctionNotice', 'awardNotice', 'contractNotice',
        'notice', 'biddingDocuments', 'technicalSpecifications',
        'evaluationCriteria', 'clarifications', 'shortlistedFirms',
        'riskProvisions', 'billOfQuantity', 'bidders', 'conflictOfInterest',
        'debarments', 'evaluationReports', 'winningBid', 'complaints',
        'contractSigned', 'contractArrangements', 'contractSchedule',
        'contractAnnexe', 'contractGuarantees', 'subContract',
        'eligibilityCriteria', 'contractProforma', 'commercialProposal',
        'qualificationDocuments', 'eligibilityDocuments', 'tenderNotice',
        'illustration', 'financialLicense', 'virtualDataRoom',
        'auctionProtocol', 'x_dgfPublicAssetCertificate',
        'x_presentation', 'x_nda', 'x_dgfAssetFamiliarization',
        'x_dgfPlatformLegalDetails',
    ])

    @serializable(serialized_name="url", serialize_when_none=False)
    def download_url(self):
        url = self.url
        if not url or '?download=' not in url:
            return url
        doc_id = parse_qs(urlparse(url).query)['download'][-1]
        root = self.__parent__
        parents = []
        while root.__parent__ is not None:
            parents[0:0] = [root]
            root = root.__parent__
        request = root.request
        if not request.registry.use_docservice:
            return url
        if 'status' in parents[0] and parents[0].status in type(parents[0])._options.roles:
            role = parents[0].status
            for index, obj in enumerate(parents):
                if obj.id != url.split('/')[(index - len(parents)) * 2 - 1]:
                    break
                field = url.split('/')[(index - len(parents)) * 2]
                if "_" in field:
                    field = field[0] + field.title().replace("_", "")[1:]
                roles = type(obj)._options.roles
                if roles[role if role in roles else 'default'](field, []):
                    return url
        from openprocurement.api.utils import generate_docservice_url
        if not self.hash:
            path = [i for i in urlparse(url).path.split('/') if len(i) == 32 and not set(i).difference(hexdigits)]
            return generate_docservice_url(request, doc_id, False, '{}/{}'.format(path[0], path[-1]))
        return generate_docservice_url(request, doc_id, False)

    def validate_hash(self, data, hash_):
        doc_type = data.get('documentType')
        if doc_type in (DOCUMENT_TYPE_URL_ONLY + DOCUMENT_TYPE_OFFLINE) and hash_:
            raise ValidationError(u'This field is not required.')

    def validate_format(self, data, format_):
        doc_type = data.get('documentType')
        if doc_type not in (DOCUMENT_TYPE_URL_ONLY + DOCUMENT_TYPE_OFFLINE) and not format_:
            raise ValidationError(u'This field is required.')
        if doc_type in DOCUMENT_TYPE_URL_ONLY and format_:
            raise ValidationError(u'This field is not required.')

    def validate_url(self, data, url):
        doc_type = data.get('documentType')
        if doc_type in DOCUMENT_TYPE_URL_ONLY:
            URLType().validate(url)
        if doc_type in DOCUMENT_TYPE_OFFLINE and url:
            raise ValidationError(u'This field is not required.')
        if doc_type not in DOCUMENT_TYPE_OFFLINE and not url:
            raise ValidationError(u'This field is required.')

    def validate_accessDetails(self, data, accessDetails):
        if data.get('documentType') in DOCUMENT_TYPE_OFFLINE and not accessDetails:
            raise ValidationError(u'This field is required.')


class dgfCDB2Document(dgfDocument):
    documentType = StringType(choices=[
        'auctionNotice', 'awardNotice', 'contractNotice',
        'notice', 'biddingDocuments', 'technicalSpecifications',
        'evaluationCriteria', 'clarifications', 'shortlistedFirms',
        'riskProvisions', 'billOfQuantity', 'bidders', 'conflictOfInterest',
        'debarments', 'evaluationReports', 'winningBid', 'complaints',
        'contractSigned', 'contractArrangements', 'contractSchedule',
        'contractAnnexe', 'contractGuarantees', 'subContract',
        'eligibilityCriteria', 'contractProforma', 'commercialProposal',
        'qualificationDocuments', 'eligibilityDocuments', 'tenderNotice',
        'illustration', 'auctionProtocol', 'x_dgfAssetFamiliarization',
        'x_presentation', 'x_nda'
    ])


class swiftsureDocument(dgfDocument):
    documentType = StringType(choices=[
        'auctionNotice', 'awardNotice', 'contractNotice',
        'notice', 'biddingDocuments', 'technicalSpecifications',
        'evaluationCriteria', 'clarifications', 'shortlistedFirms',
        'riskProvisions', 'billOfQuantity', 'bidders', 'conflictOfInterest',
        'debarments', 'evaluationReports', 'winningBid', 'complaints',
        'contractSigned', 'contractArrangements', 'contractSchedule',
        'contractAnnexe', 'contractGuarantees', 'subContract',
        'eligibilityCriteria', 'contractProforma', 'commercialProposal',
        'qualificationDocuments', 'eligibilityDocuments', 'tenderNotice',
        'illustration', 'financialLicense', 'virtualDataRoom',
        'auctionProtocol', 'x_dgfPublicAssetCertificate',
        'x_presentation', 'x_nda', 'x_dgfAssetFamiliarization', 'act',
        'x_dgfPlatformLegalDetails', 'admissionProtocol', 'rejectionProtocol'
    ])


class flashComplaint(Model):
    class Options:
        roles = {
            'create': whitelist('author', 'title', 'description', 'status', 'relatedLot'),
            'draft': whitelist('author', 'title', 'description', 'status'),
            'cancellation': whitelist('cancellationReason', 'status'),
            'satisfy': whitelist('satisfied', 'status'),
            'answer': whitelist('resolution', 'resolutionType', 'status', 'tendererAction'),
            'action': whitelist('tendererAction'),
            'review': whitelist('decision', 'status'),
            'view': view_complaint_role,
            'view_claim': (blacklist('author') + view_complaint_role),
            'active.enquiries': view_complaint_role,
            'active.tendering': view_complaint_role,
            'active.auction': view_complaint_role,
            'active.qualification': view_complaint_role,
            'active.awarded': view_complaint_role,
            'complete': view_complaint_role,
            'unsuccessful': view_complaint_role,
            'cancelled': view_complaint_role,
        }
    # system
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    complaintID = StringType()
    date = IsoDateTimeType(default=get_now)  # autogenerated date of posting
    status = StringType(
        choices=['draft', 'claim', 'answered', 'pending', 'invalid', 'resolved', 'declined', 'cancelled'],
        default='draft')
    documents = ListType(ModelType(dgfDocument), default=list())
    type = StringType(choices=['claim', 'complaint'],
                      default='claim')  # 'complaint' if status in ['pending'] or 'claim' if status in ['draft', 'claim', 'answered']
    owner_token = StringType()
    owner = StringType()
    relatedLot = MD5Type()
    # complainant
    author = ModelType(BaseOrganization, required=True)  # author of claim
    title = StringType(required=True)  # title of the claim
    description = StringType()  # description of the claim
    dateSubmitted = IsoDateTimeType()
    # tender owner
    resolution = StringType()
    resolutionType = StringType(choices=['invalid', 'resolved', 'declined'])
    dateAnswered = IsoDateTimeType()
    tendererAction = StringType()
    tendererActionDate = IsoDateTimeType()
    # complainant
    satisfied = BooleanType()
    dateEscalated = IsoDateTimeType()
    # reviewer
    decision = StringType()
    dateDecision = IsoDateTimeType()
    # complainant
    cancellationReason = StringType()
    dateCanceled = IsoDateTimeType()

    def serialize(self, role=None, context=None):
        if role == 'view' and self.type == 'claim' and get_auction(self).status in ['active.enquiries', 'active.tendering']:
            role = 'view_claim'
        return self.to_primitive(role=role, context=context)

    def get_role(self):
        root = self.__parent__
        while root.__parent__ is not None:
            root = root.__parent__
        request = root.request
        data = request.json_body['data']
        if request.authenticated_role == 'complaint_owner' and data.get('status', self.status) == 'cancelled':
            role = 'cancellation'
        elif request.authenticated_role == 'complaint_owner' and self.status == 'draft':
            role = 'draft'
        elif request.authenticated_role == 'auction_owner' and self.status == 'claim':
            role = 'answer'
        elif request.authenticated_role == 'auction_owner' and self.status == 'pending':
            role = 'action'
        elif request.authenticated_role == 'complaint_owner' and self.status == 'answered':
            role = 'satisfy'
        elif request.authenticated_role == 'reviewers' and self.status == 'pending':
            role = 'review'
        else:
            role = 'invalid'
        return role

    def __local_roles__(self):
        return dict([('{}_{}'.format(self.owner, self.owner_token), 'complaint_owner')])

    def __acl__(self):
        return [
            (Allow, 'g:reviewers', 'edit_complaint'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_complaint_documents'),
        ]

    def validate_resolutionType(self, data, resolutionType):
        if not resolutionType and data.get('status') == 'answered':
            raise ValidationError(u'This field is required.')

    def validate_cancellationReason(self, data, cancellationReason):
        if not cancellationReason and data.get('status') == 'cancelled':
            raise ValidationError(u'This field is required.')

    def validate_relatedLot(self, data, relatedLot):
        if relatedLot and isinstance(data['__parent__'], Model) and relatedLot not in [i.id for i in get_auction(data['__parent__']).lots]:
            raise ValidationError(u"relatedLot should be one of lots")


class Identifier(BaseIdentifier):
    scheme = StringType(required=True, choices=ORA_CODES)


class dgfOrganization(BaseOrganization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))


def validate_ua_fin(items, *args):
    if items and not any([i.scheme == u"UA-FIN" for i in items]):
        raise ValidationError(u"One of additional classifications should be UA-FIN.")


class FinancialOrganization(dgfOrganization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier), required=True, validators=[validate_ua_fin])


class dgfComplaint(flashComplaint):
    author = ModelType(dgfOrganization, required=True)
    documents = ListType(ModelType(dgfDocument), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])


class dgfCDB2Complaint(flashComplaint):
    author = ModelType(dgfOrganization, required=True)
    documents = ListType(ModelType(dgfCDB2Document), default=list())


class flashCancellation(BaseCancellation):
    documents = ListType(ModelType(flashDocument), default=list())


class dgfCancellation(BaseCancellation):
    documents = ListType(ModelType(dgfDocument), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])



class Contract(BaseContract):
    class Options:
        roles = {
            'create': blacklist('id', 'status', 'date', 'documents', 'dateSigned'),
            'edit': blacklist('id', 'documents', 'date', 'awardID', 'suppliers', 'items', 'contractID'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }
    awardID = StringType(required=True)

    def validate_awardID(self, data, awardID):
        if (
            awardID
            and isinstance(data['__parent__'], Model)
            and awardID not in [i.id for i in data['__parent__'].awards]
        ):
            raise ValidationError(u"awardID should be one of awards")

    def validate_dateSigned(self, data, value):
        if value and isinstance(data['__parent__'], Model):
            award = [i for i in data['__parent__'].awards if i.id == data['awardID']][0]
            if award.complaintPeriod.endDate >= value:
                raise ValidationError(
                    u"Contract signature date should be after award complaint period end date ({})".format(
                        award.complaintPeriod.endDate.isoformat()
                    )
                )
            if value > get_now():
                raise ValidationError(u"Contract signature date can't be in the future")


class Parameter(Model):

    code = StringType(required=True)
    value = FloatType(required=True)

    def validate_code(self, data, code):
        if isinstance(data['__parent__'], Model) and code not in [i.code for i in (get_auction(data['__parent__']).features or [])]:
            raise ValidationError(u"code should be one of feature code.")

    def validate_value(self, data, value):
        if isinstance(data['__parent__'], Model):
            auction = get_auction(data['__parent__'])
            codes = dict([(i.code, [x.value for x in i.enum]) for i in (auction.features or [])])
            if data['code'] in codes and value not in codes[data['code']]:
                raise ValidationError(u"value should be one of feature value.")


def validate_parameters_uniq(parameters, *args):
    if parameters:
        codes = [i.code for i in parameters]
        if [i for i in set(codes) if codes.count(i) > 1]:
            raise ValidationError(u"Parameter code should be uniq for all parameters")


def rounding_shouldStartAfter(start_after, auction, use_from=datetime(2016, 6, 1, tzinfo=TZ)):
    if (auction.enquiryPeriod and auction.enquiryPeriod.startDate or get_now()) > use_from and not (SANDBOX_MODE and auction.submissionMethodDetails and u'quick' in auction.submissionMethodDetails):
        midnigth = datetime.combine(start_after.date(), time(0, tzinfo=start_after.tzinfo))
        if start_after > midnigth:
            start_after = midnigth + timedelta(1)
    return start_after


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        auction = get_auction(self)
        lot = self.__parent__
        if auction.status not in ['active.tendering', 'active.auction'] or lot.status != 'active':
            return
        if auction.status == 'active.auction' and lot.numberOfBids < 2:
            return
        if self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(auction.numberOfBids, self.startDate)
        else:
            start_after = auction.tenderPeriod.endDate
        return rounding_shouldStartAfter(start_after, auction).isoformat()


class Award(Model):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    class Options:
        roles = {
            'create': blacklist('id', 'status', 'date', 'documents', 'complaints', 'complaintPeriod'),
            'edit': whitelist('status', 'title', 'title_en', 'title_ru',
                              'description', 'description_en', 'description_ru'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'Administrator': whitelist('complaintPeriod'),
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    title = StringType()  # Award title
    title_en = StringType()
    title_ru = StringType()
    description = StringType()  # Award description
    description_en = StringType()
    description_ru = StringType()
    status = StringType(required=True, choices=['pending', 'unsuccessful', 'active', 'cancelled'], default='pending')
    date = IsoDateTimeType(default=get_now)
    value = ModelType(Value)
    suppliers = ListType(ModelType(dgfOrganization), required=True, min_size=1, max_size=1)
    items = ListType(ModelType(dgfCDB2Item))
    documents = ListType(ModelType(dgfCDB2Document), default=list())
    complaints = ListType(ModelType(dgfCDB2Complaint), default=list())
    complaintPeriod = ModelType(Period)

    def validate_lotID(self, data, lotID):
        if isinstance(data['__parent__'], Model):
            if not lotID and data['__parent__'].lots:
                raise ValidationError(u'This field is required.')
            if lotID and lotID not in [i.id for i in data['__parent__'].lots]:
                raise ValidationError(u"lotID should be one of lots")


class LotValue(Model):
    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'create': whitelist('value', 'relatedLot'),
            'edit': whitelist('value', 'relatedLot'),
            'auction_view': whitelist('value', 'date', 'relatedLot', 'participationUrl'),
            'auction_post': whitelist('value', 'date', 'relatedLot'),
            'auction_patch': whitelist('participationUrl', 'relatedLot'),
        }

    value = ModelType(Value, required=True)
    relatedLot = MD5Type(required=True)
    participationUrl = URLType()
    date = IsoDateTimeType(default=get_now)

    def validate_value(self, data, value):
        if value and isinstance(data['__parent__'], Model) and data['relatedLot']:
            lots = [i for i in get_auction(data['__parent__']).lots if i.id == data['relatedLot']]
            if not lots:
                return
            lot = lots[0]
            if lot.value.amount > value.amount:
                raise ValidationError(u"value of bid should be greater than value of lot")
            if lot.get('value').currency != value.currency:
                raise ValidationError(u"currency of bid should be identical to currency of value of lot")
            if lot.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot")

    def validate_relatedLot(self, data, relatedLot):
        if isinstance(data['__parent__'], Model) and relatedLot not in [i.id for i in get_auction(data['__parent__']).lots]:
            raise ValidationError(u"relatedLot should be one of lots")


class Question(Model):
    class Options:
        roles = {
            'create': whitelist('author', 'title', 'description', 'questionOf', 'relatedItem'),
            'edit': whitelist('answer'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'active.enquiries': (blacklist('author') + schematics_embedded_role),
            'active.tendering': (blacklist('author') + schematics_embedded_role),
            'active.auction': (blacklist('author') + schematics_embedded_role),
            'active.qualification': schematics_default_role,
            'active.awarded': schematics_default_role,
            'complete': schematics_default_role,
            'unsuccessful': schematics_default_role,
            'cancelled': schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    author = ModelType(dgfOrganization, required=True)  # who is asking question (contactPoint - person, identification - organization that person represents)
    title = StringType(required=True)  # title of the question
    description = StringType()  # description of the question
    date = IsoDateTimeType(default=get_now)  # autogenerated date of posting
    answer = StringType()  # only tender owner can post answer
    questionOf = StringType(required=True, choices=['tender', 'item', 'lot'], default='tender')
    relatedItem = StringType(min_length=1)

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get('questionOf') in ['item', 'lot']:
            raise ValidationError(u'This field is required.')
        if relatedItem and isinstance(data['__parent__'], Model):
            auction = get_auction(data['__parent__'])
            if data.get('questionOf') == 'lot' and relatedItem not in [i.id for i in auction.lots]:
                raise ValidationError(u"relatedItem should be one of lots")
            if data.get('questionOf') == 'item' and relatedItem not in [i.id for i in auction.items]:
                raise ValidationError(u"relatedItem should be one of items")


default_lot_role = (blacklist('numberOfBids') + schematics_default_role)
embedded_lot_role = (blacklist('numberOfBids') + schematics_embedded_role)


class Lot(Model):
    class Options:
        roles = {
            'create': whitelist('id', 'title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
            'edit': whitelist('title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
            'embedded': embedded_lot_role,
            'view': default_lot_role,
            'default': default_lot_role,
            'auction_view': default_lot_role,
            'auction_patch': whitelist('id', 'auctionUrl'),
            'chronograph': whitelist('id', 'auctionPeriod'),
            'chronograph_view': whitelist('id', 'auctionPeriod', 'numberOfBids', 'status'),
            'Administrator': whitelist('auctionPeriod'),
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    date = IsoDateTimeType()
    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value, required=True)
    auctionPeriod = ModelType(LotAuctionPeriod, default={})
    auctionUrl = URLType()
    status = StringType(choices=['active', 'cancelled', 'unsuccessful', 'complete'], default='active')
    guarantee = ModelType(Guarantee)

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        bids = [
            bid
            for bid in self.__parent__.bids
            if self.id in [i.relatedLot for i in bid.lotValues] and getattr(bid, "status", "active") == "active"
        ]
        return len(bids)

    @serializable(serialized_name="value", type=ModelType(Value))
    def lot_value(self):
        return Value(dict(amount=self.value.amount,
                          currency=self.__parent__.value.currency,
                          valueAddedTaxIncluded=self.__parent__.value.valueAddedTaxIncluded))

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def lot_minimalStep(self):
        return Value(dict(amount=self.minimalStep.amount,
                          currency=self.__parent__.minimalStep.currency,
                          valueAddedTaxIncluded=self.__parent__.minimalStep.valueAddedTaxIncluded))

    def validate_minimalStep(self, data, value):
        if value and value.amount and data.get('value'):
            if data.get('value').amount < value.amount:
                raise ValidationError(u"value should be less than value of lot")


plain_role = (blacklist('_attachments', 'revisions', 'dateModified') + schematics_embedded_role)

create_role = (blacklist('owner', '_attachments', 'revisions', 'date', 'dateModified',
                         'doc_id', 'auctionID', 'bids', 'documents', 'awards',
                         'questions', 'complaints', 'auctionUrl', 'status',
                         'auctionPeriod', 'awardPeriod', 'procurementMethod',
                         'awardCriteria', 'submissionMethod', 'cancellations',
                         'numberOfBidders', 'contracts') + auction_embedded_role)

draft_role = whitelist('status')
edit_role = (blacklist('status', 'procurementMethodType', 'lots', 'owner', '_attachments', 'revisions', 'date', 'dateModified', 'doc_id', 'auctionID', 'bids', 'documents', 'awards', 'questions', 'complaints', 'auctionUrl', 'auctionPeriod', 'awardPeriod', 'procurementMethod', 'awardCriteria', 'submissionMethod', 'mode', 'cancellations', 'numberOfBidders', 'contracts') + auction_embedded_role)
view_role = (blacklist('_attachments', 'revisions') + auction_embedded_role)
listing_role = whitelist('dateModified', 'doc_id')
auction_view_role = whitelist('auctionID', 'dateModified', 'bids', 'auctionPeriod', 'minimalStep', 'auctionUrl', 'features', 'lots', 'items', 'procurementMethodType')
auction_post_role = whitelist('bids')
auction_patch_role = whitelist('auctionUrl', 'bids', 'lots')
enquiries_role = (blacklist('_attachments', 'revisions', 'bids', 'numberOfBids') + auction_embedded_role)
auction_role = (blacklist('_attachments', 'revisions', 'bids', 'numberOfBids') + auction_embedded_role)
#chronograph_role = whitelist('status', 'enquiryPeriod', 'tenderPeriod', 'auctionPeriod', 'awardPeriod', 'lots')
chronograph_role = whitelist('auctionPeriod', 'lots', 'next_check')
chronograph_view_role = whitelist('status', 'enquiryPeriod', 'tenderPeriod', 'auctionPeriod', 'awardPeriod', 'awards', 'lots', 'doc_id', 'submissionMethodDetails', 'mode', 'numberOfBids', 'complaints', 'procurementMethodType')
Administrator_role = whitelist('status', 'mode', 'procuringEntity', 'auctionPeriod', 'lots', 'suspended')


class ProcuringEntity(dgfOrganization):
    """An organization."""
    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'edit_active.enquiries': schematics_default_role + blacklist("kind"),
            'edit_active.tendering': schematics_default_role + blacklist("kind"),
        }

    kind = StringType(choices=['general', 'special', 'defense', 'other'])


auction_roles = {
        'plain': plain_role,
        'create': create_role,
        'edit': edit_role,
        'edit_draft': draft_role,
        'edit_active.enquiries': edit_role,
        'edit_active.tendering': whitelist(),
        'edit_active.auction': whitelist(),
        'edit_active.qualification': whitelist(),
        'edit_active.awarded': whitelist(),
        'edit_complete': whitelist(),
        'edit_unsuccessful': whitelist(),
        'edit_cancelled': whitelist(),
        'view': view_role,
        'listing': listing_role,
        'auction_view': auction_view_role,
        'auction_post': auction_post_role,
        'auction_patch': auction_patch_role,
        'draft': enquiries_role,
        'active.enquiries': enquiries_role,
        'active.tendering': enquiries_role,
        'active.auction': auction_role,
        'active.qualification': view_role,
        'active.awarded': view_role,
        'complete': view_role,
        'unsuccessful': view_role,
        'cancelled': view_role,
        'chronograph': chronograph_role,
        'chronograph_view': chronograph_view_role,
        'Administrator': Administrator_role,
        'default': schematics_default_role,
        'contracting': whitelist('doc_id', 'owner'),
    }

dgf_auction_roles = {
    'create': (auction_embedded_role + blacklist('owner', '_attachments', 'revisions', 'date', 'dateModified', 'doc_id', 'auctionID', 'bids', 'documents', 'awards', 'questions', 'complaints', 'auctionUrl', 'status', 'enquiryPeriod', 'tenderPeriod', 'awardPeriod', 'procurementMethod', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'awardCriteria', 'submissionMethod', 'cancellations', 'numberOfBidders', 'contracts', 'suspended')),
    'edit_active.tendering': (edit_role + blacklist('enquiryPeriod', 'tenderPeriod', 'value', 'auction_value', 'minimalStep', 'auction_minimalStep', 'guarantee', 'auction_guarantee', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'awardCriteriaDetails', 'awardCriteriaDetails_en', 'awardCriteriaDetails_ru', 'procurementMethodRationale', 'procurementMethodRationale_en', 'procurementMethodRationale_ru', 'submissionMethodDetails', 'submissionMethodDetails_en', 'submissionMethodDetails_ru', 'items', 'procuringEntity', 'suspended', 'auctionParameters')),
    'Administrator': (whitelist('suspended', 'awards', 'auctionParameters') + Administrator_role),
    'pending.verification': enquiries_role,
    'invalid': view_role,
    'edit_pending.verification': whitelist(),
    'edit_invalid': whitelist(),
    'convoy': whitelist('status', 'items', 'documents', 'dgfID'),
    'auction_view': (auction_view_role + whitelist('auctionParameters')),
}

view_bid_role = (blacklist('owner_token', 'transfer_token') + schematics_default_role)
Administrator_bid_role = whitelist('tenderers')

swiftsure_auction_roles = deepcopy(dgf_auction_roles)
swiftsure_auction_roles['edit_active.tendering'] = (dgf_auction_roles['edit_active.tendering'] + blacklist('registrationFee', 'bankAccount', 'minNumberOfQualifiedBids'))
swiftsure_auction_roles['auction_view'] = (dgf_auction_roles['auction_view'] + whitelist('minNumberOfQualifiedBids', 'registrationFee', 'bankAccount'))


class Bid(Model):
    class Options:
        roles = {
            'Administrator': Administrator_bid_role,
            'embedded': view_bid_role,
            'view': view_bid_role,
            'create': whitelist('value', 'status', 'tenderers', 'parameters', 'lotValues'),
            'edit': whitelist('value', 'status', 'tenderers', 'parameters', 'lotValues'),
            'auction_view': whitelist('value', 'lotValues', 'id', 'date', 'parameters', 'participationUrl', 'owner'),
            'auction_post': whitelist('value', 'lotValues', 'id', 'date'),
            'auction_patch': whitelist('id', 'lotValues', 'participationUrl'),
            'active.enquiries': whitelist(),
            'active.tendering': whitelist(),
            'active.auction': whitelist(),
            'active.qualification': view_bid_role,
            'active.awarded': view_bid_role,
            'complete': view_bid_role,
            'unsuccessful': view_bid_role,
            'cancelled': view_bid_role,
        }

    def __local_roles__(self):
        return dict([('{}_{}'.format(self.owner, self.owner_token), 'bid_owner')])

    tenderers = ListType(ModelType(dgfOrganization), required=True, min_size=1, max_size=1)
    parameters = ListType(ModelType(Parameter), default=list(), validators=[validate_parameters_uniq])
    lotValues = ListType(ModelType(LotValue), default=list())
    date = IsoDateTimeType(default=get_now)
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=['active', 'draft'], default='active')
    value = ModelType(Value)
    documents = ListType(ModelType(dgfCDB2Document), default=list())
    participationUrl = URLType()
    owner_token = StringType()
    owner = StringType()

    __name__ = ''

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.

        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if k != "value" and data[k] is None]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def __acl__(self):
        return [
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_bid'),
        ]

    def validate_participationUrl(self, data, url):
        if url and isinstance(data['__parent__'], Model) and get_auction(data['__parent__']).lots:
            raise ValidationError(u"url should be posted for each lot of bid")

    def validate_lotValues(self, data, values):
        if isinstance(data['__parent__'], Model):
            tender = data['__parent__']
            if tender.lots and not values:
                raise ValidationError(u'This field is required.')

    def validate_value(self, data, value):
        if isinstance(data['__parent__'], Model):
            auction = data['__parent__']
            if auction.lots:
                if value:
                    raise ValidationError(u"value should be posted for each lot of bid")
            else:
                if not value:
                    raise ValidationError(u'This field is required.')
                if auction.value.amount > value.amount:
                    raise ValidationError(u"value of bid should be greater than value of auction")
                if auction.get('value').currency != value.currency:
                    raise ValidationError(u"currency of bid should be identical to currency of value of auction")
                if auction.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                    raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of auction")

    def validate_parameters(self, data, parameters):
        if isinstance(data['__parent__'], Model):
            tender = data['__parent__']
            if tender.lots:
                lots = [i.relatedLot for i in data['lotValues']]
                items = [i.id for i in tender.items if i.relatedLot in lots]
                codes = dict([
                    (i.code, [x.value for x in i.enum])
                    for i in (tender.features or [])
                    if i.featureOf == 'tenderer' or i.featureOf == 'lot' and i.relatedItem in lots or i.featureOf == 'item' and i.relatedItem in items
                ])
                if set([i['code'] for i in parameters]) != set(codes):
                    raise ValidationError(u"All features parameters is required.")
            elif not parameters and tender.features:
                raise ValidationError(u'This field is required.')
            elif set([i['code'] for i in parameters]) != set([i.code for i in (tender.features or [])]):
                raise ValidationError(u"All features parameters is required.")


flash_bid_roles = {
    'embedded': view_bid_role,
    'view': view_bid_role,
    'auction_view': whitelist('value', 'lotValues', 'id', 'date', 'parameters', 'participationUrl', 'owner'),
    'active.qualification': view_bid_role,
    'active.awarded': view_bid_role,
    'complete': view_bid_role,
    'unsuccessful': view_bid_role,
    'cancelled': view_bid_role,
}


def validate_cav_group(items, *args):
    if items and len(set([i.classification.id[:3] for i in items])) != 1:
        raise ValidationError(u"CAV group of items be identical")


class AuctionAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        auction = self.__parent__
        if auction.lots or auction.status not in ['active.tendering', 'active.auction']:
            return
        if self.startDate and get_now() > calc_auction_end_time(auction.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(auction.numberOfBids, self.startDate)
        else:
            start_after = auction.tenderPeriod.endDate
        return rounding_shouldStartAfter(start_after, auction).isoformat()


class Auction(BaseResourceItem):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    class Options:
        roles = auction_roles

    def __local_roles__(self):
        roles = dict([('{}_{}'.format(self.owner, self.owner_token), 'auction_owner')])
        for i in self.bids:
            roles['{}_{}'.format(i.owner, i.owner_token)] = 'bid_owner'
        return roles

    def __init__(self, *args, **kwargs):
        super(Auction, self).__init__(*args, **kwargs)
        self.doc_type = "Auction"

    title = StringType(required=True)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    date = IsoDateTimeType()
    auctionID = StringType()  # AuctionID should always be the same as the OCID. It is included to make the flattened data structure more convenient.
    value = ModelType(Value, required=True)  # The total estimated value of the procurement.
    procurementMethod = StringType(choices=['open', 'selective', 'limited'],
                                   default='open')  # Specify tendering method as per GPA definitions of Open, Selective, Limited (http://www.wto.org/english/docs_e/legal_e/rev-gpr-94_01_e.htm)
    procurementMethodRationale = StringType()  # Justification of procurement method, especially in the case of Limited tendering.
    procurementMethodRationale_en = StringType()
    procurementMethodRationale_ru = StringType()
    awardCriteria = StringType(choices=['highestCost', 'bestProposal', 'bestValueToGovernment', 'singleBidOnly'],
                               default='highestCost')  # Specify the selection criteria, by lowest cost,
    awardCriteriaDetails = StringType()  # Any detailed or further information on the selection criteria.
    awardCriteriaDetails_en = StringType()
    awardCriteriaDetails_ru = StringType()
    submissionMethod = StringType(choices=['electronicAuction', 'electronicSubmission', 'written', 'inPerson'],
                                  default='electronicAuction')  # Specify the method by which bids must be submitted, in person, written, or electronic auction
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    enquiryPeriod = ModelType(AuctionPeriodEndRequired,
                              required=True)  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(AuctionPeriodEndRequired,
                             required=True)  # The period when the auction is open for submissions. The end date is the closing date for auction submissions.
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of auction process.
    eligibilityCriteria = StringType()  # A description of any eligibility criteria for potential suppliers.
    eligibilityCriteria_en = StringType()
    eligibilityCriteria_ru = StringType()
    awardPeriod = ModelType(Period)  # The date or period on which an award is anticipated to be made.
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the auction
    # numberOfBids = IntType()  # The number of bids or submissions to the auction. In the case of an auction, the number of bids may differ from the numberOfBidders.
    bids = ListType(ModelType(Bid),
                    default=list())  # A list of all the companies who entered submissions for the auction.
    procuringEntity = ModelType(ProcuringEntity,
                                required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    auctionPeriod = ModelType(AuctionAuctionPeriod, default={})

    minimalStep = ModelType(Value, required=True)
    status = StringType(
        choices=['draft', 'active.enquiries', 'active.tendering', 'active.auction', 'active.qualification',
                 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.enquiries')
    questions = ListType(ModelType(Question), default=list())
    auctionUrl = URLType()
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])
    guarantee = ModelType(Guarantee)
    if SANDBOX_MODE:
        procurementMethodDetails = StringType()

    procurementMethodType = StringType()

    create_accreditation = 1
    edit_accreditation = 2
    procuring_entity_kinds = ['general', 'special', 'defense', 'other', '']
    block_complaint_status = ['claim', 'answered', 'pending']

    __name__ = ''

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        elif request.authenticated_role == 'chronograph':
            role = 'chronograph'
        elif request.authenticated_role == 'auction':
            role = 'auction_{}'.format(request.method.lower())
        elif request.authenticated_role == 'contracting':
            role = 'contracting'
        else:
            role = 'edit_{}'.format(request.context.status)
        return role

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            for i in self.bids
        ]
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_auction_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
        ])
        return acl

    def __repr__(self):
        return '<%s:%r@%r>' % (type(self).__name__, self.id, self.rev)

    def initialize(self):
        if not self.enquiryPeriod.startDate:
            self.enquiryPeriod.startDate = get_now()
        if not self.tenderPeriod.startDate:
            self.tenderPeriod.startDate = self.enquiryPeriod.endDate
        now = get_now()
        self.date = now
        if self.lots:
            for lot in self.lots:
                lot.date = now

    @serializable(serialize_when_none=False)
    def next_check(self):
        '''
            Serializable date field for openprocurement.chronograph.
            Chronograph will check Auction for patching status
            to next by workflow
        '''
        now = get_now()
        checks = []
        if self.status == 'active.enquiries' and self.tenderPeriod.startDate:
            checks.append(self.tenderPeriod.startDate.astimezone(TZ))
        elif self.status == 'active.enquiries' and self.enquiryPeriod.endDate:
            checks.append(self.enquiryPeriod.endDate.astimezone(TZ))
        elif self.status == 'active.tendering' and self.tenderPeriod.endDate:
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif not self.lots and self.status == 'active.auction' and self.auctionPeriod and self.auctionPeriod.startDate and not self.auctionPeriod.endDate:
            if now < self.auctionPeriod.startDate:
                checks.append(self.auctionPeriod.startDate.astimezone(TZ))
            elif now < calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ):
                checks.append(calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ))
        elif self.lots and self.status == 'active.auction':
            for lot in self.lots:
                if lot.status != 'active' or not lot.auctionPeriod or not lot.auctionPeriod.startDate or lot.auctionPeriod.endDate:
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(TZ))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ))
        # Use next_check part from awarding 1.0
        request = get_request_from_root(self)
        if request is not None:
            awarding_check = request.registry.getAdapter(self, IAwardingNextCheck).add_awarding_checks(self)
            if awarding_check is not None:
                checks.append(awarding_check)
        if self.status.startswith('active'):
            from openprocurement.auctions.core.utils import calculate_business_date
            for complaint in self.complaints:
                if complaint.status == 'claim' and complaint.dateSubmitted:
                    checks.append(
                        calculate_business_date(complaint.dateSubmitted, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
                elif complaint.status == 'answered' and complaint.dateAnswered:
                    checks.append(
                        calculate_business_date(complaint.dateAnswered, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
            for award in self.awards:
                for complaint in award.complaints:
                    if complaint.status == 'claim' and complaint.dateSubmitted:
                        checks.append(
                            calculate_business_date(complaint.dateSubmitted, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
                    elif complaint.status == 'answered' and complaint.dateAnswered:
                        checks.append(
                            calculate_business_date(complaint.dateAnswered, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
        return min(checks).isoformat() if checks else None

    def validate_procurementMethodDetails(self, *args, **kw):
        if self.mode and self.mode == 'test' and self.procurementMethodDetails and self.procurementMethodDetails != '':
            raise ValidationError(u"procurementMethodDetails should be used with mode test")

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len(self.bids)

    @serializable(serialized_name='id')
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    @serializable(serialized_name="value", type=ModelType(Value))
    def auction_value(self):
        return Value(dict(amount=sum([i.value.amount for i in self.lots]),
                          currency=self.value.currency,
                          valueAddedTaxIncluded=self.value.valueAddedTaxIncluded)) if self.lots else self.value

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def auction_guarantee(self):
        if self.lots:
            lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
            if not lots_amount:
                return self.guarantee
            guarantee = {'amount': sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
            guarantee['currency'] = lots_currency[0] if lots_currency else None
            if self.guarantee:
                guarantee['currency'] = self.guarantee.currency
            return Guarantee(guarantee)
        else:
            return self.guarantee

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def auction_minimalStep(self):
        return Value(dict(amount=min([i.minimalStep.amount for i in self.lots]),
                          currency=self.minimalStep.currency,
                          valueAddedTaxIncluded=self.minimalStep.valueAddedTaxIncluded)) if self.lots else self.minimalStep

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if
                    data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def validate_features(self, data, features):
        if features and data['lots'] and any([
            round(vnmax([
                i
                for i in features
                if i.featureOf == 'tenderer' or i.featureOf == 'lot' and i.relatedItem == lot[
                    'id'] or i.featureOf == 'item' and i.relatedItem in [j.id for j in data['items'] if
                                                                         j.relatedLot == lot['id']]
            ]), 15) > 0.3
            for lot in data['lots']
        ]):
            raise ValidationError(u"Sum of max value of all features for lot should be less then or equal to 30%")
        elif features and not data['lots'] and round(vnmax(features), 15) > 0.3:
            raise ValidationError(u"Sum of max value of all features should be less then or equal to 30%")

    def validate_auctionUrl(self, data, url):
        if url and data['lots']:
            raise ValidationError(u"url should be posted for each lot")

    def validate_minimalStep(self, data, value):
        if value and value.amount and data.get('value'):
            if data.get('value').amount < value.amount:
                raise ValidationError(u"value should be less than value of auction")
            if data.get('value').currency != value.currency:
                raise ValidationError(u"currency should be identical to currency of value of auction")
            if data.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(
                    u"valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of auction")

    def validate_awardPeriod(self, data, period):
        if period and period.startDate and data.get('auctionPeriod') and data.get(
                'auctionPeriod').endDate and period.startDate < data.get('auctionPeriod').endDate:
            raise ValidationError(u"period should begin after auctionPeriod")
        if period and period.startDate and data.get('tenderPeriod') and data.get(
                'tenderPeriod').endDate and period.startDate < data.get('tenderPeriod').endDate:
            raise ValidationError(u"period should begin after tenderPeriod")

    def validate_lots(self, data, value):
        if len(set([lot.guarantee.currency for lot in value if lot.guarantee])) > 1:
            raise ValidationError(u"lot guarantee currency should be identical to auction guarantee currency")


STAND_STILL_TIME = timedelta(days=2)
BIDDER_TIME = timedelta(minutes=3 * 3)
SERVICE_TIME = timedelta(minutes=5 + 3 + 3)
AUCTION_STAND_STILL_TIME = timedelta(minutes=15)


def calc_auction_end_time(bids, start):
    return start + bids * BIDDER_TIME + SERVICE_TIME + AUCTION_STAND_STILL_TIME


def validate_not_available(items, *args):
    if items:
        raise ValidationError(u"Option not available in this procurementMethodType")
