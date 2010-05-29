# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mollie.ideal.helpers import *

class MollieIdealPayment(models.Model):

    transaction_id = models.CharField(_('transaction ID'), max_length=255)
    amount = models.DecimalField(_('amount'), max_digits=64, decimal_places=2)
    bank = models.CharField(_('bank'), max_length=4,
                            choices=get_mollie_bank_choices(),
                            default='')
    description = models.CharField(_('description'), max_length=29)
    timestamp = models.DateTimeField(_('date'), auto_now_add=True)
    consumer_account = models.CharField(_('consumer account'), max_length=255, blank=True)
    consumer_name = models.CharField(_('consumer name'), max_length=255, blank=True)
    consumer_city = models.CharField(_('consumer city'), max_length=255, blank=True)

    class Meta:
        abstract = True
        verbose_name = _('Mollie/iDEAL payment')

    def get_order_url_and_save(self):
        """Sets up a payment, saves the transaction ID and returns an order URL"""
        request_dict = dict(
            a = 'fetch',
            amount = int(self.amount * 100),
            bank_id = self.bank,
            description = self.description,
            partnerid = settings.MOLLIE_PARTNER_ID,
            reporturl = settings.MOLLIE_REPORT_URL,
            returnurl = settings.MOLLIE_RETURN_URL
        )
        url = build_mollie_url(request_dict)
        parsed_xml = get_mollie_xml(url)
        order = parsed_xml.find('order')
        order_url = order.findtext('URL') 
        self.transaction_id = order.findtext('transaction_id')
        self.save()
        return order_url
    
    def is_paid(self):
            """Checks whether a payment has been made successfully"""
            request_dict = dict(
                a = 'check',
                partnerid = settings.MOLLIE_PARTNER_ID,
                transaction_id = self.transaction_id
            )
            url = build_mollie_url(request_dict)
            parsed_xml = get_mollie_xml(url)
            order = parsed_xml.find('order')
            consumer = order.find('consumer')
            if consumer:
                self.consumer_account = consumer.findtext('consumerAccount')
                self.consumer_city = consumer.findtext('consumerCity')
                self.consumer_name = consumer.findtext('consumerName')
            if order.findtext('payed') == 'true':
                return True
            return False

    @property
    def bank_name(self):
        return self.get_bank_display()

    def __unicode__(self):
        return u'Mollie/iDEAL Payment ID: %d' % self.id
