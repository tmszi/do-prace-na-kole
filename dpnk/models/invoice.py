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
import datetime

from author.decorators import with_author

import denorm

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import transaction
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from unidecode import unidecode

from .address import AddressOptional
from .company import Company
from .transactions import Payment, Status
from .. import invoice_pdf, util


@with_author
class Invoice(models.Model):
    """Faktura"""
    class Meta:
        verbose_name = _(u"Faktura")
        verbose_name_plural = _(u"Faktury")
        unique_together = (("sequence_number", "campaign"),)
        ordering = ('sequence_number', 'campaign', )

    created = models.DateTimeField(
        verbose_name=_(u"Datum vytvoření"),
        default=datetime.datetime.now,
        null=False,
    )
    exposure_date = models.DateField(
        verbose_name=_(u"Den vystavení daňového dokladu"),
        null=True,
        blank=True,
    )
    taxable_date = models.DateField(
        verbose_name=_(u"Den uskutečnění zdanitelného plnění"),
        null=True,
        blank=True,
    )
    payback_date = models.DateField(
        verbose_name=_("Datum splatnosti"),
        null=True,
        blank=True,
    )
    paid_date = models.DateField(
        verbose_name=_(u"Datum zaplacení"),
        default=None,
        null=True,
        blank=True,
    )
    company_pais_benefitial_fee = models.BooleanField(
        verbose_name=_(u"Moje organizace si přeje podpořit Auto*Mat a zaplatit benefiční startovné."),
        default=False,
    )
    total_amount = models.FloatField(
        verbose_name=_(u"Celková částka"),
        null=False,
        default=0,
    )
    invoice_pdf = models.FileField(
        verbose_name=_(u"PDF faktury"),
        upload_to=u'invoices',
        blank=True,
        null=True,
    )
    company = models.ForeignKey(
        Company,
        verbose_name=_(u"Organizace"),
        null=False,
        blank=False,
    )
    campaign = models.ForeignKey(
        'Campaign',
        verbose_name=_(u"Kampaň"),
        null=False,
        blank=False,
    )
    sequence_number = models.PositiveIntegerField(
        verbose_name=_(u"Pořadové číslo faktury"),
        null=False,
    )
    order_number = models.BigIntegerField(
        verbose_name=_(u"Číslo objednávky (nepovinné)"),
        null=True,
        blank=True,
    )
    company_name = models.CharField(
        verbose_name=_("Název organizace"),
        help_text=_("Název organizace. Pokud je prázdné, vyplní se všechny údaje podle nastavené organizace."),
        max_length=60,
        null=True,
        blank=True,
    )
    company_address = AddressOptional()
    company_ico = models.PositiveIntegerField(
        default=None,
        verbose_name=_("IČO organizace"),
        null=True,
        blank=True,
    )
    company_dic = models.CharField(
        verbose_name=_("DIČ organizace"),
        max_length=15,
        default="",
        null=True,
        blank=True,
    )

    def __str__(self):
        return "%s - %s" % (self.sequence_number, self.campaign.slug)

    def paid(self):
        if not self.paid_date:
            return False
        return self.paid_date <= util.today()

    def variable_symbol(self):
        return "%sD%03d" % (self.exposure_date.year, self.sequence_number)

    def document_number(self):
        return "%s%03d" % (self.exposure_date.year, self.sequence_number)

    def set_taxable_date(self):
        self.taxable_date = min(
            util.today(),
            self.campaign.phase("competition").date_to,
        )

    def set_payback_date(self):
        self.payback_date = util.today() + datetime.timedelta(days=14)

    def set_exposure_date(self):
        self.exposure_date = min(
            util.today(),
            self.campaign.phase("competition").date_to + datetime.timedelta(days=14),
        )

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.sequence_number:
            campaign = self.campaign
            first = campaign.invoice_sequence_number_first
            last = campaign.invoice_sequence_number_last
            last_transaction = Invoice.objects.filter(
                campaign=campaign,
                sequence_number__gte=first,
                sequence_number__lte=last,
            )
            last_transaction = last_transaction.order_by("sequence_number")
            last_transaction = last_transaction.last()
            if last_transaction:
                if last_transaction.sequence_number == last:
                    raise Exception(_(u"Došla číselná řada faktury"))
                self.sequence_number = last_transaction.sequence_number + 1
            else:
                self.sequence_number = first
        super(Invoice, self).save(*args, **kwargs)

    def payments_to_add(self):
        if hasattr(self, 'campaign'):
            return payments_to_invoice(self.company, self.campaign)

    @transaction.atomic
    def add_payments(self):
        payments = self.payments_to_add()
        self.payment_set = payments
        for payment in payments:
            payment.status = Status.INVOICE_MADE
            payment.save()
            denorm.flush()

    def fill_company_details(self):
        if not self.company_name:  # set invoice parameters from company
            self.company_name = self.company.name
            self.company_address = self.company.address
            self.company_ico = self.company.ico
            self.company_dic = self.company.dic

    def clean(self):
        if not self.pk and hasattr(self, 'campaign') and not self.payments_to_add().exists():
            raise ValidationError(_(u"Neexistuje žádná nefakturovaná platba"))


def change_invoice_payments_status(sender, instance, changed_fields=None, **kwargs):
    field, (old, new) = next(iter(changed_fields.items()))
    if new is not None:
        for payment in instance.payment_set.all():
            payment.status = Status.INVOICE_PAID
            payment.save()
            denorm.flush()


def payments_to_invoice(company, campaign):
    return Payment.objects.filter(
        pay_type='fc',
        status=Status.COMPANY_ACCEPTS,
        user_attendance__team__subsidiary__company=company,
        user_attendance__campaign=campaign,
    )


@receiver(pre_save, sender=Invoice)
def fill_invoice_parameters(sender, instance, **kwargs):
    instance.fill_company_details()

    if not instance.taxable_date:
        instance.set_taxable_date()

    if not instance.payback_date:
        instance.set_payback_date()

    if not instance.exposure_date:
        instance.set_exposure_date()


@receiver(post_save, sender=Invoice)
def create_invoice_files(sender, instance, created, **kwargs):
    if created:
        instance.add_payments()

    if not instance.invoice_pdf:
        temp = NamedTemporaryFile()
        invoice_pdf.make_invoice_sheet_pdf(temp, instance)
        filename = "%s/invoice_%s_%s_%s_%s.pdf" % (
            instance.campaign.slug,
            instance.sequence_number,
            unidecode(instance.company.name[0:40]),
            instance.exposure_date.strftime("%Y-%m-%d"),
            hash(str(instance.pk) + settings.SECRET_KEY)
        )
        instance.invoice_pdf.save(filename, File(temp))
        instance.save()


@receiver(pre_delete, sender=Invoice)
def user_attendance_pre_delete(sender, instance, *args, **kwargs):
    for payment in instance.payment_set.all():
        payment.status = Status.COMPANY_ACCEPTS
        payment.save()
        denorm.flush()
