==================
django-itassets
==================

[![Build Status](https://travis-ci.org/cschwede/django-itassets.png?branch=master)](https://travis-ci.org/cschwede/django-itassets)

Django app to track your IT licenses and support contracts.

Basically these are just some models and admin hooks for Django. Using the
Django admin interface you can track your expiring software licenses and 
hardware support contracts. Software licenses can be assigned to hardware
items which gives you a number of your remaining unused licenses.

Test coverage is verified with https://pypi.python.org/pypi/coverage

![License overview](https://github.com/cschwede/django-itassets/blob/master/screenshots/licenses.png?raw=true)

Grappelli is used to improve the admin interface.


Quick start
-----------

1. Start a new Django project.

2. Add "itassets" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = (
        ...
        'grappelli'
        'itassets',
    )

3. Run `python manage.py syncdb` to create the models.

4. Start the development server and visit http://127.0.0.1:8000/admin/.
