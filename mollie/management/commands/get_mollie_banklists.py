#-*- coding: utf-8 -*-

import os, urllib

from django.core.management.base import NoArgsCommand, CommandError

from mollie.ideal.settings import MOLLIE_API_URL, MOLLIE_BANKLIST_DIR

class Command(NoArgsCommand):
    help = 'Fetches the latest list of supported banks from Mollie.nl'

    def handle_noargs(self, **options):
        banklist = MOLLIE_API_URL + '?a=banklist'
        banklist_testmode = banklist + '&testmode=true'
        file = os.path.join(MOLLIE_BANKLIST_DIR, 'mollie_banklist.xml')
        file_testmode = os.path.join(MOLLIE_BANKLIST_DIR, 'mollie_banklist_testmode.xml')
        try:
            urllib.urlretrieve(banklist, file)
            urllib.urlretrieve(banklist_testmode, file_testmode)
            print 'Files saved to %s' % MOLLIE_BANKLIST_DIR
        except:
            raise CommandError('Something went wrong!')
