from openprocurement.api.models import ORA_CODES
from openprocurement.auctions.core.utils import read_json

DOCUMENT_TYPE_OFFLINE = ['x_dgfAssetFamiliarization']
DOCUMENT_TYPE_URL_ONLY = ['virtualDataRoom', 'x_dgfPublicAssetCertificate', 'x_dgfPlatformLegalDetails']

ORA_CODES = ORA_CODES[:]
ORA_CODES[0:0] = ["UA-IPN", "UA-FIN"]

CAV_CODES_FLASH = read_json('cav_flash.json')
CAV_CODES_DGF = read_json('cav_dgf.json')
