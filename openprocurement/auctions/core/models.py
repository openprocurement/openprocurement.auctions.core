from datetime import (
    datetime,
    timedelta,
    time
)
from urlparse import (
    urlparse,
    parse_qs
)
from string import hexdigits
from zope.interface import Interface
from schematics.types import (
    StringType,
    IntType,
    URLType
)
from schematics.transforms import (
    blacklist,
    whitelist
)
from schematics.exceptions import ValidationError
from schematics.types.serializable import serializable

from openprocurement.api.models import (
    Complaint as BaseComplaint,
    Model,
    Document as BaseDocument,
    ListType,
    Item as BaseItem,
    Identifier as BaseIdentifier,
    ModelType,
    Classification,
    schematics_default_role,
    validate_dkpp,
    Organization,
    Address,
    Location,
    schematics_embedded_role,
    schematics_default_role,
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)
from openprocurement.auctions.core.constants import (
    DOCUMENT_TYPE_OFFLINE,
    DOCUMENT_TYPE_URL_ONLY,
    CAV_CODES_DGF,
    CAV_CODES_FLASH,
    ORA_CODES
)


view_complaint_role = (blacklist('owner_token', 'owner') + schematics_default_role)


class IAuction(Interface):
    """ Base auction marker interface """


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


class Item(BaseItem):
    """A good, service, or work to be contracted."""
    classification = ModelType(flashCAVClassification, required=True)
    additionalClassifications = ListType(ModelType(Classification), default=list(), validators=[validate_dkpp]) # required=True, min_size=1,

    def validate_relatedLot(self, data, relatedLot):
        if relatedLot and isinstance(data['__parent__'], Model) and relatedLot not in [i.id for i in get_auction(data['__parent__']).lots]:
            raise ValidationError(u"relatedLot should be one of lots")


flashItem = Item


class Item(Item):
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


dgfItem = Item


class Document(BaseDocument):

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

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get('documentOf') in ['item', 'lot']:
            raise ValidationError(u'This field is required.')
        if relatedItem and isinstance(data['__parent__'], Model):
            auction = get_auction(data['__parent__'])
            if data.get('documentOf') == 'lot' and relatedItem not in [i.id for i in auction.lots]:
                raise ValidationError(u"relatedItem should be one of lots")
            if data.get('documentOf') == 'item' and relatedItem not in [i.id for i in auction.items]:
                raise ValidationError(u"relatedItem should be one of items")


flashDocument = Document


class Document(Document):
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
        if not request.registry.docservice_url:
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


dgfDocument = Document


class Complaint(BaseComplaint):
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
    documents = ListType(ModelType(Document), default=list())

    def serialize(self, role=None, context=None):
        if role == 'view' and self.type == 'claim' and get_auction(self).status in ['active.enquiries', 'active.tendering']:
            role = 'view_claim'
        return super(BaseComplaint, self).serialize(role=role, context=context)

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

    def validate_relatedLot(self, data, relatedLot):
        if relatedLot and isinstance(data['__parent__'], Model) and relatedLot not in [i.id for i in get_auction(data['__parent__']).lots]:
            raise ValidationError(u"relatedLot should be one of lots")


flashComplaint = Complaint


class Identifier(BaseIdentifier):
    scheme = StringType(required=True, choices=ORA_CODES)


class Organization(Organization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))


dgfOrganization = Organization


class Complaint(Complaint):
    author = ModelType(Organization, required=True)
    documents = ListType(ModelType(dgfDocument), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])


dgfComplaint = Complaint


plain_role = (blacklist('_attachments', 'revisions', 'dateModified') + schematics_embedded_role)
create_role = (blacklist('owner_token', 'owner', '_attachments', 'revisions', 'date', 'dateModified', 'doc_id', 'auctionID', 'bids', 'documents', 'awards', 'questions', 'complaints', 'auctionUrl', 'status', 'auctionPeriod', 'awardPeriod', 'procurementMethod', 'awardCriteria', 'submissionMethod', 'cancellations', 'numberOfBidders', 'contracts') + schematics_embedded_role)
draft_role = whitelist('status')
edit_role = (blacklist('status', 'procurementMethodType', 'lots', 'owner_token', 'owner', '_attachments', 'revisions', 'date', 'dateModified', 'doc_id', 'auctionID', 'bids', 'documents', 'awards', 'questions', 'complaints', 'auctionUrl', 'auctionPeriod', 'awardPeriod', 'procurementMethod', 'awardCriteria', 'submissionMethod', 'mode', 'cancellations', 'numberOfBidders', 'contracts') + schematics_embedded_role)
view_role = (blacklist('owner_token', '_attachments', 'revisions') + schematics_embedded_role)
listing_role = whitelist('dateModified', 'doc_id')
auction_view_role = whitelist('auctionID', 'dateModified', 'bids', 'auctionPeriod', 'minimalStep', 'auctionUrl', 'features', 'lots', 'items', 'procurementMethodType')
auction_post_role = whitelist('bids')
auction_patch_role = whitelist('auctionUrl', 'bids', 'lots')
enquiries_role = (blacklist('owner_token', '_attachments', 'revisions', 'bids', 'numberOfBids') + schematics_embedded_role)
auction_role = (blacklist('owner_token', '_attachments', 'revisions', 'bids', 'numberOfBids') + schematics_embedded_role)
#chronograph_role = whitelist('status', 'enquiryPeriod', 'tenderPeriod', 'auctionPeriod', 'awardPeriod', 'lots')
chronograph_role = whitelist('auctionPeriod', 'lots', 'next_check')
chronograph_view_role = whitelist('status', 'enquiryPeriod', 'tenderPeriod', 'auctionPeriod', 'awardPeriod', 'awards', 'lots', 'doc_id', 'submissionMethodDetails', 'mode', 'numberOfBids', 'complaints', 'procurementMethodType')
Administrator_role = whitelist('status', 'mode', 'procuringEntity','auctionPeriod', 'lots')

flash_auction_roles = {
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


view_bid_role = (blacklist('owner_token') + schematics_default_role)
Administrator_bid_role = whitelist('tenderers')

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


STAND_STILL_TIME = timedelta(days=2)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)
BIDDER_TIME = timedelta(minutes=3 * 3)
SERVICE_TIME = timedelta(minutes=5 + 3 + 3)
AUCTION_STAND_STILL_TIME = timedelta(minutes=15)


def calc_auction_end_time(bids, start):
    return start + bids * BIDDER_TIME + SERVICE_TIME + AUCTION_STAND_STILL_TIME
