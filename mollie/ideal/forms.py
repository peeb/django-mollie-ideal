#-*- coding: utf-8 -*-

from decimal import Decimal

from django import forms

from mollie.ideal.models import MollieIdealPayment
from mollie.ideal.settings import MOLLIE_MIN_AMOUNT

class MollieIdealPaymentForm(forms.ModelForm):

    amount = forms.DecimalField(min_value=Decimal(MOLLIE_MIN_AMOUNT),
                                max_digits=64, decimal_places=2)

    class Meta:
        model = MollieIdealPayment
