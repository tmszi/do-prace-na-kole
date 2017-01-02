# -*- coding: utf-8 -*-

# Author: Hynek Hanke <hynek.hanke@auto-mat.cz>
# Author: Petr Dlouhý <petr.dlouhy@email.cz>
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

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from .address import Address, get_address_string


class Company(models.Model):
    """Organizace"""

    class Meta:
        verbose_name = _(u"Organizace")
        verbose_name_plural = _(u"Organizace")
        ordering = ('name',)

    name = models.CharField(
        unique=True,
        verbose_name=_(u"Název organizace"),
        help_text=_(u"Např. „Výrobna, a.s.“, „Příspěvková, p.o.“, „Nevládka, z.s.“, „Univerzita Karlova“"),
        max_length=60,
        null=False,
    )
    address = Address()
    ico = models.PositiveIntegerField(
        default=None,
        verbose_name=_(u"IČO"),
        null=True,
        blank=False,
    )
    dic = models.CharField(
        verbose_name=_(u"DIČ"),
        max_length=15,
        default="",
        null=True,
        blank=True,
    )
    active = models.BooleanField(
        verbose_name=_(u"Aktivní"),
        default=True,
        null=False,
    )

    def has_filled_contact_information(self):
        address_complete = self.address.street and self.address.street_number and self.address.psc and self.address.city
        return self.name and address_complete and self.ico

    def __str__(self):
        return "%s" % self.name

    def company_address(self):
        return get_address_string(self.address)