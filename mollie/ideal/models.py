# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mollie.ideal.helpers import get_and_parse_mollie_xml


__all__ = ['MollieBankChoices', 'MollieIdealPayment']


class MollieBankChoices(object):
    pass


class MollieIdealPayment(models.Model):

    transaction_id = models.CharField(_('Transaction ID'),
                                      max_length=255)
    amount = models.DecimalField(_('Amount'),
                                 max_digits=64,
                                 decimal_places=2)
    bank_id = models.CharField(_('Bank ID'),
                               max_length=4,
                               choices=get_mollie_bank_choices(show_all_banks=True),
                               default = '')
    description = models.CharField(_('Description'),
                                   max_length=29)
    timestamp = models.DateTimeField(_('Timestamp'),
                                     auto_now_add=True)
    consumer_account = models.CharField(_('Consumer account'),
                                        max_length=255,
                                        blank=True)
    consumer_name = models.CharField(_('Consumer name'),
                                     max_length=255,
                                     blank=True)
    consumer_city = models.CharField(_('Consumer city'),
                                     max_length=255,
                                     blank=True)

    class Meta:
        abstract = True
        verbose_name = _('Mollie/iDEAL payment')

    def get_order_url(self):
        'Sets up a payment with Mollie.nl and returns an order URL.'
        request_dict = dict(
            a='fetch',
            amount=int(self.amount * 100),
            bank_id=self.bank_id,
            description=self.description,
            partnerid=settings.MOLLIE_PARTNER_ID,
            reporturl=settings.MOLLIE_REPORT_URL,
            returnurl=settings.MOLLIE_RETURN_URL
        )
        parsed_xml = _get_mollie_xml(request_dict)
        order = parsed_xml.find('order')
        order_url = order.findtext('URL')
        self.transaction_id = order.findtext('transaction_id')
        self.save()
        return order_url

    fetch = get_order_url
        
    def is_paid(self):
        'Checks whether a payment has been made successfully.'
        request_dict = dict(
            a='check',
            partnerid=settings.MOLLIE_PARTNER_ID,
            transaction_id=self.transaction_id
        )
        parsed_xml = get_and_parse_mollie_xml(request_dict)
        order = parsed_xml.find('order')
        consumer = order.find('consumer')
        if consumer:
            self.consumer_account = consumer.findtext('consumerAccount')
            self.consumer_city = consumer.findtext('consumerCity')
            self.consumer_name = consumer.findtext('consumerName')
            self.save()
        if order.findtext('payed') == 'true':
            return True
        return False

    check = is_paid

    @property
    def bank_name(self):
        return self.get_bank_id_display()

    def __unicode__(self):
        return u'Mollie/iDEAL Payment ID: %d' % self.id
