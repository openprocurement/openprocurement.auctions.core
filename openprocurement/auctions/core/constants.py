# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from openprocurement.api.constants import TZ
from openprocurement.auctions.core.utils import read_json

ENGLISH_AUCTION_PROCUREMENT_METHOD_TYPES = ["belowThreshold", "dgfOtherAssets", "dgfFinancialAssets"]
DUTCH_AUCTION_PROCUREMENT_METHOD_TYPES = ["dgfInsider"]

DOCUMENT_TYPE_OFFLINE = ['x_dgfAssetFamiliarization']
DOCUMENT_TYPE_URL_ONLY = ['virtualDataRoom', 'x_dgfPublicAssetCertificate', 'x_dgfPlatformLegalDetails']

ORA_CODES = [i['code'] for i in read_json('OrganisationRegistrationAgency.json')['data']]
ORA_CODES[0:0] = ["UA-IPN", "UA-FIN"]

CAV_CODES_FLASH = read_json('cav_flash.json')
CAV_CODES_DGF = read_json('cav_dgf.json')

CAVPS_CODES_DGF_CDB2 = read_json('cav_ps_dgf_cdb2.json')
CPVS_CODES_DGF_CDB2 = read_json('cpvs_dgf_cdb2.json')

# CDB2 dgf
CPV_NON_SPECIFIC_LOCATION_UNITS_DGF_CDB2 = (
    '45', '48', '50', '51', '55', '60', '63', '64',
    '65', '66', '71', '72', '73', '75', '76', '77',
    '79', '80', '85', '90', '92', '98'
)
CAV_NON_SPECIFIC_LOCATION_UNITS_DGF_CDB2 = ('07', '08')
DGF_CDB2_ADDRESS_REQUIRED_FROM = datetime(2020, 2, 9, tzinfo=TZ)
DGF_CDB2_CLASSIFICATION_PRECISELY_FROM = datetime(2017, 7, 19, tzinfo=TZ)

# Periods of prolongations, that can be applied on Contract
PROLONGATION_SHORT_PERIOD = timedelta(days=42)
PROLONGATION_LONG_PERIOD = timedelta(days=132)

# Period, that limits time period between `datePublished` of
# Prolongation and it's actual creation time `dateCreated`
PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD = timedelta(days=20)

DGF_PLATFORM_LEGAL_DETAILS = {
    'url': 'http://torgi.fg.gov.ua/prozorrosale',
    'title': u'Місце та форма прийому заяв на участь в аукціоні та банківські реквізити для зарахування гарантійних внесків',
    'documentType': 'x_dgfPlatformLegalDetails',
}

DGF_ELIGIBILITY_CRITERIA = {
    "ua": u"""Учасником електронного аукціону, предметом продажу на яких є права вимоги за кредитними договорами та договорами забезпечення, не може бути користувач, який є позичальником (боржником відносно банку) та/або поручителем (майновим поручителем) за такими кредитними договорами та/або договорами забезпечення.""",
    "ru": u"Участником электронного аукциона, предметом продажи на которых являются права требования по кредитным договорам и договорам обеспечения, не может быть пользователь, являющийся заёмщиком (должником относительно банка) и\или поручителем (имущественным поручителем) по таким кредитным договорам и/или договорам обеспечения.",
    "en": u"The user, who is the borrower (the debtor of the bank) and/or guarantor (property guarantor) for loan agreements and/or collateral agreements, cannot be the bidder of the electronic auction, where the items for sale are the claim rights on such loan agreements and collateral agreements."
}

DGF_PLATFORM_LEGAL_DETAILS_FROM = datetime(2016, 12, 23, tzinfo=TZ)

ADDITIONAL_CLASSIFICATIONS_SCHEMES = [u'ДКПП', u'NONE', u'ДК003', u'ДК015', u'ДК018']

# Declares what roles can interact with document in different statuses
STATUS4ROLE = {
    'complaint_owner': ['draft', 'answered'],
    'reviewers': ['pending'],
    'tender_owner': ['claim'],
}

