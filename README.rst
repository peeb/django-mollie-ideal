Welcome
=======

``django-mollie-ideal`` provides a Python interface to the iDEAL API by Mollie.nl_ for use in Django projects.

.. _Mollie.nl: http://www.mollie.nl/

iDEAL is an online payment system used in the Netherlands which allows Dutch consumers to make payments via the secure environment of their own bank.

Mollie.nl provide a unified API which removes the complexity of interacting with the individual Dutch banks which support iDEAL payments. You can find detailed information about the Mollie.nl iDEAL API here_.

.. _here: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/en/

Nederlandse versie vindt u hier_.

.. _hier: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/

Installation
============

Link the ``mollie`` directory into your ``PYTHONPATH`` and add ``mollie`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
    ...
    'mollie',
    )

``django-mollie-ideal`` will use ``lxml`` if it is installed. You can install ``lxml`` as follows::

    easy_install lxml

or::

    pip install lxml

If you do not have ``lxml`` installed, the built-in ``xml.etree.cElementTree`` will be used instead.

Registering with Mollie.nl
==========================

Before you can start using django-mollie-ideal you must `register with Mollie.nl`_.

.. _`register with Mollie.nl`: http://www.mollie.nl/aanmelden/

Once you have registered you will receive a so-called "Partner ID" which you should set as the value of ``MOLLIE_PARTNER_ID`` in your Django project's ``settings.py`` file. See below for more information about the available settings.

Settings
========

::

    # You must also set 'iDEAL testmode aan' or 'iDEAL testmode uit'
    # at the following URL: http://www.mollie.nl/beheer/betaaldiensten/instellingen/
    MOLLIE_TEST = True # aan/on
    #MOLLIE_TEST = False # uit/off
    
    MOLLIE_PARTNER_ID = 123456

    MOLLIE_REPORT_URL = 'http://yoursite.yourdomain.com/payment/process/'
    MOLLIE_RETURN_URL = 'http://yoursite.yourdomain.com/payment/thankyou/'
    
    MOLLIE_MIN_AMOUNT = '1.18'

Set up your URLs
================

::

    urlpatterns = patterns('my_project.my_app.views',
        ...
        url(r'^payment/pay/$', 'make_payment', name='pay'),
        url(r'^payment/process/$', 'payment_report', name='payment_report'),
        url(r'^payment/thankyou/$', 'payment_return', name='payment_return'),
        ...
    )

Supported Banks
===============


Models
======

Most of the logic in ``django-mollie-ideal`` is handled by the ``MollieIdealPayment`` class. All you need to do is subclass and specialise ``MollieIdealPayment`` with your own site-specific requirements. An example follows::

    from mollie.ideal.models import MollieIdealPayment

    class MyPayment(MollieIdealPayment):
        name = models.CharField(max_length=100)
        email = models.EmailField()
        complete = models.BooleanField()

Payment processing is handled by 2 separate instance methods on ``MollieIdealPayment`` - ``get_order_url_and_save()`` and ``is_paid()``. These are analogous to the "fetch" and "check" steps respectively, as described in the Mollie API.

The list of supported banks is fetched dynamically every time an instance of your payment class is created. Future release of ``django-mollie-ideal`` may handle this with locally-stored xml files.

Forms
=====

You will also need to create a specialised form by subclassing ``MollieIdealPaymentForm``. An example follows, based on the previous model example::

    from mollie.ideal.forms import MollieIdealPaymentForm
    from my_project.my_app.models import MyPayment

    class MyPaymentForm(MollieIdealPaymentForm):

        class Meta:
            model = MyPayment
            fields = ('bank', 'amount', 'name', 'email')

``MollieIdealPaymentForm`` subclasses ``django.forms.ModelForm``. This means that in your own form, you should take care to manually specify which fields from it you wish to display in addition to the custom fields from your own model. In the above example, we're displaying ``bank`` and ``amount`` from ``MollieIdealPaymentForm`` and ``name`` and ``email`` from the ``MyPaymentForm`` subclass. You must display ``bank`` as a bare minimum.

Note that Mollie require payments to be a minimum of €1.18 (€0.99 + BTW). ``MollieIdealPaymentForm`` already handles this for you. This is worth bearing in mind when you are pricing items on your site.

Views
=====

There are 3 main steps.

Step 1. Define your payment and use its ``get_order_url_and_save()`` instance method to set up the transaction with Mollie.nl. ``get_order_url_and_save()`` takes care of storing the Mollie.nl ``transaction_id`` which identifies your payment and returns an ``order_url`` for use in your view function's template context. 

Step 2. Set up a return URL which acts as a "Thank You" landing page for users of your site. Once the user has finished the transaction with their bank, they will be redirected to this page.

Step 3. Set up a report URL which uses the ``is_paid()`` instance method to check with Mollie.nl that the transaction was successful and to perform any site-specific processing tasks based on this response. For example you might want to mark the above ``MyPayment`` instance's ``complete`` field as ``True``. The function you attach to this URL should handle both successful and unsuccessful/cancelled payments. For the sake of flexibility, ``is_paid()`` does not handle saving the payment instance to the database, so you must remember to perform a ``save()`` in your view.

The ``views.py`` code below is a reasonably complete example of the above steps::

    from django.conf import settings
    from django.http import HttpResponse, HttpResponseServerError
    from django.shortcuts import render_to_response
    from django.template import RequestContext

    from my_project.my_app.forms import MyPaymentForm

    def make_payment(request, form_class=MyPaymentForm): # Step 1
        if request.method == 'POST':
            form = form_class(request.POST) 
            if form.is_valid()
                cd = form.cleaned_data
                payment = form.save(commit=False)
                payment.description = u'max 29 char product description'
                payment.name = cd['name']
                payment.email = cd['email']
                order_url = payment.get_order_url_and_save()
                return render_to_response('payment_step2.html',
                                          {'payment': payment, 'order_url': order_url},
                                          context_instance=RequestContext(request))
        else:
            form = form_class()
        return render_to_response('payment_step1.html', {'form': form},
            context_instance=RequestContext(request))

    def payment_thanks(request): # Step 2

    def process_payment(request): # Step 3
        transaction_id = request.GET.get('transaction_id', None)
        if transaction_id:
            payment = MyPayment.objects.get(transaction_id=transaction_id)
            if payment.is_paid():
                # any processing you want to do goes here
                payment.complete = True
            # don't forget to commit the changes!
            payment.save()
            return HttpResponse('OK')
        else:
            return HttpResponseServerError
