"""
Forms for Contract and Role Management
"""

from django import forms
from .models import Contract, ContractTemplate, Role

class ContractTemplateForm(forms.ModelForm):
    class Meta:
        model = ContractTemplate
        fields = [
            'name', 'template_type', 'description',
            'template_content', 'template_file',
            'is_active', 'requires_signature', 'auto_send',
            'default_delivery_method'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Template Name'}),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'template_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Enter contract template with dynamic tags like {{full_name}}, {{serial_number}}, etc.'
            }),
            'template_file': forms.FileInput(attrs={'class': 'form-control'}),
            'default_delivery_method': forms.Select(attrs={'class': 'form-control'}),
        }

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'labourer', 'template', 'start_date', 'end_date',
            'terms_and_conditions', 'sent_via'
        ]
        widgets = {
            'labourer': forms.Select(attrs={'class': 'form-control'}),
            'template': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'sent_via': forms.Select(attrs={'class': 'form-control'}),
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = [
            'name', 'role_type', 'description', 'project',
            'base_wage', 'overtime_rate', 'work_hours_per_day',
            'requires_certification', 'requires_background_check',
            'minimum_experience_years', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'role_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'base_wage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'overtime_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'work_hours_per_day': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }
