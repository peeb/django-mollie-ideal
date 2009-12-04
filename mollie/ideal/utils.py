import decimal
import socket
import urllib
import urllib2
import urlparse

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree

from conf import MOLLIE_TEST, MOLLIE_API_URL, MOLLIE_TIMEOUT, MOLLIE_BTW, MOLLIE_TRANSACTION_FEE

socket.setdefaulttimeout(MOLLIE_TIMEOUT)

def build_mollie_url(input_dict, base_url=MOLLIE_API_URL, testmode=MOLLIE_TEST):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(base_url)
    if testmode:
        input_dict['testmode'] = 'true'
    query = urllib.urlencode(input_dict)
    url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
    return url

def parse_mollie_response(url):
    data = urllib2.urlopen(url)
    mollie_response = etree.parse(data)
    return mollie_response

def get_mollie_banklist():
    url = build_mollie_url(dict(a='banklist'))
    try:
        mollie_response = parse_mollie_response(url)
    except:
        raise
    banks = mollie_response.getiterator('bank')
    choices = ((bank.findtext('bank_id'), bank.findtext('bank_name')) for bank in banks)
    return tuple(choices)

def query_mollie(request_dict, mode=None, valid_modes=('check', 'fetch')):
    assert mode in valid_modes, 'Invalid mode "%s". Valid modes are "%s" and "%s".' % (mode, valid_modes)
    request_dict['a'] = mode
    url = build_mollie_url(request_dict)
    mollie_response = parse_mollie_response(url)
    order = mollie_response.find('order')
    response_dict = {}
    response_dict['amount'] = decimal.Decimal(order.findtext('amount')) / 100
    response_dict['transaction_id'] = order.findtext('transaction_id')
    if mode == 'fetch':
        response_dict['order_url'] = order.findtext('URL')
    elif mode == 'check':
        response_dict['paid'] = order.findtext('payed') # sic!
        consumer = order.find('consumer')
        response_dict['consumerAcount'] = consumer.findtext('consumerAccount')
        response_dict['consumerCity'] = consumer.findtext('consumerCity')
        response_dict['consumerName'] = consumer.findtext('consumerName')
    return response_dict

def get_mollie_fee(btw=MOLLIE_BTW, fee=MOLLIE_TRANSACTION_FEE):
    assert isinstance(btw, int), 'MOLLIE_BTW must be an integer value'
    assert isinstance(fee, str), 'MOLLIE_TRANSACTION_FEE must be a string value'
    btw = decimal.Decimal(btw)
    fee = decimal.Decimal(fee)
    fee += ((btw / 100) * fee)
    return fee.quantize(decimal.Decimal(10) ** -2)
