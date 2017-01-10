# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2016 o.s. Auto*Mat
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
import datetime

from PyPDF2 import PdfFileReader

from django.test import TestCase

from model_mommy import mommy


class DiscountCouponTests(TestCase):
    def test_save(self):
        discount_coupon = mommy.make(
            'coupons.DiscountCoupon',
            coupon_type__prefix="AA",
            coupon_type__campaign__slug="testing-campaign",
            coupon_type__valid_until=datetime.datetime(2017, 12, 12),
        )
        self.assertRegex(discount_coupon.name(), r"AA-[A-Z]{6}")
        self.assertRegex(discount_coupon.coupon_pdf.name, r"coupon_[-]?[0-9]+\.pdf")
        pdf = PdfFileReader(discount_coupon.coupon_pdf)
        pdf_string = pdf.pages[0].extractText()
        self.assertTrue(discount_coupon.name() in pdf_string)
        self.assertTrue("12. 12. 2017" in pdf_string)

    def test_available(self):
        discount_coupon = mommy.make(
            'coupons.DiscountCoupon',
            coupon_type__campaign__slug="testing-campaign",
            user_attendance_number=None,
        )
        self.assertTrue(discount_coupon.available())
