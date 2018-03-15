from datetime import timedelta, datetime

from openprocurement.api.models import ORA_CODES, TZ
from openprocurement.auctions.core.utils import read_json

DOCUMENT_TYPE_OFFLINE = ['x_dgfAssetFamiliarization']
DOCUMENT_TYPE_URL_ONLY = ['virtualDataRoom', 'x_dgfPublicAssetCertificate', 'x_dgfPlatformLegalDetails']

ORA_CODES = ORA_CODES[:]
ORA_CODES[0:0] = ["UA-IPN", "UA-FIN"]

CAV_CODES_FLASH = read_json('cav_flash.json')
CAV_CODES_DGF = read_json('cav_dgf.json')

CAVPS_CODES_DGF_CDB2 = read_json('cav_ps_dgf_cdb2.json')
CPVS_CODES_DGF_CDB2 = read_json('cpvs_dgf_cdb2.json')

# CDB2 dgf
CPV_NON_SPECIFIC_LOCATION_UNITS_DGF_CDB2 = ('45', '48', '50', '51', '55', '60', '63', '64',
                                   '65', '66', '71', '72', '73', '75', '76', '77',
                                   '79', '80', '85', '90', '92', '98')
CAV_NON_SPECIFIC_LOCATION_UNITS_DGF_CDB2 = ('07', '08')
DGF_CDB2_ADDRESS_REQUIRED_FROM = datetime(2018, 2, 9, tzinfo=TZ)
DGF_CDB2_CLASSIFICATION_PRECISELY_FROM = datetime(2017, 7, 19, tzinfo=TZ)

# Periods of prolongations, that can be applied on Contract
PROLONGATION_SHORT_PERIOD = timedelta(days=42)
PROLONGATION_LONG_PERIOD = timedelta(days=132)

# Period, that limits time period between `datePublished` of
# Prolongation and it's actual creation time `dateCreated`
PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD = timedelta(days=20)
