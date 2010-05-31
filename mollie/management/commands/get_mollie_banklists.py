#-*- coding: utf-8 -*-

import os, urllib

from django.core.management.base import NoArgsCommand, CommandError

from mollie.ideal.settings import MOLLIE_API_URL

class Command(NoArgsCommand):
    help = 'Fetches the latest list of supported banks from Mollie.nl'

    def handle_noargs(self, **options):
        here = os.path.abspath('.')
        url1 = MOLLIE_API_URL + '?a=banklist'
        url2 = url1 + '&testmode=true'
        file1 = os.path.join(here, 'mollie_banklist.xml')
        file2 = os.path.join(here, 'mollie_banklist_testmode.xml')
        try:
            urllib.urlretrieve(url1, file1)
            urllib.urlretrieve(url2, file2)
            print 'Files saved to %s' % here
        except:
            raise CommandError('Something went wrong!')
