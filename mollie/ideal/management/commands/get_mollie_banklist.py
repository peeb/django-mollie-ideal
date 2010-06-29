#-*- coding: utf-8 -*-

import os, urllib

from django.core.management.base import NoArgsCommand, CommandError

from mollie.ideal.settings import MOLLIE_API_URL

class Command(NoArgsCommand):
    help = 'Fetches the latest list of supported banks from Mollie.nl'
    requires_model_validation = False

    def handle_noargs(self, **options):
        here = os.path.realpath('.')
        url = '%s?a=banklist' % MOLLIE_API_URL
        file = os.path.join(here, 'mollie_banklist.xml')
        try:
            urllib.urlretrieve(url, file)
            print 'File %s saved to %s.' % (os.path.basename(file), here)
        except:
            raise CommandError('Something went wrong!')
