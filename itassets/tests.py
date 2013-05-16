""" Tests for assertmgr """
#pylint:disable=E1101, C0111, R0904, C0301
from datetime import date, timedelta

from django.test import TestCase
from django.test.utils import setup_test_environment
from django.contrib.admin.sites import AdminSite

from itassets.models import HardwareGroup, Hardware, Maker, Person, Location
from itassets.models import Vendor, Software, License, SupportContract
from itassets.admin import HardwareAdmin, SoftwareAdmin, LicenseAdmin
from itassets.admin import RemainingListFilter, ExpireFilter

import sys
sys.path.append('.')

setup_test_environment()


def common_setup(self):
    self.expires = (date.today() + timedelta(42)).strftime('%Y-%m-%d')

    self.hardware_group = HardwareGroup.objects.create(name='Notebook')
    self.maker = Maker.objects.create(name='Maker')
    self.person = Person.objects.create(name='Me')
    self.location = Location.objects.create(name='Room')
    self.hardware = Hardware.objects.create(name='Model',
                                           location=self.location,
                                           hardware_group=self.hardware_group,
                                           maker=self.maker)

    self.hardware.person.add(self.person)

    self.vendor = Vendor.objects.create(name='Someone')
    self.maker2 = Maker.objects.create(name='Maker')
    self.software = Software.objects.create(vendor=self.vendor,
                                            name='Software',
                                            maker=self.maker2)

    self.license = License.objects.create(software=self.software,
                                          expires=self.expires,
                                          count=3)
    self.license.hardware.add(self.hardware)
    self.license.person.add(self.person)

    self.support = SupportContract.objects.create(hardware=self.hardware,
                                                  expires=self.expires)


class ModelTests(TestCase):
    """ Tests for assertmgr """

    def setUp(self):
        common_setup(self)

    def test_unicode(self):
        self.assertEqual(str(self.hardware), 'Maker Model (Me, Room)')
        self.assertEqual(str(self.hardware_group), 'Notebook')
        self.assertEqual(str(self.maker), 'Maker')
        self.assertEqual(str(self.person), 'Me')
        self.assertEqual(str(self.location), 'Room')
        self.assertEqual(str(self.vendor), 'Someone')
        self.assertEqual(str(self.software), 'Maker Software')
        self.assertEqual(str(self.license),
            'Software (1 remaining, expires %s)' % self.expires)
        self.assertEqual(str(self.support),
            'Maker Model (Me, Room) (expires %s)' % self.expires)
        self.hardware.person.clear()
        self.assertEqual(str(self.hardware), 'Maker Model (Room)')

    def test_remaining_licenses(self):
        self.assertEqual(self.license.remaining(), 1)


class AdminTests(TestCase):
    """ Tests for assertmgr """

    def setUp(self):
        common_setup(self)
        self.site = AdminSite()
        self.request = None

    def test_full_name(self):
        hwadmin = HardwareAdmin(self.hardware, self.site)
        self.assertEqual(hwadmin.full_name(self.hardware),
            'Maker Model (Me, Room)')

        swadmin = SoftwareAdmin(self.software, self.site)
        self.assertEqual(swadmin.full_name(self.software),
            'Maker Software')

    def test_remaining_list_filter(self):
        license_admin = LicenseAdmin(self.license, self.site)
        rlf = RemainingListFilter(self.request, {},
                                  self.license, license_admin)
        self.assertEqual(rlf.lookups(self.request, license_admin),
                         (('5', '<= 5'), ('10', '<= 10')))

        licenses = License.objects.all()
        self.assertEqual(rlf.queryset(self.request, licenses), licenses)

        rlf = RemainingListFilter(self.request, {'remaining': '5'},
            self.license, license_admin)
        self.assertEqual(set(rlf.queryset(self.request, licenses)),
                         set(licenses))

        rlf = RemainingListFilter(self.request, {'remaining': '10'},
                                  self.license, license_admin)
        self.assertEqual(set(rlf.queryset(self.request, licenses)),
                         set(licenses))

    def test_expire_filter(self):
        license_admin = LicenseAdmin(self.license, self.site)
        rlf = ExpireFilter(self.request, {}, self.license, license_admin)
        self.assertEqual(rlf.lookups(self.request, license_admin), (
            ('expired', 'Already expired'),
            ('6weeks', 'Within 6 weeks'),)
        )

        licenses = License.objects.all()
        self.assertEqual(rlf.queryset(self.request, licenses), licenses)

        rlf = ExpireFilter(self.request, {'expiration': 'expired'},
            self.license, license_admin)
        self.assertEqual(set(rlf.queryset(self.request, licenses)), set([]))

        rlf = ExpireFilter(self.request, {'expiration': '6weeks'},
            self.license, license_admin)
        self.assertEqual(set(rlf.queryset(self.request, licenses)),
                         set(licenses))
