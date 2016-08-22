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

import os

import reportlab
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Image

from svg2rlg import svg2rlg


def make_customer_sheets_pdf(outfile, delivery_batch):
    canvas = Canvas(outfile, pagesize=A4)

    folder = '/usr/share/fonts/truetype/ttf-dejavu'
    reportlab.rl_config.TTFSearchPath.append(folder)
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuB', 'DejaVuSans-Bold.ttf'))

    for package_transaction in delivery_batch.packagetransaction_set.order_by('id'):
        if not package_transaction.user_attendance.team:
            continue
        make_sheet(package_transaction, canvas)
        canvas.showPage()

    canvas.save()


def make_sheet(package_transaction, canvas):
    DIR = os.path.dirname(__file__)
    # CONFIGURATION
    user_attendance = package_transaction.user_attendance
    logo_file = os.path.join(DIR, "static/img/logo.jpg")
    # END OF CONFIGURATION

    # START OF THE DOCUMENT
    im = Image(logo_file, 3.98 * cm, 1.5 * cm)
    im.drawOn(canvas, 2 * cm, 26 * cm)

    barcode = code128.Code128(package_transaction.tnt_con_reference(), barWidth=0.5 * mm, barHeight=20 * mm, humanReadable=True)
    barcode.drawOn(canvas, 8 * cm, 26 * cm)

    canvas.setFont('DejaVuB', 20)
    canvas.drawString(5 * cm, 24 * cm, user_attendance.campaign.__str__())

    canvas.setFont('DejaVuB', 10)
    canvas.drawString(2 * cm, 22 * cm, u"Uživatelské jméno: %s" % user_attendance.userprofile.user.username)

    d = package_transaction.created
    datestr = "%d. %d. %d" % (d.day, d.month, d.year)
    canvas.drawString(13 * cm, 22 * cm, datestr)

    barcode = code128.Code128(package_transaction.tracking_number_cnc(), barWidth=0.5 * mm, barHeight=20 * mm, humanReadable=True)
    barcode.drawOn(canvas, 12 * cm, 19.5 * cm)

    canvas.setFont('DejaVu', 10)
    canvas.drawString(2 * cm, 21 * cm, u"%s, %s" % (user_attendance.team.subsidiary.company, user_attendance.team.subsidiary.address_recipient))
    canvas.drawString(2 * cm, 20.5 * cm, user_attendance.userprofile.user.get_full_name())
    canvas.drawString(2 * cm, 20 * cm, u"%s %s" % (user_attendance.team.subsidiary.address_street, user_attendance.team.subsidiary.address_street_number))
    canvas.drawString(2 * cm, 19.5 * cm, u"%s, %s" % (user_attendance.team.subsidiary.address_psc, user_attendance.team.subsidiary.address_city))

    realized = getattr(user_attendance.representative_payment, 'realized', None)
    if realized:
        canvas.drawString(2 * cm, 18.5 * cm, u"Zaplaceno: %s" % (realized.date()))

    if package_transaction.t_shirt_size:
        canvas.setFont('DejaVuB', 20)
        canvas.drawString(5 * cm, 17 * cm, package_transaction.t_shirt_size.__str__())

        if package_transaction.t_shirt_size.t_shirt_preview:
            svg_tshirt = svg2rlg(package_transaction.t_shirt_size.t_shirt_preview.path)
            svg_tshirt.scale(0.2, 0.2)
            svg_tshirt.drawOn(canvas, 15 * cm, 13 * cm)
