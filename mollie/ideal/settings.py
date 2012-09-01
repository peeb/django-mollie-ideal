#-*- coding: utf-8 -*-

from django.conf import settings

MOLLIE_API_URL = 'http://www.mollie.nl/xml/ideal'
MOLLIE_BANKLIST_DIR = getattr(settings, 'MOLLIE_BANKLIST_DIR', '/var/tmp')
MOLLIE_BTW = getattr(settings, 'MOLLIE_BTW', 19)
# A range of logos and buttons can be found at http://www.mollie.nl/support/klanten/logo-badges/
MOLLIE_IDEAL_BUTTON = getattr(settings, 'MOLLIE_IDEAL_BUTTON', 'http://www.mollie.nl/images/badge-ideal-big.png')
MOLLIE_MIN_AMOUNT = getattr(settings, 'MOLLIE_MIN_AMOUNT', '1.18')
MOLLIE_TEST = getattr(settings, 'MOLLIE_TEST', False)
MOLLIE_TRANSACTION_FEE = getattr(settings, 'MOLLIE_TRANSACTION_FEE', '.99')
MOLLIE_TIMEOUT = getattr(settings, 'MOLLIE_TIMEOUT', 10)
MOLLIE_PROFILE_KEY = getattr(settings, 'MOLLIE_PROFILE_KEY', None)