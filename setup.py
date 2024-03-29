import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-itassets',
    version = '0.1',
    packages = ['itassets'],
    include_package_data = True,
    test_suite = 'itassets.runtests.runtests',
    license = 'Apache License',
    description = 'Simple IT asset management using Django Admin',
    long_description = README,
    url = 'https://github.com/cschwede/django-itassets',
    author = 'Christian Schwede',
    author_email = 'info@cschwede.de',
    install_requires=['django>=1.5', 'django-grappelli'],
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
