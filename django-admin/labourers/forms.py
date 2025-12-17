# labourers/forms.py
from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from .models import (
    Labourer, Project, Role, Supervisor, Contract, 
    IDVerificationLog, CheckIn, AttendanceLog, Task,
    Equipment, CheckOut, DailyAttendanceSummary
)


class LabourerForm(forms.ModelForm):
    # Define choices for designation
    DESIGNATION_CHOICES = [
        ('', 'Select Designation'),
        ('Supervisor', 'Supervisor'),
        ('Foreman', 'Foreman'),
        ('Mason', 'Mason'),
        ('Carpenter', 'Carpenter'),
        ('Plumber', 'Plumber'),
        ('Electrician', 'Electrician'),
        ('Welder', 'Welder'),
        ('Painter', 'Painter'),
        ('General Worker', 'General Worker'),
        ('Machine Operator', 'Machine Operator'),
        ('Driver', 'Driver'),
        ('Security Guard', 'Security Guard'),
        ('Cleaner', 'Cleaner'),
        ('Technician', 'Technician'),
        ('Engineer', 'Engineer'),
        ('Other', 'Other'),
    ]
    
    # Define choices for department
    DEPARTMENT_CHOICES = [
        ('', 'Select Department'),
        ('Construction', 'Construction'),
        ('Electrical', 'Electrical'),
        ('Plumbing', 'Plumbing'),
        ('Carpentry', 'Carpentry'),
        ('Painting', 'Painting'),
        ('Mechanical', 'Mechanical'),
        ('Civil', 'Civil'),
        ('Administration', 'Administration'),
        ('Security', 'Security'),
        ('Maintenance', 'Maintenance'),
        ('Logistics', 'Logistics'),
        ('Operations', 'Operations'),
        ('Other', 'Other'),
    ]
    
    # Override designation and department as ChoiceFields
    designation = forms.ChoiceField(
        choices=DESIGNATION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required'
        }),
        required=True
    )
    
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required'
        }),
        required=True
    )
    
    # Override fields to add custom widgets and validators
    portrait_photo = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Upload a clear front-facing portrait photo'
    )
    
    id_front_photo = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Upload front side of national ID card'
    )
    
    id_back_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Upload back side of national ID card (optional)'
    )
    
    # Custom field for 'sex' if you want to keep it separate from 'gender'
    sex = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Sex"
    )
    
    class Meta:
        model = Labourer
        fields = [
            # Personal Information
            'national_id',
            'full_name',
            'date_of_birth',
            'gender',  # This exists in your model
            'sex',     # Custom field (not in model by default)
            'district_of_birth',
            'id_serial_number',
            
            # Employment Information
            'designation',
            'department', 
            'employment_type',
            'project',
            'role',
            'supervisor',
            
            # Contact Information
            'phone_number',
            'email',
            
            # Photo/Document Fields
            'portrait_photo',
            'id_front_photo',
            'id_back_photo',
            'id_document',
            
            # Status
            'status',
        ]
        widgets = {
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter national ID number',
                'required': 'required'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name',
                'required': 'required'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'district_of_birth': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter district of birth'
            }),
            'id_serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ID serial number'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'project': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254XXXXXXXXX',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'id_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'national_id': 'Unique national identification number',
            'portrait_photo': 'Clear face photo for facial recognition',
            'phone_number': 'Format: +254XXXXXXXXX',
            'id_document': 'Upload ID document (PDF, DOC, or image)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value for sex from gender if instance exists
        if self.instance and self.instance.pk:
            self.fields['sex'].initial = self.instance.gender
    
    def save(self, commit=True):
        # Save sex to gender field before saving
        labourer = super().save(commit=False)
        if 'sex' in self.cleaned_data:
            labourer.gender = self.cleaned_data['sex']
        if commit:
            labourer.save()
        return labourer
    
    def clean_portrait_photo(self):
        portrait = self.cleaned_data.get('portrait_photo')
        if portrait:
            if portrait.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Portrait photo size should not exceed 5MB.')
            if not portrait.name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                raise forms.ValidationError('Only JPG, PNG, and BMP images are allowed.')
        return portrait
    
    def clean_id_front_photo(self):
        id_front = self.cleaned_data.get('id_front_photo')
        if id_front:
            if id_front.size > 3 * 1024 * 1024:  # 3MB limit
                raise forms.ValidationError('ID front image size should not exceed 3MB.')
            if not id_front.name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                raise forms.ValidationError('Only JPG, PNG, and BMP images are allowed.')
        return id_front
    
    def clean_id_back_photo(self):
        id_back = self.cleaned_data.get('id_back_photo')
        if id_back:
            if id_back.size > 3 * 1024 * 1024:  # 3MB limit
                raise forms.ValidationError('ID back image size should not exceed 3MB.')
            if not id_back.name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                raise forms.ValidationError('Only JPG, PNG, and BMP images are allowed.')
        return id_back
    
    def clean_id_document(self):
        id_doc = self.cleaned_data.get('id_document')
        if id_doc:
            if id_doc.size > 10 * 1024 * 1024:  # 10MB limit for documents
                raise forms.ValidationError('ID document size should not exceed 10MB.')
            valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            if not any(id_doc.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    'Only PDF, DOC, DOCX, JPG, PNG files are allowed.'
                )
        return id_doc

# Keep the rest of your forms.py as is...
class ImageUploadForm(forms.Form):
    """Form for uploading images separately"""
    portrait_photo = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Capture or upload a clear face photo'
    )
    
    id_front_photo = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Capture or upload front of ID card'
    )
    
    id_back_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Capture or upload back of ID card (optional)'
    )

class IDScanForm(forms.Form):
    """Form for ID card scanning"""
    scan_image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Scan or take photo of ID card'
    )
    
    scan_type = forms.ChoiceField(
        choices=[('front', 'Front Side'), ('back', 'Back Side')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='front'
    )

class AttendanceCheckinForm(forms.Form):
    """Form for attendance check-in with image capture"""
    labourer_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Labourer ID or scan ID card',
            'autofocus': 'autofocus'
        })
    )
    
    verification_method = forms.ChoiceField(
        choices=[
            ('facial', 'Facial Recognition'),
            ('id_scan', 'ID Card Scan'),
            ('manual', 'Manual Entry')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='id_scan'
    )
    
    captured_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'd-none',
            'accept': 'image/*',
            'capture': 'environment',
            'id': 'captured-image-input'
        })
    )
    
    latitude = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'latitude'})
    )
    
    longitude = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'longitude'})
    )
    
    location_accuracy = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'location-accuracy'})
    )

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'site_identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'auto_checkout_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = ['user', 'project', 'phone_number', 'email', 'is_active']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
              
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users to show only staff users
        self.fields['user'].queryset = User.objects.filter(is_staff=True)