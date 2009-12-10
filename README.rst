Welcome
=======

django-mollie-ideal provides a python interface to the iDEAL API by Mollie.nl_ for use in django projects.

.. _Mollie.nl: http://www.mollie.nl/

iDEAL is an online payment system used in the Netherlands which allows Dutch consumers to make payments via the secure environment of their own bank. It is only available in the Netherlands.

Mollie.nl provide a unified API which removes the complexity of interacting with the individual Dutch banks which support iDEAL payments. You can find detailed information about the Mollie.nl iDEAL API here_.

.. _here: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/en/

Nederlandse versie vindt u hier_.

.. _hier: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/

Installation
============

Since django-mollie-ideal currently doesn't contain any Django models it does not need to be added to your ``INSTALLED_APPS`` in ``settings.py``. You simply need to install it or download it and link it into your ``PYTHONPATH``.

Registering with Mollie.nl
==========================

Before you can start using django-mollie-ideal you must `register with Mollie.nl`_.

.. _`register with Mollie.nl`: http://www.mollie.nl/aanmelden/

Once you have registered you will receive a so-called "Partner ID" which you should set as the value of ``MOLLIE_PARTNER_ID`` in your Django project's ``settings.py`` file. See below for more information about the available settings.

Settings
========

::

    # you must also set 'iDEAL testmode aan' or 'iDEAL testmode uit'
    # at the following URL: http://www.mollie.nl/beheer/betaaldiensten/instellingen/
    MOLLIE_TEST = True # aan/on
    #MOLLIE_TEST = False # uit/off
    
    MOLLIE_PARTNER_ID = 123456

    MOLLIE_REPORT_URL = 'http://yoursite.yourdomain.com/payment/process/'
    MOLLIE_RETURN_URL = 'http://yoursite.yourdomain.com/payment/thankyou/'

    MOLLIE_TIMEOUT = 20 # seconds

Setup your URLs
===============

::

    urlpatterns = patterns('your_project.views',
        ...

        url(r'^payment/process/$', 'mollie_report', name='mollie_report'),
        url(r'^payment/thankyou/$', 'mollie_return', name='mollie_return'),

        url(r'^payment/give/$', 'give', name='give'),

        ...
    )

Using the banklist in your models and/or forms
==============================================

To be filled in.

Interacting with Mollie.nl
==========================

django-mollie-ideal makes no assumptions about your site installation. It is entirely up to you to decide what information to capture from users and what information you wish to store in your own database.

Interaction with Mollie.nl happens via a few utility functions in ``mollie.ideal.utils``. The following gives a broad overview of the required steps:

Step 1. Build a dictionary to describe your payment.

Step 2. Pass this dictionary as an argument to ``fetch_mollie_payment()``. The response contains a transaction_id and an order_url. Save the transaction_id in your model and pass the order_url to your template context to proceed with the payment.

Step 3. Setup a "return" URL which acts as a Thank You page for users of your site.

Step 4. Setup a "report" URL which uses ``check_mollie_payment()`` to confirm with Mollie.nl that the transaction was successful and perform any site-specific tasks based on this response (for example you might want to mark an invoice 'status' field as 'paid' or 'complete').

The ``views.py`` code below is a reasonably complete example of the above steps::

    from django.conf import settings
    from django.http import HttpResponseServerError
    from django.shortcuts import render_to_response
    from django.template import RequestContext

    from mollie.ideal.utils import build_mollie_url, check_mollie_payment, fetch_mollie_payment

    from my_project.forms import MyProductForm

    def give(request, form_class=MyProductForm, testmode=settings.MOLLIE_TEST):
        if request.method == 'POST':
            form = form_class(data=request.POST) 
            cd = form.cleaned_data
            invoice = form.save(commit=False)
            if testmode:
                invoice.test = True
            # Step 1
            payment_dict = {
                'amount': invoice.amount,
                'bank_id': cd['bank_id'],
                'description': invoice.description,
                'partnerid': settings.MOLLIE_PARTNER_ID,
                'reporturl': settings.MOLLIE_REPORT_URL,
                'returnurl': settings.MOLLIE_RETURN_URL,
            }
            # Step 2
            mollie_response = fetch_mollie_payment(payment_dict)
            order_url = mollie_response['order_url']
            invoice.transaction_id = mollie_response['transaction_id']
            invoice.save()
            return render_to_response('give_step2.html', {'invoice': invoice, 'order_url': order_url},
                context_instance=RequestContext(request))
        else:
            form = form_class()
        return render_to_response('give_step1.html', {'form': form},
            context_instance=RequestContext(request))
    

    def mollie_return(request):

    def mollie_report(request):

Templates
=========

To be filled in.

