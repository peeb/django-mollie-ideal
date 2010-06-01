#-*- coding: utf-8 -*-

from decimal import Decimal

from django import forms
from django.utils.translation import ugettext_lazy as _

from mollie.ideal.helpers import get_mollie_bank_choices
from mollie.ideal.models import MollieIdealPayment
from mollie.ideal.settings import MOLLIE_MIN_AMOUNT

class MollieIdealPaymentForm(forms.ModelForm):

    amount = forms.DecimalField(min_value=Decimal(MOLLIE_MIN_AMOUNT),
                                max_digits=64, decimal_places=2)
    bank_id = forms.ChoiceField(choices=get_mollie_bank_choices(),
                                label=_('Bank'))

    class Meta:
        model = MollieIdealPayment
