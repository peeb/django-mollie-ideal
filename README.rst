Overview
========

``django-mollie-ideal`` provides a Python interface to the iDEAL API by Mollie.nl_ for use in Django projects. It requires Python 2.5 or higher.

.. _Mollie.nl: http://www.mollie.nl/

iDEAL is a payment system used in the Netherlands which allows Dutch consumers to make online payments via the secure environment of their own bank.

Mollie.nl provide a unified API which removes the complexity of interacting with the individual Dutch banks which support iDEAL payments. You can find detailed information about the Mollie.nl iDEAL API here_.

.. _here: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/en/

Nederlandse versie vindt u hier_.

.. _hier: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/

Installation
============

Link the ``mollie`` directory into your ``PYTHONPATH`` and add ``mollie.ideal`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'mollie.ideal',
    )

``django-mollie-ideal`` will use ``lxml`` if it is installed. You can install ``lxml`` as follows::

    $ pip install lxml

If you do not have ``lxml`` installed, the built-in ``xml.etree.[c]ElementTree`` will be used instead.

Registering with Mollie.nl
==========================

Before you can start using ``django-mollie-ideal`` you must `register with Mollie.nl`_.

.. _`register with Mollie.nl`: http://www.mollie.nl/aanmelden/

Once you have registered you will receive a so-called "Partner ID" which you should set as the value of ``MOLLIE_PARTNER_ID`` in your Django project's ``settings.py`` file. See below for more information about the available settings.

Settings
========

::

    ## Required settings ##

    MOLLIE_PARTNER_ID = 123456

    MOLLIE_REPORT_URL = 'http://yoursite.yourdomain.com/payment/process/'
    MOLLIE_RETURN_URL = 'http://yoursite.yourdomain.com/payment/thankyou/'

    ## Optional settings ##

    # You must also set 'iDEAL testmode aan' or 'iDEAL testmode uit'
    # at the following URL: http://www.mollie.nl/beheer/betaaldiensten/instellingen/
    MOLLIE_TEST = True # defaults to False

    MOLLIE_MIN_AMOUNT = '1.18' # defaults to '1.18'

    import os
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    MOLLIE_BANKLIST_DIR = SITE_ROOT # defaults to your project's root directory

    MOLLIE_PROFILE_KEY = 'Jas87821'

    MOLLIE_REVERSE_URLS = True # defaults to False, if set True, both reporting and returning url have to be reversable, e.g.:
    MOLLIE_RETURN_URL = 'shop:thanks'


Grabbing the latest list of supported banks
===========================================

Before you start to use ``django-mollie-ideal`` in your Django project, you should first grab the latest list of supported banks from Mollie.nl. The ``_get_mollie_xml()`` function in the ``mollie.ideal.helpers`` module used by ``MollieIdealPayment`` requires this file to build the list of supported banks available to your application.

Once ``django-mollie-ideal`` is installed in your project a new Django management command ``get_mollie_banklist`` will become available. This command requests the latest list of supported banks and saves the file ``mollie_banklist.xml`` to the current directory. You should also specify ``MOLLIE_BANKLIST_DIR`` in your ``settings.py`` file.

You should run this command periodically to refresh the list of banks available to users of your web application. Here's how::

    $ cd /path/to/your/django_app
    $ python manage.py get_mollie_banklist

Note that if you do not run this command, ``django-mollie-ideal`` will default to using its own list of supported banks. However, this may well already be out-of-date by the time you start using your application.

Setup your URLs
===============

How you setup your ``urls.py`` is, of course, entirely up to you. The following serves as an example::

    urlpatterns = patterns('my_project.my_app.views',
        ...
        url(r'^payment/pay/$', 'make_payment', name='pay'),
        url(r'^payment/process/$', 'process_payment', name='process_payment'),
        url(r'^payment/thankyou/$', 'payment_thanks', name='payment_thanks'),
        ...
    )

Models
======

Most of the logic in ``django-mollie-ideal`` is handled by the ``MollieIdealPayment`` class. All you need to do is subclass and specialise ``MollieIdealPayment`` with your own site-specific requirements. An example follows::

    from mollie.ideal.models import MollieIdealPayment

    class MyPayment(MollieIdealPayment):
        name = models.CharField(max_length=100)
        email = models.EmailField()
        complete = models.BooleanField()

Payment processing is handled by 2 separate instance methods on ``MollieIdealPayment`` - ``get_order_url()`` and ``is_paid()``. These are analogous to the "fetch" and "check" steps respectively, as described in the Mollie API. As a convenience, you may also use ``fetch()`` and ``check()`` in place of ``get_order_url()`` and ``is_paid()``.

Note that because ``MollieIdealPayment`` is an `abstract base class`_, you will also need to setup your own ``admin.py`` file to represent your own ``MyPayment`` model in the Django admin.

.. _`abstract base class`: http://docs.djangoproject.com/en/dev/topics/db/models/#id6

Forms
=====

You will also need to create a specialised form by subclassing ``MollieIdealPaymentForm``. An example follows, based on the previous model example::

    from mollie.ideal.forms import MollieIdealPaymentForm
    from my_project.my_app.models import MyPayment

    class MyPaymentForm(MollieIdealPaymentForm):

        class Meta:
            model = MyPayment
            fields = ('bank_id', 'amount', 'name', 'email')

``MollieIdealPaymentForm`` subclasses ``django.forms.ModelForm``. This means that in your own form, you should take care to manually specify which fields from it you wish to display in addition to the custom fields from your own model. In the above example we're displaying ``bank_id`` and ``amount`` from ``MollieIdealPaymentForm`` and ``name`` and ``email`` from the ``MyPaymentForm`` subclass. You must display ``bank_id`` as a bare minimum. The Django ``ModelForm`` documentation_ is worth consulting for more detailed informtation on how to create forms from models.

Note that Mollie require payments to be a minimum of €1.18 (€0.99 + BTW). Although ``MollieIdealPaymentForm`` already handles this for you, it is worth bearing in mind when you are pricing items on your site. 

.. _documentation: http://docs.djangoproject.com/en/dev/topics/forms/modelforms/

Views
=====

There are 3 main steps.

Step 1. Define your payment and use its ``get_order_url()`` (or ``fetch()``) instance method to setup the transaction with Mollie.nl. ``get_order_url()`` takes care of storing the Mollie.nl ``transaction_id`` which identifies your payment and returns an ``order_url`` for use in your view function's template context. Note that ``get_order_url()`` also performs a ``save()`` on your payment instance so you do not need to do this in your view function.

Step 2. Setup a return URL which acts as a "Thank You" landing page for users of your site. Once the user has finished the transaction with their bank, they will be redirected to this page.

Step 3. Setup a report URL which uses the ``is_paid()`` (or ``check()``) instance method to check with Mollie.nl that the transaction was successful and to perform any site-specific processing tasks based on this response. For example you might want to mark the above ``MyPayment`` instance's ``complete`` field as ``True``. The function you attach to this URL should handle both successful and unsuccessful/cancelled payments. Note that ``is_paid()`` does not handle saving the payment instance to the database because it is likely that you will need to perform various processing tasks such as setting site-specific attributes before committing to the database. Therefore you must remember to perform a ``save()`` in your view.

The ``views.py`` code below is a reasonably complete example of the above steps::

    from django.http import HttpResponse, HttpResponseServerError
    from django.shortcuts import redirect, render_to_response
    from django.template import RequestContext

    from my_project.my_app.forms import MyPaymentForm

    def make_payment(request, form_class=MyPaymentForm): # Step 1
        if request.method == 'POST':
            form = form_class(data=request.POST) 
            if form.is_valid()
                cd = form.cleaned_data
                payment = form.save(commit=False)
                payment.description = u'max 29 char product description'
                payment.amount = cd['amount']
                payment.name = cd['name']
                payment.email = cd['email']
                order_url = payment.get_order_url()
                return render_to_response('payment_step2.html',
                                          {'payment': payment, 'order_url': order_url},
                                          context_instance=RequestContext(request))
        else:
            form = form_class()
        return render_to_response('payment_step1.html', {'form': form},
                                  context_instance=RequestContext(request))

    def payment_thanks(request): # Step 2
        transaction_id = request.GET.get('transaction_id', None)
        if transaction_id:
            payment = MyPayment.objects.get(transaction_id=transaction_id)
            return render_to_response('payment_thanks.html',
                                      {'payment': payment},
                                      context_instance=RequestContext(request))
        else:
            return redirect('/')

    def process_payment(request): # Step 3
        transaction_id = request.GET.get('transaction_id', None)
        if transaction_id:
            payment = MyPayment.objects.get(transaction_id=transaction_id)
            if payment.is_paid():
                # Any processing you want to do goes here
                payment.complete = True
            # Don't forget to commit the changes!
            payment.save()
            return HttpResponse('OK')
        else:
            return HttpResponseServerError

Making test payments
====================

Once your project is written and configured, you can start to make some test payments. Mollie provide a test bank called "TBM Bank (The Big Mollie Bank)" which can be used as a developer sandbox to test out your code.

To enable this test bank in your project you need to set ``MOLLIE_TEST`` to ``True`` in your ``settings.py`` file, then go to your `Mollie.nl account settings`_ and set "iDEAL testmode aan". Both of these steps are required.

Once this is done, an additional bank "TBM Bank (Test Bank)" will appear in the list of supported banks in your application. You should use this bank (and **only** this bank) to make test transactions.

When you decide to go into production, you must set ``MOLLIE_TEST`` to ``False`` in your ``settings.py`` file **and** set "iDEAL testmode uit" in your `Mollie.nl account settings`_.

.. _`Mollie.nl account settings`: https://www.mollie.nl/beheer/betaaldiensten/instellingen/
