#-*- coding: utf-8 -*-

from decimal import Decimal

from mollie.ideal.helpers import *
from mollie.ideal.settings import MOLLIE_BTW, MOLLIE_TRANSACTION_FEE

def query_mollie(request_dict, mode):
    valid_modes = ('check', 'fetch')
    if mode not in valid_modes:
        raise ValueError("Invalid mode. Valid modes are '%s' and '%s'." % valid_modes)
    request_dict['a'] = mode
    url = build_mollie_url(request_dict)
    parsed_xml = get_mollie_xml(url)
    order = parsed_xml.find('order')
    response_dict = dict()
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
    btw = Decimal(btw)
    fee = Decimal(fee)
    fee += ((btw / 100) * fee)
    return fee.quantize(Decimal(10) ** -2)

get_mollie_banklist = get_mollie_bank_choices
