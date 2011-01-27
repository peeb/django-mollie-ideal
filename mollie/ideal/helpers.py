#-*- coding: utf-8 -*-

from __future__ import with_statement

import os
import socket
import urllib
import urllib2
import urlparse

from django.utils.translation import ugettext_lazy as _

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree

from mollie.ideal.settings import MOLLIE_API_URL, MOLLIE_BANKLIST_DIR, MOLLIE_TEST, MOLLIE_TIMEOUT


__all__ = ['get_and_parse_mollie_xml', 'get_mollie_bank_choices']


socket.setdefaulttimeout(MOLLIE_TIMEOUT)


def get_and_parse_mollie_xml(request_dict,
                             base_url=MOLLIE_API_URL,
                             testmode=MOLLIE_TEST):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(base_url)
    if testmode:
        request_dict['testmode'] = 'true'
    query = urllib.urlencode(request_dict)
    url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
    try:
        xml = urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError), error:
        raise error
    parsed_xml = etree.parse(xml)
    return parsed_xml


def get_mollie_bank_choices(testmode=MOLLIE_TEST,
                            show_all_banks=False):
    fallback_file = os.path.join(os.path.dirname(__file__), 'mollie_banklist.xml')
    file = os.path.join(MOLLIE_BANKLIST_DIR, 'mollie_banklist.xml')
    test_bank = ('9999', 'TBM Bank (Test Bank)')
    empty_choice = ('', _('Please select your bank'))
    if not os.path.exists(file):
        file = fallback_file
    with open(file) as xml:
        try:
            parsed_xml = etree.parse(xml)
            banks = parsed_xml.getiterator('bank')
            choices = [(bank.findtext('bank_id'), bank.findtext('bank_name')) for bank in banks]
            if testmode or show_all_banks:
                choices.append(test_bank)
            choices.insert(0, empty_choice)
            return tuple(choices)
        except etree.XMLSyntaxError, error:
            raise error
