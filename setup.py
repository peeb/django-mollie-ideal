from distutils.core import setup

setup(name='django-mollie-ideal',
      version='0.1',
      description='Python/Django interface to Mollie.nl iDEAL API',
      long_description=open('README.rst').read(),
      author='Paul Burt',
      author_email='paul.burt@gmail.com',
      license='BSD',
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utlities'],
      url='http://github.com/peeb/django-mollie-ideal',
      download_url='http://github.com/peeb/django-mollie-ideal/downloads',
      packages=['mollie',
                'mollie.ideal',
                'mollie.ideal.management',
                'mollie.ideal.management.commands']
      )
