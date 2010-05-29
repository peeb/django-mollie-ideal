#-*- coding: utf-8 -*-

import socket
import urllib, urllib2, urlparse

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree

from django.utils.translation import ugettext_lazy as _

from mollie.ideal.settings import MOLLIE_API_URL, MOLLIE_TEST, MOLLIE_TIMEOUT

socket.setdefaulttimeout(MOLLIE_TIMEOUT)

def build_mollie_url(request_dict, base_url=MOLLIE_API_URL, testmode=MOLLIE_TEST):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(base_url)
    if testmode:
        request_dict['testmode'] = 'true'
    query = urllib.urlencode(request_dict)
    url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
    return url

def get_mollie_xml(url):
    try:
        xml = urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError), error:
        raise error
    parsed_xml = etree.parse(xml)
    return parsed_xml

def get_mollie_bank_choices():
    request_dict = dict(a = 'banklist')
    url = build_mollie_url(request_dict)
    parsed_xml = get_mollie_xml(url)
    banks = parsed_xml.getiterator('bank')
    choices = [(bank.findtext('bank_id'), bank.findtext('bank_name')) for bank in banks]
    choices.insert(0, ('', _('Please select your bank')))
    return tuple(choices)
