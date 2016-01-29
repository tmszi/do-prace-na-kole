# -*- coding: utf-8 -*-
# Author: Petr Dlouhý <petr.dlouhy@email.cz>
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

from django.conf.urls import url

from . import views
from .forms import AuthenticationFormDPNK
from . import auth
from . import company_admin_views
from .decorators import must_be_in_group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required as login_required_simple
from django.utils.translation import ugettext_lazy as _
import django

urlpatterns = [
    url(r'^tym/$',
        views.ChangeTeamView.as_view(),
        name="zmenit_tym"),
    url(r'^upravit_tym/$',
        views.UpdateTeam.as_view(),
        name="edit_team"),
    url(r'^tym/(?P<token>[0-9A-Za-z]+)/(?P<initial_email>[^&]+)/$$',
        views.ConfirmTeamInvitationView.as_view(),
        name="zmenit_tym"),
    url(r'^registrace/$',
        views.RegistrationView.as_view(),
        {'success_url': 'typ_platby'},
        name="registrace"),
    url(r'^registrace/(?P<token>[0-9A-Za-z]+)/(?P<initial_email>[^&/]+)/$$',
        views.RegistrationView.as_view(),
        {'success_url': 'typ_platby'},
        name="registrace"),
    url(r'^registrace/(?P<initial_email>[^&]+)/$$',
        views.RegistrationView.as_view(),
        {'success_url': 'typ_platby'},
        name="registrace"),
    url(r'^registrace_pristup/$',
        views.RegistrationAccessView.as_view(),
        name="registration_access"
        ),
    url(r'^pozvanky/$',
        views.InviteView.as_view(),
        {'success_url': 'typ_platby'},
        name="pozvanky"),
    url(r'^zaslat_zadost_clenstvi/$',
        views.TeamApprovalRequest.as_view(),
        name="zaslat_zadost_clenstvi",
        ),
    url(r'^$',
        views.ProfileView.as_view(),
        name="profil"),
    url(r'^dalsi_clenove/$',
        views.TeamMembers.as_view(),
        name="team_members",
        ),
    url(r'^dalsi_clenove_vysledky/$',
        views.OtherTeamMembers.as_view(
            template_name='registration/team_members_results.html',
        ),
        name="other_team_members_results",
        ),
    url(r'^jizdy/$',
        views.RidesView.as_view(),
        name="jizdy",
        ),
    url(r'^souteze/$',
        views.AdmissionsView.as_view(
            template_name="registration/competitions.html"
        ),
        name="competitions",
        ),
    url(r'^souteze/pravidla/(?P<city_slug>[^&]+)/$',
        views.CompetitionsView.as_view(
            template_name="registration/competitions_rules.html"
        ),
        name="competition-rules-city",
        ),
    url(r'^vysledky_souteze/(?P<competition_slug>[0-9A-Za-z_\-]+)/$',
        views.CompetitionResultsView.as_view(),
        name="competition_results",
        ),
    url(r'^vysledky_souteze/(?P<competition_slug>[0-9A-Za-z_\-]+)/(?P<limit>[0-9]+)/$',
        views.CompetitionResultsView.as_view(),
        name="competition_results",
        ),
    url(r'^questionnaire_answers/(?P<competition_slug>[0-9A-Za-z_\-]+)/$',
        views.QuestionnaireAnswersAllView.as_view(),
        name="questionnaire_answers_all",
        ),
    url(r'^otazka/(?P<questionnaire_slug>[0-9A-Za-z_\-]+)/$',
        views.QuestionnaireView.as_view(),
        name="questionnaire",
        ),
    url(r'^upravit_profil/$',
        login_required_simple(views.UpdateProfileView.as_view()),
        name="upravit_profil"),
    url(r'^working_schedule/$',
        login_required_simple(views.WorkingScheduleView.as_view()),
        name="working_schedule"),
    url(r'^upravit_trasu/$',
        login_required_simple(views.UpdateTrackView.as_view()),
        name="upravit_trasu"),
    url(r'^zmenit_triko/$',
        views.ChangeTShirtView.as_view(),
        {'success_url': 'typ_platby'},
        name="zmenit_triko"),
    url(r'^typ_platby/$',
        views.PaymentTypeView.as_view(),
        name="typ_platby"),
    url(r'^platba/$',
        views.PaymentView.as_view(),
        name="platba"),
    url(r'^statistika/(?P<variable>[0-9A-Za-z\-]+)/$',
        views.statistics),
    url(r'^denni-graf/$',
        views.daily_chart),
    url(r'^denni-vzdalenost/$',
        views.daily_distance_json),
    url(r'^cykloservis/$',
        login_required(must_be_in_group('cykloservis')(views.BikeRepairView.as_view()))),
    url(r'^package/$',
        views.PackageView.as_view(),
        name="package"),
    url(r'^package-confirmation/$',
        views.ConfirmDeliveryView.as_view(),
        ),
    url(r'^address/$',
        views.UserAttendanceView.as_view(
            template_name="registration/address.html"
        )),
    url(r'^tracks/$',
        views.CombinedTracksKMLView.as_view()
        ),
    url(r'^tracks/(?P<city_slug>[^&]+)/$',
        views.CombinedTracksKMLView.as_view()
        ),
    url(r'^gpx_file/(?P<id>\d+)$',
        views.UpdateGpxFileView.as_view(),
        name="gpx_file",
        ),
    url(r'^gpx_file_create/(?P<date>[^&]+)/(?P<direction>[^&]+)$',
        views.CreateGpxFileView.as_view(),
        name="gpx_file_create",
        ),
    url(r'^emisni_kalkulacka/$',
        views.UserAttendanceView.as_view(
            template_name="registration/emission_calculator.html",
            title=_(u"Emisní kalkulačka"),
        ),
        name="emission_calculator",
        ),


    # company admin:
    url(r'^spolecnost/zadost_admina/$',
        company_admin_views.CompanyAdminView.as_view(),
        name='company_admin_application',
        ),
    url(r'^spolecnost/soutez/(?P<competition_slug>[0-9A-Za-z_\-]+)/$',
        company_admin_views.CompanyCompetitionView.as_view(),
        name="company_admin_competition",
        ),
    url(r'^spolecnost/soutez/$',
        company_admin_views.CompanyCompetitionView.as_view(),
        name="company_admin_competition",
        ),
    url(r'^struktura_spolecnosti/$',
        company_admin_views.CompanyStructure.as_view(),
        name="company_structure",
        ),
    url(r'^spolecnost/souteze/$',
        company_admin_views.CompanyCompetitionsShowView.as_view(),
        name="company_admin_competitions"
        ),
    url(r'^faktury/$',
        company_admin_views.InvoicesView.as_view(),
        name="invoices",
        ),
    url(r'^zaplatit_za_uzivatele/$',
        company_admin_views.SelectUsersPayView.as_view(),
        name='company_admin_pay_for_users',
        ),
    url(r'^spolecnost/editovat_spolecnost/$',
        company_admin_views.CompanyEditView.as_view(),
        name="edit_company",
        ),
    url(r'^spolecnost/registrace_admina/$',
        company_admin_views.CompanyAdminApplicationView.as_view()),
    url(r'^login/(?P<initial_email>[^&]+)/$$',
        views.DPNKLoginView.as_view(
            form_class=AuthenticationFormDPNK,
            template_name='base_generic_form.html',
        ),
        name='login',
        ),
    url(r'^login/$',
        views.DPNKLoginView.as_view(
            form_class=AuthenticationFormDPNK,
            template_name='base_generic_form.html',
        ),
        name='login',
        ),
    url(r'^logout/$',
        django.contrib.auth.views.logout,
        name='logout',
        ),
    url(r'^platba_status$',
        views.payment_status),
    url(r'^platba_uspesna/(?P<trans_id>[0-9]+)/(?P<session_id>[0-9A-Za-z\-]+)/(?P<pay_type>[0-9A-Za-z]+)/$$',
        views.PaymentResult.as_view(),
        {'success': True},
        name="payment_successfull",
        ),
    url(r'^platba_neuspesna/(?P<trans_id>[0-9]*)/(?P<session_id>[0-9A-Za-z\-]+)/(?P<pay_type>[0-9A-Za-z]+)/(?P<error>[^&]+)/$$',
        views.PaymentResult.as_view(),
        {'success': False},
        name="payment_unsuccessfull",
        ),
    url(r'^zapomenute_heslo/$',
        django.contrib.auth.views.password_reset,
        {'password_reset_form': auth.PasswordResetForm},
        name='password_reset',
        ),
    url(r'^zapomenute_heslo/odeslano/$',
        django.contrib.auth.views.password_reset_done,
        name='password_reset_done'),
    url(r'^zapomenute_heslo/zmena/(?P<uidb64>[0-9A-Za-z_]+)-(?P<token>.+)/$',
        django.contrib.auth.views.password_reset_confirm,
        {'set_password_form': auth.SetPasswordForm},
        name='password_reset_confirm'),
    url(r'^zapomenute_heslo/dokonceno/$',
        django.contrib.auth.views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^zmena_hesla/$',
        django.contrib.auth.views.password_change,
        {'password_change_form': auth.PasswordChangeForm},
        name='password_change'),
    url(r'^zmena_hesla_hotovo/$',
        django.contrib.auth.views.password_change_done,
        name='password_change_done'),
]
