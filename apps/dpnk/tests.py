# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2015 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
import datetime


@override_settings(
    SITE_ID=2,
    FAKE_DATE=datetime.date(year=2010, month=11, day=20),
)
class AdminFilterTests(TestCase):
    fixtures = ['campaign', 'views']

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_admin_views(self):
        """
        test if the admin pages work
        """
        self.assertTrue(self.client.login(username='admin', password='admin'))
        response = self.client.get(reverse("admin:dpnk_userattendance_changelist"), HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_code, 200)

    def test_dpnk_views_no_login(self):
        address = reverse('registrace')
        response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_code, 200)

    @override_settings(
        FAKE_DATE=datetime.date(year=2010, month=10, day=1),
    )
    def test_dpnk_registration_out_of_phase(self):
        address = reverse('registrace')
        response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_message, "out_of_phase")
        self.assertEqual(response.status_code, 403)

    def test_dpnk_views(self):
        """
        test if the user pages work
        """
        self.assertTrue(self.client.login(username='test', password='test'))

        address = reverse('upravit_profil')
        response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_code, 200)

        address = reverse('profil')
        response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_code, 302)

        address = reverse('zmenit_tym')
        response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_code, 200)

        address = reverse('upravit_trasu')
        response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_code, 200)

        address = reverse('zmenit_triko')
        response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_code, 200)

        address = reverse('working_schedule')
        response = self.client.get(address, HTTP_HOST="testing-campaign.testserver")
        self.assertEqual(response.status_code, 200)
