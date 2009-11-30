import os

from django.conf import settings

here = os.path.dirname(__file__)

MOLLIE_API_URL = 'http://www.mollie.nl/xml/ideal'

MOLLIE_TEST = getattr(settings, 'MOLLIE_TEST', False)

MOLLIE_BANKS_FILE = getattr(settings, 'MOLLIE_BANKS_FILE', None)

if not MOLLIE_BANKS_FILE:
    if MOLLIE_TEST:
        MOLLIE_BANKS_FILE = os.path.join(here, 'banklist-testmode.xml')
    else:
        MOLLIE_BANKS_FILE = os.path.join(here, 'banklist.xml')

MOLLIE_MIN_AMOUNT = getattr(settings, 'MOLLIE_MIN_AMOUNT', 118)

# A range of logos and buttons can be found at http://www.mollie.nl/support/klanten/logo-badges/
MOLLIE_IDEAL_BUTTON = getattr(settings, 'MOLLIE_IDEAL_BUTTON', 'http://www.mollie.nl/images/badge-ideal-big.png')

MOLLIE_BTW = getattr(settings, 'MOLLIE_BTW', 19) # integer value
MOLLIE_TRANSACTION_FEE = getattr(settings, 'MOLLIE_TRANSACTION_FEE', '.99') # string value

MOLLIE_TIMEOUT = getattr(settings, 'MOLLIE_TIMEOUT', 10)

