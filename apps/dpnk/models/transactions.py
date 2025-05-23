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
import logging

from author.decorators import with_author

from denorm import denormalized, depend_on_related

from django.contrib.gis.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from polymorphic.models import PolymorphicModel

from .payu_ordered_product import PayUOrderedProduct
from .. import mailing
from ..email import payment_confirmation_company_mail, payment_confirmation_mail

logger = logging.getLogger(__name__)


class Status(object):
    NEW = 1
    CANCELED = 2
    COMMENCED = 4
    WAITING_CONFIRMATION = 5
    REJECTED = 7
    DONE = 99
    WRONG_STATUS = 888
    COMPANY_ACCEPTS = 1005
    INVOICE_MADE = 1006
    INVOICE_PAID = 1007
    FREE_FOR_PARTNER = 1008

    PACKAGE_NEW = 20001
    PACKAGE_ACCEPTED_FOR_ASSEMBLY = 20002
    PACKAGE_ASSEMBLED = 20003
    PACKAGE_SENT = 20004
    PACKAGE_DELIVERY_CONFIRMED = 20005
    PACKAGE_DELIVERY_DENIED = 20006
    PACKAGE_RECLAIM_CAUSED = 20007
    PACKAGE_RECLAIM_UNCAUSED = 20008

    BIKE_REPAIR = 40001

    COMPETITION_START_CONFIRMED = 30002


PACKAGE_STATUSES = [
    (Status.PACKAGE_NEW, _("Nový")),
    (Status.PACKAGE_ACCEPTED_FOR_ASSEMBLY, _("Přijat k sestavení")),
    (Status.PACKAGE_ASSEMBLED, _("Sestaven")),
    (Status.PACKAGE_SENT, _("Odeslán")),
    (Status.PACKAGE_DELIVERY_CONFIRMED, _("Doručení potvrzeno")),
    (Status.PACKAGE_DELIVERY_DENIED, _("Dosud nedoručeno")),
    (Status.PACKAGE_RECLAIM_CAUSED, _("Reklamován (zaviněná)")),
    (Status.PACKAGE_RECLAIM_UNCAUSED, _("Reklamován (nezaviněná)")),
]

PAYMENT_STATUSES = [
    (Status.NEW, _("Nová")),
    (Status.CANCELED, _("Zrušena")),
    (Status.REJECTED, _("Odmítnuta")),
    (Status.COMMENCED, _("Zahájena")),
    (Status.WAITING_CONFIRMATION, _("Očekává potvrzení")),
    (Status.REJECTED, _("Platba zamítnuta, prostředky nemožno vrátit, řeší PayU")),
    (Status.DONE, _("Platba přijata")),
    (Status.WRONG_STATUS, _("Nesprávný status -- kontaktovat PayU")),
    (Status.COMPANY_ACCEPTS, _("Platba akceptována organizací")),
    (Status.FREE_FOR_PARTNER, _("Partner má startovné zdarma")),
    (Status.INVOICE_MADE, _("Faktura vystavena")),
    (Status.INVOICE_PAID, _("Faktura zaplacena")),
]

BIKE_REPAIR_STATUSES = [
    (Status.BIKE_REPAIR, "Oprava v cykloservisu"),
]

COMPETITION_STATUSES = [
    (Status.COMPETITION_START_CONFIRMED, "Potvrzen vstup do soutěže"),
]

STATUS = tuple(
    PACKAGE_STATUSES + PAYMENT_STATUSES + BIKE_REPAIR_STATUSES + COMPETITION_STATUSES
)


@with_author
class Transaction(PolymorphicModel):
    """Transakce"""

    status = models.PositiveIntegerField(
        verbose_name=_("Status"),
        default=0,
        choices=STATUS,
        null=False,
        blank=False,
    )
    user_attendance = models.ForeignKey(
        "UserAttendance",
        related_name="transactions",
        null=True,
        blank=False,
        default=None,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(
        verbose_name=_("Vytvoření"),
        default=datetime.datetime.now,
        null=False,
    )
    description = models.TextField(
        verbose_name=_("Popis"),
        null=True,
        blank=True,
        default="",
    )
    realized = models.DateTimeField(
        verbose_name=_("Realizace"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Transakce")
        verbose_name_plural = _("Transakce")


class CommonTransaction(Transaction):
    """Obecná transakce"""

    class Meta:
        verbose_name = _("Obecná transakce")
        verbose_name_plural = _("Obecné transakce")


class UserActionTransaction(Transaction):
    """Uživatelská akce"""

    class Meta:
        verbose_name = _("Uživatelská akce")
        verbose_name_plural = _("Uživatelské akce")


class Payment(Transaction):
    """Platba"""

    done_statuses = [
        Status.DONE,
        Status.COMPANY_ACCEPTS,
        Status.FREE_FOR_PARTNER,
        Status.INVOICE_MADE,
        Status.INVOICE_PAID,
    ]
    waiting_statuses = [
        Status.NEW,
        Status.COMMENCED,
        Status.WAITING_CONFIRMATION,
    ]

    PAY_TYPES = (
        ("mp", _("mPenize - mBank")),
        ("mps", _("mPenize - mBank")),
        ("kb", _("MojePlatba")),
        ("rf", _("ePlatby pro eKonto")),
        ("pg", _("GE Money Bank")),
        ("pv", _("Sberbank (Volksbank)")),
        ("pf", _("Fio banka")),
        ("pfs", _("Fio banka")),
        ("cs", _("Česká spořitelna")),
        ("css", _("Česká spořitelna")),
        ("era", _("Era - Poštovní spořitelna")),
        ("cb", _("ČSOB")),
        ("c", _("Kreditní karta přes GPE")),
        ("bt", _("bankovní převod")),
        ("pt", _("převod přes poštu")),
        ("sc", _("superCASH")),  # Deprecated
        ("psc", _("PaySec")),
        ("mo", _("Mobito")),
        ("uc", _("UniCredit")),
        ("t", _("testovací platba")),
        ("fa", _("faktura mimo PayU")),
        ("fc", _("platba přes firemního koordinátora")),
        ("am", _("člen Klubu přátel AutoMatu")),
        ("amw", _("kandidát na členství v Klubu přátel AutoMatu")),
        ("fe", _("neplatí startovné")),
        ("rbczs", _("Raiffeisen Bank")),
        ("rf", _("Raiffeisen Bank")),
        ("cbs", _("Československá obchodní banka")),
        ("kb", _("Komerční banka")),
        ("kbs", _("Komerční banka")),
        ("mons", _("MONETA Money Bank")),
        ("dpcz", _("Pay later with Twisto - Czech")),
        ("PBL", _("online nebo standardní převod")),  # PAYU REST API
        (
            "CARD_TOKEN",
            _("platba kartou (včetně MasterPass a Visa checkout)"),
        ),  # PAYU REST API
        ("INSTALLMENTS", _("platba cez  Payu | Installments řešení")),  # PAYU REST API
    )
    PAY_TYPES_DICT = dict(PAY_TYPES)

    NOT_PAYING_TYPES = [
        "am",
        "amw",
        "fe",
    ]

    PAYU_PAYING_TYPES = [
        "mp",
        "kb",
        "rf",
        "pg",
        "pv",
        "pf",
        "cs",
        "era",
        "cb",
        "c",
        "bt",
        "pt",
        "sc",
        "psc",
        "mo",
        "uc",
        "t",
    ]

    PAYMENT_SUBJECT = [
        ("individual", _("Jednotlivec")),
        ("voucher", _("Slevový kupón")),
        ("company", _("Organizace")),
        ("school", _("Škola")),
    ]

    PAYMENT_CATEGORY = [
        ("entry_fee", _("Startovné")),
        ("donation", _("Dar")),
        ("entry_fee-donation", _("Startovné a dar")),
    ]

    class Meta:
        verbose_name = _("Platební transakce")
        verbose_name_plural = _("Platební transakce")

    order_id = models.CharField(
        verbose_name="Order ID",
        max_length=50,
        null=True,
        blank=True,
        default="",
    )
    session_id = models.CharField(
        verbose_name="Session ID",
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        default=None,
    )
    trans_id = models.CharField(
        verbose_name="Transaction ID",
        max_length=50,
        null=True,
        blank=True,
    )
    amount = models.PositiveIntegerField(
        verbose_name=_("Částka"),
        null=False,
    )
    pay_type = models.CharField(
        verbose_name=_("Typ platby"),
        choices=PAY_TYPES,
        max_length=50,
        null=True,
        blank=True,
    )
    error = models.PositiveIntegerField(
        verbose_name=_("Chyba"),
        null=True,
        blank=True,
    )
    invoice = models.ForeignKey(
        "Invoice",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name=("payment_set"),
    )
    pay_subject = models.CharField(
        verbose_name=_("Platobní subjekt"),
        choices=PAYMENT_SUBJECT,
        max_length=20,
        null=True,
        blank=True,
    )
    pay_category = models.CharField(
        verbose_name=_("Platobní kategorie"),
        choices=PAYMENT_CATEGORY,
        max_length=20,
        null=True,
        blank=True,
    )
    payu_ordered_product = models.ManyToManyField(
        PayUOrderedProduct,
        verbose_name=_("PayU objednávaný produkt"),
        help_text=_("PayU objednávaný produkt(y) - RTWBB startovné, RTWBB dar"),
        blank=True,
    )
    # TODO: This is a hack which allows making denorms dependend only on Payment and not on any other type of transaction.
    # Better would be to add some kind of conditions to denorms
    @denormalized(
        models.ForeignKey,
        "UserAttendance",
        null=True,
        blank=False,
        default=None,
        on_delete=models.CASCADE,
    )
    @depend_on_related(
        "Transaction", foreign_key="transaction_ptr", skip={"updated", "created"}
    )
    def payment_user_attendance(self):
        return self.user_attendance

    # TODO: This is a hack which allows making denorms dependend only on Payment and not on any other type of transaction.
    # Better would be to add some kind of conditions to denorms
    @denormalized(
        models.PositiveIntegerField, default=0, choices=STATUS, null=True, blank=True
    )
    @depend_on_related(
        "Transaction", foreign_key="transaction_ptr", skip={"updated", "created"}
    )
    def payment_status(self):
        return self.status

    def save(self, *args, **kwargs):
        status_before_update = None
        if self.id:
            status_before_update = Payment.objects.get(pk=self.id).status
            logger.info(
                "Saving payment (before): %s"
                % Payment.objects.get(pk=self.id).full_string()
            )
        super().save(*args, **kwargs)

        statuses_company_ok = (
            Status.COMPANY_ACCEPTS,
            Status.INVOICE_MADE,
            Status.INVOICE_PAID,
        )
        if (
            self.user_attendance
            and (status_before_update != Status.DONE)
            and self.status == Status.DONE
        ):
            payment_confirmation_mail(self.user_attendance)
        elif (
            self.user_attendance
            and (status_before_update not in statuses_company_ok)
            and self.status in statuses_company_ok
        ):
            payment_confirmation_company_mail(self.user_attendance)

        if self.id:
            payment = Payment.objects.filter(pk=self.id)
            if payment:
                logger.info("Saving payment (after): %s" % payment[0].full_string())

    def full_string(self):
        if self.user_attendance:
            user = self.user_attendance
            username = self.user_attendance.userprofile.user.username
        else:
            user = None
            username = None
        return (
            "id: %s, "
            "user: %s (%s), "
            "order_id: %s, "
            "session_id: %s, "
            "trans_id: %s, "
            "amount: %s, "
            "description: %s, "
            "created: %s, "
            "realized: %s, "
            "pay_type: %s, "
            "status: %s, "
            "error: %s"
            % (
                self.pk,
                user,
                username,
                self.order_id,
                getattr(self, "session_id", ""),
                self.trans_id,
                self.amount,
                self.description,
                self.created,
                self.realized,
                self.pay_type,
                self.status,
                self.error,
            )
        )


@receiver(post_save, sender=UserActionTransaction)
@receiver(post_delete, sender=UserActionTransaction)
def update_user_attendance(sender, instance, *args, **kwargs):
    if not kwargs.get("raw", False):
        mailing.add_or_update_user(instance.user_attendance)


@receiver(post_save, sender=Payment)
def update_mailing_payment(sender, instance, created, **kwargs):
    if instance.user_attendance and kwargs.get("raw", False):
        mailing.add_or_update_user(instance.user_attendance)


@receiver(post_save, sender=Payment)
def assign_vouchers(sender, instance, created, **kwargs):
    if instance.user_attendance and instance.user_attendance.payment_status == "done":
        instance.user_attendance.assign_vouchers()


@receiver(pre_save, sender=Payment)
def payment_set_realized_date(sender, instance, **kwargs):
    if instance.status in Payment.done_statuses and not instance.realized:
        instance.realized = datetime.datetime.now()
