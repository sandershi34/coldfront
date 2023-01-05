import csv
import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import formset_factory
from django.http import HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from coldfront.core.utils.common import Echo
from coldfront.core.grant.forms import GrantDeleteForm, GrantDownloadForm, GrantForm
from coldfront.core.grant.models import (Grant, GrantFundingAgency,
                                         GrantStatusChoice)
from coldfront.core.project.models import Project


class GrantCreateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = GrantForm
    template_name = 'grant/grant_create.html'

    def test_func(self):
        """ UserPassesTestMixin Tests"""
        if self.request.user.is_superuser:
            return True

        project_obj = get_object_or_404(Project, pk=self.kwargs.get('project_pk'))

        if project_obj.pi == self.request.user:
            return True

        if project_obj.projectuser_set.filter(user=self.request.user, role__name='Manager', status__name='Active').exists():
            return True

        messages.error(self.request, 'You do not have permission to add a new grant to this project.')

    def dispatch(self, request, *args, **kwargs):
        project_obj = get_object_or_404(Project, pk=self.kwargs.get('project_pk'))
        if project_obj.status.name not in ['Active', 'New', ]:
            messages.error(request, 'You cannot add grants to an archived project.')
            return HttpResponseRedirect(reverse('project-detail', kwargs={'pk': project_obj.pk}))
        else:
            return super().dispatch(request, *args, **kwargs)
    
    def parse_Currency(self,text):
        text = text.replace(',','')                                  # removes commas

        text = ''.join([c for c in text if c.isdigit() or c == '.']) #removes characters from string

        match = re.search(r'\b\d+\.?\d*\b',text)                     #finds first and last instance of digits and combined with . if exists
        if match:
            return match.group()
        else:
            messages(self.request,"Please Enter a Valid Number")

    def form_valid(self, form):
        form_data = form.cleaned_data
        project_obj = get_object_or_404(Project, pk=self.kwargs.get('project_pk'))
        grant_obj = Grant.objects.create(
            project=project_obj,
            title=form_data.get('title'),
            grant_number=form_data.get('grant_number'),
            role=form_data.get('role'),
            grant_pi_full_name=form_data.get('grant_pi_full_name'),
            funding_agency=form_data.get('funding_agency'),
            other_funding_agency=form_data.get('other_funding_agency'),
            other_award_number=form_data.get('other_award_number'),
            grant_start=form_data.get('grant_start'),
            grant_end=form_data.get('grant_end'),
            percent_credit=form_data.get('percent_credit'),
            direct_funding=form_data.get('direct_funding'),
            total_amount_awarded='$'+self.parse_Currency(form_data.get('total_amount_awarded')),
            status=form_data.get('status'),
        )

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs.get('project_pk'))
        return context

    def get_success_url(self):
        messages.success(self.request, 'Added a grant.')
        return reverse('project-detail', kwargs={'pk': self.kwargs.get('project_pk')})


class GrantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        """ UserPassesTestMixin Tests"""
        if self.request.user.is_superuser:
            return True

        grant_obj = get_object_or_404(Grant, pk=self.kwargs.get('pk'))

        if grant_obj.project.pi == self.request.user:
            return True

        if grant_obj.project.projectuser_set.filter(user=self.request.user, role__name='Manager', status__name='Active').exists():
            return True

        messages.error(self.request, 'You do not have permission to update grant from this project.')

    model = Grant
    template_name_suffix = '_update_form'
    fields = ['title', 'grant_number', 'role', 'grant_pi_full_name', 'funding_agency', 'other_funding_agency',
              'other_award_number', 'grant_start', 'grant_end', 'percent_credit', 'direct_funding', 'total_amount_awarded', 'status', ]

    def get_success_url(self):
        return reverse('project-detail', kwargs={'pk': self.object.project.id})


class GrantDeleteGrantsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'grant/grant_delete_grants.html'

    def test_func(self):
        """ UserPassesTestMixin Tests"""
        if self.request.user.is_superuser:
            return True

        project_obj = get_object_or_404(Project, pk=self.kwargs.get('project_pk'))

        if project_obj.pi == self.request.user:
            return True

        if project_obj.projectuser_set.filter(user=self.request.user, role__name='Manager', status__name='Active').exists():
            return True

        messages.error(self.request, 'You do not have permission to delete grants from this project.')

    def get_grants_to_delete(self, project_obj):

        grants_to_delete = [

            {'title': grant.title,
             'grant_number': grant.grant_number,
             'grant_end': grant.grant_end}

            for grant in project_obj.grant_set.all()
        ]

        return grants_to_delete

    def get(self, request, *args, **kwargs):
        project_obj = get_object_or_404(Project, pk=self.kwargs.get('project_pk'))

        grants_to_delete = self.get_grants_to_delete(project_obj)
        context = {}

        if grants_to_delete:
            formset = formset_factory(GrantDeleteForm, max_num=len(grants_to_delete))
            formset = formset(initial=grants_to_delete, prefix='grantform')
            context['formset'] = formset

        context['project'] = project_obj
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        project_obj = get_object_or_404(Project, pk=self.kwargs.get('project_pk'))

        grants_to_delete = self.get_grants_to_delete(project_obj)
        context = {}

        formset = formset_factory(GrantDeleteForm, max_num=len(grants_to_delete))
        formset = formset(request.POST, initial=grants_to_delete, prefix='grantform')

        grants_deleted_count = 0

        if formset.is_valid():
            for form in formset:
                grant_form_data = form.cleaned_data
                if grant_form_data['selected']:

                    grant_obj = Grant.objects.get(
                        project=project_obj,
                        title=grant_form_data.get('title'),
                        grant_number=grant_form_data.get('grant_number')
                    )
                    grant_obj.delete()
                    grants_deleted_count += 1

            messages.success(request, 'Deleted {} grants from project.'.format(grants_deleted_count))
        else:
            for error in formset.errors:
                messages.error(request, error)

        return HttpResponseRedirect(reverse('project-detail', kwargs={'pk': project_obj.pk}))

    def get_success_url(self):
        return reverse('project-detail', kwargs={'pk': self.object.project.id})


class GrantReportView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'grant/grant_report_list.html'

    def test_func(self):
        """ UserPassesTestMixin Tests"""
        if self.request.user.is_superuser:
            return True

        if self.request.user.has_perm('grant.can_view_all_grants'):
            return True

        messages.error(self.request, 'You do not have permission to view all grants.')


    def get_grants(self):
        grants = Grant.objects.prefetch_related(
            'project', 'project__pi').all().order_by('-total_amount_awarded')
        grants= [

            {'pk': grant.pk,
            'title': grant.title,
            'project_pk': grant.project.pk,
            'pi_first_name': grant.project.pi.first_name,
            'pi_last_name':grant.project.pi.last_name,
            'role': grant.role,
            'grant_pi': grant.grant_pi,
            'total_amount_awarded': grant.total_amount_awarded,
            'funding_agency': grant.funding_agency,
            'grant_number': grant.grant_number,
            'grant_start': grant.grant_start,
            'grant_end': grant.grant_end,
            'percent_credit': grant.percent_credit,
            'direct_funding': grant.direct_funding,
            }
            for grant in grants
        ]

        return grants


    def get(self, request, *args, **kwargs):
        context = {}
        grants = self.get_grants()

        if grants:
            formset = formset_factory(GrantDownloadForm, max_num=len(grants))
            formset = formset(initial=grants, prefix='grantdownloadform')
            context['formset'] = formset
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        grants = self.get_grants()

        formset = formset_factory(GrantDownloadForm, max_num=len(grants))
        formset = formset(request.POST, initial=grants, prefix='grantdownloadform')

        header = [
            'Grant Title',
            'Project PI',
            'Faculty Role',
            'Grant PI',
            'Total Amount Awarded',
            'Funding Agency',
            'Grant Number',
            'Start Date',
            'End Date',
            'Percent Credit',
            'Direct Funding',
        ]
        rows = []
        grants_selected_count = 0

        if formset.is_valid():
            for form in formset:
                form_data = form.cleaned_data
                if form_data['selected']:
                    grant = get_object_or_404(Grant, pk=form_data['pk'])

                    row = [
                        grant.title,
                        ' '.join((grant.project.pi.first_name, grant.project.pi.last_name)),
                        grant.role,
                        grant.grant_pi_full_name,
                        grant.total_amount_awarded,
                        grant.funding_agency,
                        grant.grant_number,
                        grant.grant_start,
                        grant.grant_end,
                        grant.percent_credit,
                        grant.direct_funding,
                    ]

                    rows.append(row)
                    grants_selected_count += 1

            if grants_selected_count == 0:
                grants = Grant.objects.prefetch_related('project', 'project__pi').all().order_by('-total_amount_awarded')
                for grant in grants:
                    row = [
                        grant.title,
                        ' '.join((grant.project.pi.first_name, grant.project.pi.last_name)),
                        grant.role,
                        grant.grant_pi_full_name,
                        grant.total_amount_awarded,
                        grant.funding_agency,
                        grant.grant_number,
                        grant.grant_start,
                        grant.grant_end,
                        grant.percent_credit,
                        grant.direct_funding,
                    ]
                    rows.append(row)

            rows.insert(0, header)
            pseudo_buffer = Echo()
            writer = csv.writer(pseudo_buffer)
            response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                            content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename="grants.csv"'
            return response
        else:
            for error in formset.errors:
                messages.error(request, error)
            return HttpResponseRedirect(reverse('grant-report'))


class GrantDownloadView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "/"

    def test_func(self):
        """ UserPassesTestMixin Tests"""
        if self.request.user.is_superuser:
            return True

        if self.request.user.has_perm('grant.can_view_all_grants'):
            return True

        messages.error(self.request, 'You do not have permission to download all grants.')

    def get(self, request):

        header = [
            'Grant Title',
            'Project PI',
            'Faculty Role',
            'Grant PI',
            'Total Amount Awarded',
            'Funding Agency',
            'Grant Number',
            'Start Date',
            'End Date',
            'Percent Credit',
            'Direct Funding',
        ]

        rows = []
        grants = Grant.objects.prefetch_related('project', 'project__pi').all().order_by('-total_amount_awarded')
        for grant in grants:
            row = [
                grant.title,
                ' '.join((grant.project.pi.first_name, grant.project.pi.last_name)),
                grant.role,
                grant.grant_pi_full_name,
                grant.total_amount_awarded,
                grant.funding_agency,
                grant.grant_number,
                grant.grant_start,
                grant.grant_end,
                grant.percent_credit,
                grant.direct_funding,
            ]

            rows.append(row)
        rows.insert(0, header)
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="grants.csv"'
        return response
