import json
import base64
import numpy as np
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User  # KEEP THIS - Django's built-in User
import uuid
from django.core.validators import RegexValidator
import os
from django.core.validators import FileExtensionValidator
from django.db import models
import base64
import io
from PIL import Image
import hashlib
class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    site_identifier = models.CharField(max_length=50, unique=True)
    company_email = models.EmailField()
    company_phone = models.CharField(max_length=20)
    
    # Geofencing fields - MUST be nullable
    boundary_coordinates = models.JSONField(
        default=list,
        null=True,      # IMPORTANT
        blank=True,     # IMPORTANT
        help_text="Store as: [[lat1,lng1], [lat2,lng2], ...]"
    )
    entry_points = models.JSONField(
        default=list, 
        null=True,      # IMPORTANT
        blank=True,     # IMPORTANT
        help_text="Store as: [[lat,lng], [lat,lng], ...]"
    )
    
    # Operating hours
    operating_hours = models.JSONField(default=list, help_text="[{'day': 'Monday', 'start': '08:00', 'end': '17:00'}]")
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    
    # Configuration
    auto_checkout_time = models.TimeField(default='20:00')
    overtime_threshold = models.IntegerField(default=8, help_text="Hours after which overtime applies")
    overtime_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.5)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.site_identifier})"

class Role(models.Model):
    ROLE_TYPES = [
        ('SUPERVISOR', 'Supervisor'),
        ('FOREMAN', 'Foreman'),
        ('SKILLED', 'Skilled Worker'),
        ('SEMI_SKILLED', 'Semi-Skilled Worker'),
        ('UNSKILLED', 'Unskilled Worker'),
        ('OPERATOR', 'Machine Operator'),
        ('TECHNICIAN', 'Technician'),
        ('DRIVER', 'Driver'),
        ('SECURITY', 'Security Guard'),
        ('CLEANER', 'Cleaner'),
        ('CUSTOM', 'Custom Role'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES, default='CUSTOM')
    description = models.TextField(blank=True)
    
    # Wage structure
    base_wage = models.DecimalField(max_digits=10, decimal_places=2)
    overtime_rate = models.DecimalField(max_digits=10, decimal_places=2)
    work_hours_per_day = models.IntegerField(default=8)
    
    # Permissions - Expanded
    permissions = models.JSONField(default=dict, help_text="{'can_approve_timesheets': false, 'can_manage_equipment': false, 'can_create_tasks': false, 'can_view_reports': false, 'access_level': 1}")
    
    # Role Settings
    requires_certification = models.BooleanField(default=False)
    requires_background_check = models.BooleanField(default=False)
    minimum_experience_years = models.IntegerField(default=0)
    
    # Active Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        unique_together = ['project', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"

class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')  # USING Django User
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='supervisors')
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    
    # Substitution protocol
    substitute_supervisors = models.ManyToManyField('self', blank=True, symmetrical=False)
    approval_hierarchy = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.name}"
class Labourer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
        ('TERMINATED', 'Terminated'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('CASUAL', 'Casual'),
        ('TEMPORARY', 'Temporary'),
    ]
    
    # Basic Information
    labourer_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    serial_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Auto-generated unique employee ID")
    
    # Identity Information (from ID card)
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    district_of_birth = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=20, unique=True)
    id_serial_number = models.CharField(max_length=50, blank=True, null=True) 
    
    # Employment Information
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='CONTRACT'
        # Removed: blank=True, null=True
    )
    
    # Contact Information - FIXED regex pattern
    phone_regex = RegexValidator(
        regex=r'^\+254[17]\d{8}$', 
        message="Phone number must be in format: +254XXXXXXXXX"
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=13, 
        unique=True
    )
    email = models.EmailField(blank=True)
    
    # ... rest of your model remains the same ...
    # Employment Information project = models.ForeignKey(
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='labourers')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='labourers')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, related_name='labourers')
    
    # Biometric Data
    portrait_photo = models.ImageField(upload_to='portraits/')

    facial_encoding = models.BinaryField(null=True, blank=True)  # Store facial embeddings
    id_front_photo = models.ImageField(upload_to='id_documents/')
    id_back_photo = models.ImageField(upload_to='id_documents/')
    
    # ID Document (PDF/DOC upload)
    id_document = models.FileField(
        upload_to='id_documents/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )
    
    # System Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    whitelisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    id_scan_quality_score = models.FloatField(null=True, blank=True)  # OCR quality score
    facial_recognition_confidence = models.FloatField(null=True, blank=True)
    portrait_image = models.ImageField(upload_to='portraits/', null=True, blank=True)
    portrait_hash = models.CharField(max_length=64, blank=True)  # Store image hash
    
    def save(self, *args, **kwargs):
        # Generate serial number if not exists
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        
        # Generate hash when portrait is saved
        if self.portrait_image:
            self.portrait_hash = self.generate_image_hash()
        super().save(*args, **kwargs)
    
    def generate_serial_number(self):
        """Generate unique employee ID in format: EMP-YYYY-XXXXX"""
        from datetime import datetime
        year = datetime.now().year
        
        # Get last serial number for this year
        last_labourer = Labourer.objects.filter(
            serial_number__startswith=f'EMP-{year}'
        ).order_by('-serial_number').first()
        
        if last_labourer and last_labourer.serial_number:
            try:
                last_num = int(last_labourer.serial_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        return f'EMP-{year}-{new_num:05d}'
    
    def generate_image_hash(self):
        """Generate hash from portrait image"""
        try:
            with Image.open(self.portrait_image.path) as img:
                # Resize to standard size
                img = img.resize((200, 200))
                # Convert to grayscale
                img = img.convert('L')
                # Get pixel data
                pixels = list(img.getdata())
                # Create hash
                pixel_str = ''.join(str(p) for p in pixels)
                return hashlib.sha256(pixel_str.encode()).hexdigest()
        except:
            return ''
    
    def get_portrait_base64(self):
        """Get portrait as base64"""
        if self.portrait_image:
            with open(self.portrait_image.path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return ''

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['national_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.serial_number})"

class IDVerificationLog(models.Model):
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='verification_logs')
    verification_type = models.CharField(max_length=50, choices=[
        ('INITIAL', 'Initial Registration'),
        ('DAILY', 'Daily Verification'),
        ('REVERIFICATION', 'Re-verification'),
    ])
    verification_time = models.DateTimeField(auto_now_add=True)
    verification_method = models.CharField(max_length=50, choices=[
        ('FACIAL', 'Facial Recognition'),
        ('ID_SCAN', 'ID Card Scan'),
        ('MANUAL', 'Manual Verification'),
    ])
    
    # Location data
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_address = models.TextField(null=True, blank=True)
    
    # Verification results
    facial_match_score = models.FloatField(null=True, blank=True)
    id_match_score = models.FloatField(null=True, blank=True)
    overall_confidence = models.FloatField(null=True, blank=True)
    is_successful = models.BooleanField(default=False)
    
    # Device info
    device_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Verification agent - CHANGED FROM admin_auth.AdminUser to User
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-verification_time']
    
    def __str__(self):
        return f"Verification for {self.labourer.full_name} at {self.verification_time}"
    
    @property
    def location(self):
        """Return location as tuple if coordinates exist"""
        if self.location_lat and self.location_lng:
            return (float(self.location_lat), float(self.location_lng))
        return None
    
    @location.setter
    def location(self, value):
        """Set location from tuple or list"""
        if isinstance(value, (tuple, list)) and len(value) == 2:
            self.location_lat, self.location_lng = value

class Contract(models.Model):
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='contracts')
    template = models.ForeignKey('ContractTemplate', on_delete=models.SET_NULL, null=True)
    
    # Contract Details
    contract_number = models.CharField(max_length=50, unique=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Generated Content
    terms_and_conditions = models.TextField(help_text="Auto-generated from template")
    generated_content = models.TextField(blank=True, help_text="Full contract with replaced tags")
    generated_pdf = models.FileField(upload_to='contracts/generated/', null=True, blank=True)
    
    # Digital Signature
    signature_image = models.ImageField(upload_to='signatures/', null=True, blank=True)
    signature_data = models.TextField(blank=True, help_text="Base64 signature data")
    signature_timestamp = models.DateTimeField(null=True, blank=True)
    signature_ip = models.GenericIPAddressField(null=True, blank=True)
    signature_device = models.CharField(max_length=200, blank=True)
    signature_verified = models.BooleanField(default=False)
    
    # Delivery & Communication
    sent_via = models.CharField(
        max_length=50,
        choices=[('EMAIL', 'Email'), ('SMS', 'SMS'), ('WHATSAPP', 'WhatsApp'), ('MANUAL', 'Manual')],
        default='EMAIL'
    )
    sent_to = models.CharField(max_length=200, blank=True, help_text="Email/Phone where sent")
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=50, blank=True)
    
    # Acknowledgment
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledgment_method = models.CharField(max_length=50, blank=True)
    acknowledgment_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'Draft'),
        ('GENERATED', 'Generated'),
        ('SENT', 'Sent'),
        ('VIEWED', 'Viewed'),
        ('SIGNED', 'Signed'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('TERMINATED', 'Terminated'),
    ], default='DRAFT')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contracts')
    
    # Audit Trail
    audit_log = models.JSONField(default=list, help_text="Track all contract actions")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contract_number']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Contract {self.contract_number} - {self.labourer.full_name}"
    
    def add_to_audit_log(self, action, user=None, details=''):
        """Add entry to audit trail"""
        from django.utils import timezone
        entry = {
            'timestamp': timezone.now().isoformat(),
            'action': action,
            'user': user.username if user else 'System',
            'details': details
        }
        if not isinstance(self.audit_log, list):
            self.audit_log = []
        self.audit_log.append(entry)
        self.save(update_fields=['audit_log'])
    
    def generate_contract_number(self):
        """Auto-generate unique contract number"""
        from datetime import datetime
        if not self.contract_number:
            year = datetime.now().year
            # Get last contract number for this year
            last_contract = Contract.objects.filter(
                contract_number__startswith=f'CNT-{year}'
            ).order_by('-contract_number').first()
            
            if last_contract:
                last_num = int(last_contract.contract_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.contract_number = f'CNT-{year}-{new_num:05d}'
        return self.contract_number

class ContractTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('EMPLOYMENT', 'Employment Contract'),
        ('NDA', 'Non-Disclosure Agreement'),
        ('SAFETY', 'Safety Agreement'),
        ('TERMINATION', 'Termination Letter'),
        ('CUSTOM', 'Custom Document'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='EMPLOYMENT')
    description = models.TextField(blank=True)
    
    # Template Content
    template_content = models.TextField(help_text="Use tags: {{full_name}}, {{serial_number}}, {{national_id}}, {{phone_number}}, {{email}}, {{designation}}, {{role}}, {{project}}, {{start_date}}, {{end_date}}, {{base_rate}}, {{contract_number}}, {{current_date}}")
    template_file = models.FileField(
        upload_to='contract_templates/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['docx', 'pdf', 'html'])],
        help_text="Upload Word/PDF template with dynamic tags"
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    requires_signature = models.BooleanField(default=True)
    auto_send = models.BooleanField(default=False)
    default_delivery_method = models.CharField(
        max_length=20,
        choices=[('EMAIL', 'Email'), ('SMS', 'SMS'), ('WHATSAPP', 'WhatsApp'), ('MANUAL', 'Manual')],
        default='EMAIL'
    )
    
    # Metadata
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_templates')
    
    # Available Tags Documentation
    available_tags = models.JSONField(default=dict, editable=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    def get_available_tags(self):
        """Return all available template tags"""
        return {
            '{{full_name}}': 'Labourer full name',
            '{{serial_number}}': 'Employee ID',
            '{{national_id}}': 'National ID number',
            '{{phone_number}}': 'Phone number',
            '{{email}}': 'Email address',
            '{{designation}}': 'Job designation',
            '{{role}}': 'Role name',
            '{{project}}': 'Project name',
            '{{project_location}}': 'Project location',
            '{{start_date}}': 'Contract start date',
            '{{end_date}}': 'Contract end date',
            '{{base_rate}}': 'Base pay rate',
            '{{contract_number}}': 'Contract number',
            '{{current_date}}': 'Current date',
            '{{company_name}}': 'Company name',
        }
    
    def save(self, *args, **kwargs):
        self.available_tags = self.get_available_tags()
        super().save(*args, **kwargs)

class CheckIn(models.Model):
    CHECKIN_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('OVERRIDE', 'Manual Override'),
    ]
    
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='checkins')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    # Verification Data
    facial_recognition_photo = models.ImageField(upload_to='attendance/checkin/', null=True, blank=True)
    facial_match_confidence = models.FloatField(null=True, blank=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # System Validation
    within_geofence = models.BooleanField(default=True)
    whitelist_valid = models.BooleanField(default=True)
    within_operating_hours = models.BooleanField(default=True)
    
    # Result
    status = models.CharField(max_length=20, choices=CHECKIN_STATUS)
    access_granted = models.BooleanField(default=False)
    
    # Security/Override Information
    security_guard = models.ForeignKey('SecurityGuard', on_delete=models.SET_NULL, null=True, blank=True)
    override_reason = models.TextField(blank=True)
    override_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # CHANGED
    
    # Device Information
    device_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['labourer', 'timestamp']),
            models.Index(fields=['status', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.labourer.full_name} - {self.timestamp} - {self.status}"

class CheckInDenial(models.Model):
    checkin_attempt = models.OneToOneField(CheckIn, on_delete=models.CASCADE, related_name='denial')
    reason = models.CharField(max_length=100, choices=[
        ('FACE_MISMATCH', 'Facial Recognition Failed'),
        ('NOT_WHITELISTED', 'Not Whitelisted'),
        ('OUTSIDE_GEOFENCE', 'Outside Geofence'),
        ('OUTSIDE_HOURS', 'Outside Operating Hours'),
        ('SYSTEM_ERROR', 'System Error'),
    ])
    details = models.TextField(blank=True)
    
    # Notification
    supervisor_notified = models.BooleanField(default=False)
    supervisor_notified_at = models.DateTimeField(null=True, blank=True)
    supervisor_acknowledged = models.BooleanField(default=False)
    supervisor_acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Lock Status
    system_lock_active = models.BooleanField(default=True)
    lock_released_at = models.DateTimeField(null=True, blank=True)
    lock_released_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # CHANGED
    
    # Resolution
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Denial for {self.checkin_attempt.labourer.full_name} - {self.reason}"

class SecurityGuard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_guard_profile')  # USING Django User
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='security_guards')
    badge_number = models.CharField(max_length=50, unique=True)
    can_override = models.BooleanField(default=False)
    override_limit = models.IntegerField(default=3)
    
    # Shift Information
    current_shift_start = models.DateTimeField(null=True, blank=True)
    current_shift_end = models.DateTimeField(null=True, blank=True)
    entry_point_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    entry_point_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    entry_point_name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.badge_number}"

class AttendanceLog(models.Model):
    LOG_TYPES = [
        ('Check-In', 'Check-In'),
        ('Check-Out', 'Check-Out'),
        ('Forced-Check-Out', 'Forced-Check-Out'),
    ]
    
    VERIFICATION_METHOD = [
        ('Facial', 'Facial Recognition'),
        ('ID_Scan', 'ID Card Scan'),
        ('Manual', 'Manual Entry'),
        ('QR', 'QR Code'),
        ('Location', 'Location Verified'),
    ]
    
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='attendance_logs')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    log_timestamp = models.DateTimeField(auto_now_add=True)
    verification_method = models.CharField(max_length=20, choices=VERIFICATION_METHOD, default='Manual')
    
    # Geolocation data
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_accuracy = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="GPS accuracy in meters"
    )
    
    # Location verification status
    location_verified = models.BooleanField(
        default=False,
        help_text="Was the location verified to be within site?"
    )
    location_verification_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When location was verified"
    )
    
    # Image capture for attendance
    def get_attendance_image_upload_path(instance, filename):
        date_str = instance.log_timestamp.date() if instance.log_timestamp else 'unknown'
        return f'attendance/{instance.labourer.national_id}/{date_str}/{filename}'
    
    captured_image = models.ImageField(
        upload_to=get_attendance_image_upload_path,
        null=True,
        blank=True,
        verbose_name='Captured Attendance Image'
    )
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, default="Main Gate")
    
    # Verification fields
    verification_photo = models.ImageField(upload_to='verification_photos/', null=True, blank=True)
    verification_hash = models.CharField(max_length=64, blank=True)
    similarity_score = models.FloatField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    
    @property
    def status(self):
        if self.check_in_time and not self.check_out_time:
            return "Checked In"
        elif self.check_in_time and self.check_out_time:
            return "Checked Out"
        return "Not Checked In"
    # Verification scores
    facial_recognition_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    id_verification_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overall_confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Verification flags
    whitelist_verified = models.BooleanField(default=False)
    geofence_verified = models.BooleanField(
        default=False,
        help_text="Verified to be within site geofence"
    )
    biometric_verified = models.BooleanField(default=False)
    
    # Supervisor verification
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True)
    supervisor_verified = models.BooleanField(default=False)
    supervisor_verification_time = models.DateTimeField(null=True, blank=True)
    
    # Security verification
    security_verified = models.BooleanField(default=False)
    security_verification_time = models.DateTimeField(null=True, blank=True)
    
    # Overtime
    overtime_minutes = models.IntegerField(default=0)
    overtime_approved = models.BooleanField(default=False)
    overtime_remarks = models.TextField(null=True, blank=True)
    
    # Access control
    access_granted = models.BooleanField(default=True)
    denial_reason = models.TextField(null=True, blank=True)
    supervisor_acknowledged = models.BooleanField(default=False)
    supervisor_acknowledgment_time = models.DateTimeField(null=True, blank=True)
    
    # Device and session info
    device_id = models.CharField(max_length=255, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='attendance_photos/', null=True, blank=True)
    has_photo = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['log_timestamp']),
            models.Index(fields=['labourer', 'log_timestamp']),
            models.Index(fields=['access_granted']),
            models.Index(fields=['verification_method']),
            models.Index(fields=['log_type']),
            models.Index(fields=['location_verified']),
            models.Index(fields=['geofence_verified']),
        ]
        ordering = ['-log_timestamp']
        verbose_name = 'Attendance Log'
        verbose_name_plural = 'Attendance Logs'
    
    def __str__(self):
        return f"{self.log_type} - {self.labourer.full_name} at {self.log_timestamp}"
    
    def verify_location(self, user_lat, user_lng):
        """Verify if attendance location is within project site"""
        if not self.labourer.project:
            return False, "Labourer not assigned to any project"
        
        # You need to implement this method in Project model
        # is_within_site = self.labourer.project.is_location_within_site(user_lat, user_lng)
        is_within_site = False  # Placeholder
        
        if is_within_site:
            self.location_verified = True
            self.geofence_verified = True
            self.verification_method = 'Location'
            self.save()
            
        return is_within_site, f"{'Within' if is_within_site else 'Outside'} site"
    
    def is_within_operating_hours(self):
        """Check if attendance is within project operating hours"""
        if self.labourer.project:
            # You need to implement this method in Project model
            # return self.labourer.project.is_within_operating_hours()
            return True
        return True
    
    @property
    def location_status(self):
        """Get human-readable location status"""
        if self.location_verified:
            return "📍 Within site"
        elif self.latitude and self.longitude:
            return "📍 Location recorded (not verified)"
        else:
            return "📍 No location data"
    
    @property
    def is_late_checkin(self):
        """Check if check-in is late (after 8 AM)"""
        if self.log_type == 'Check-In' and self.log_timestamp:
            from datetime import time
            checkin_time = self.log_timestamp.time()
            return checkin_time > time(8, 0, 0)
        return False
    
    @property
    def image_url(self):
        """Get the URL for the captured image"""
        if self.captured_image:
            return self.captured_image.url
        return None

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Scheduling
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)
    deadline = models.DateTimeField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(Labourer, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    # Progress Tracking
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_updated = models.DateTimeField(auto_now=True)
    
    # Equipment
    required_equipment = models.JSONField(default=list, help_text="List of equipment IDs/names")
    
    # Quality Control
    quality_check_passed = models.BooleanField(default=False)
    quality_check_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-deadline', 'priority']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='task_assignments')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, related_name='task_assignments')
    
    # Assignment details
    assigned_date = models.DateField(auto_now_add=True)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    
    # Work details
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Completion
    completed_date = models.DateField(null=True, blank=True)
    completion_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # CHANGED
    
    # Quality metrics
    quality_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    quality_feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['task', 'labourer']
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.labourer.full_name} - {self.task.title}"

class TaskProgressLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='progress_logs')
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='task_logs')
    
    # Progress Update
    update_type = models.CharField(max_length=50, choices=[
        ('STARTED', 'Task Started'),
        ('PROGRESS', 'Progress Update'),
        ('MILESTONE', 'Milestone Reached'),
        ('ISSUE', 'Issue Encountered'),
        ('COMPLETED', 'Task Completed'),
    ])
    description = models.TextField()
    progress_percentage = models.IntegerField()
    hours_spent = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Media Evidence (optional)
    photo_evidence = models.ImageField(upload_to='task_evidence/', null=True, blank=True)
    notes = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.task.title} - {self.update_type} at {self.timestamp}"

class Equipment(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('IN_USE', 'In Use'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('DAMAGED', 'Damaged'),
        ('LOST', 'Lost'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=200)
    equipment_id = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    # Assignment
    current_assignment = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_equipment')
    assigned_to = models.ForeignKey(Labourer, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment')
    assigned_at = models.DateTimeField(null=True, blank=True)
    expected_return = models.DateTimeField(null=True, blank=True)
    
    # Maintenance
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    maintenance_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.equipment_id}) - {self.status}"

class EquipmentAssignment(models.Model):
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('IN_USE', 'In Use'),
        ('RETURNED', 'Returned'),
        ('DAMAGED', 'Damaged'),
        ('LOST', 'Lost'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='assignments')
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='equipment_assignments')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, related_name='equipment_assignments')
    
    # Assignment details
    assigned_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    
    # Usage tracking
    condition_before = models.TextField(help_text="Condition before assignment")
    condition_after = models.TextField(null=True, blank=True, help_text="Condition after return")
    
    # Authorization
    authorized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # CHANGED
    notes = models.TextField(blank=True)
    
    # Charges/damages
    damage_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damage_assessed = models.BooleanField(default=False)
    damage_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.equipment.name} assigned to {self.labourer.full_name}"

class CheckOut(models.Model):
    CHECKOUT_TYPE = [
        ('NORMAL', 'Normal Checkout'),
        ('OVERTIME', 'Overtime Checkout'),
        ('EARLY', 'Early Checkout'),
        ('FORCED', 'System Forced Checkout'),
    ]
    
    STAGE_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ESCALATED', 'Escalated'),
    ]
    
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='checkouts')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    # Stage 1: Supervisor Checkout
    supervisor_checkout = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, related_name='approved_checkouts')
    supervisor_checkout_time = models.DateTimeField(null=True, blank=True)
    supervisor_verification_photo = models.ImageField(upload_to='attendance/checkout/supervisor/', null=True, blank=True)
    supervisor_status = models.CharField(max_length=20, choices=STAGE_STATUS, default='PENDING')
    supervisor_notes = models.TextField(blank=True)
    
    # Stage 2: Security Checkout
    security_checkout = models.ForeignKey(SecurityGuard, on_delete=models.SET_NULL, null=True, related_name='processed_checkouts')
    security_checkout_time = models.DateTimeField(null=True, blank=True)
    security_verification_photo = models.ImageField(upload_to='attendance/checkout/security/', null=True, blank=True)
    security_status = models.CharField(max_length=20, choices=STAGE_STATUS, default='PENDING')
    security_notes = models.TextField(blank=True)
    
    # Overtime Information
    has_overtime = models.BooleanField(default=False)
    overtime_minutes = models.IntegerField(default=0)
    overtime_approved = models.BooleanField(default=False)
    overtime_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='overtime_approvals')  # CHANGED
    overtime_approval_time = models.DateTimeField(null=True, blank=True)
    overtime_remarks = models.TextField(blank=True)
    
    # Final Details
    checkout_type = models.CharField(max_length=20, choices=CHECKOUT_TYPE, default='NORMAL')
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    checkout_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    checkout_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Equipment Check
    equipment_returned = models.BooleanField(default=True)
    equipment_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"Checkout for {self.labourer.full_name} - {self.checkout_type}"

class DailyAttendanceSummary(models.Model):
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='daily_summaries')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Time Tracking
    checkin_time = models.DateTimeField()
    checkout_time = models.DateTimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    regular_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Task Summary
    tasks_completed = models.IntegerField(default=0)
    tasks_pending = models.IntegerField(default=0)
    productivity_score = models.FloatField(null=True, blank=True)
    
    # Earnings
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    attendance_status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late Arrival'),
        ('EARLY_LEAVE', 'Early Leave'),
        ('HALF_DAY', 'Half Day'),
    ])
    
    # Flags
    has_exceptions = models.BooleanField(default=False)
    exceptions = models.JSONField(default=list)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # CHANGED
    
    class Meta:
        unique_together = ['labourer', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.labourer.full_name} - {self.date} - {self.attendance_status}"

class ReportTemplate(models.Model):
    REPORT_TYPES = [
        ('DAILY_ATTENDANCE', 'Daily Attendance'),
        ('WEEKLY_SUMMARY', 'Weekly Summary'),
        ('MONTHLY_PAYROLL', 'Monthly Payroll'),
        ('PRODUCTIVITY', 'Productivity Analysis'),
        ('EXCEPTION', 'Exception Report'),
        ('COMPLIANCE', 'Compliance Report'),
    ]
    
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    template_file = models.FileField(upload_to='report_templates/', null=True, blank=True)
    format = models.CharField(max_length=20, choices=[('PDF', 'PDF'), ('EXCEL', 'Excel'), ('CSV', 'CSV')], default='PDF')
    parameters = models.JSONField(default=dict)
    schedule = models.CharField(max_length=50, blank=True, help_text="Cron expression for automated generation")
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

class GeneratedReport(models.Model):
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='generated_reports')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    
    # Generation details
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # CHANGED
    
    # Report data
    period_start = models.DateField()
    period_end = models.DateField()
    parameters_used = models.JSONField(default=dict)
    
    # File storage
    report_file = models.FileField(upload_to='generated_reports/')
    file_size = models.IntegerField()
    checksum = models.CharField(max_length=64, blank=True)
    
    # Distribution
    emailed_to = models.JSONField(default=list, help_text="List of email addresses")
    downloaded_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.period_start} to {self.period_end}"

class DailyClosureLog(models.Model):
    closure_date = models.DateField(unique=True)
    closure_time = models.TimeField()
    total_labourers_checked_in = models.IntegerField(default=0)
    total_labourers_checked_out = models.IntegerField(default=0)
    forced_checkouts = models.IntegerField(default=0)
    exceptions_count = models.IntegerField(default=0)
    processed_by_system = models.BooleanField(default=True)
    processed_timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Daily Closure - {self.closure_date}"

class ExceptionReport(models.Model):
    EXCEPTION_TYPES = [
        ('Late Check-In', 'Late Check-In'),
        ('Missed Check-Out', 'Missed Check-Out'),
        ('Access Denied', 'Access Denied'),
        ('Overtime Violation', 'Overtime Violation'),
        ('Equipment Not Returned', 'Equipment Not Returned'),
    ]
    
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    labourer = models.ForeignKey(Labourer, on_delete=models.CASCADE, related_name='exceptions')
    exception_date = models.DateField()
    exception_type = models.CharField(max_length=50, choices=EXCEPTION_TYPES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(null=True, blank=True)
    resolved_by = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_timestamp = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-exception_date']
    
    def __str__(self):
        return f"{self.labourer.full_name} - {self.exception_type} - {self.exception_date}"

class SystemConfig(models.Model):
    """System configuration for image handling and scanning"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
    
    def __str__(self):
        return self.key

class ImageQualityConfig(models.Model):
    """Configuration for image quality requirements"""
    config_name = models.CharField(max_length=100, default='Default')
    
    # Minimum image quality scores
    min_portrait_quality = models.DecimalField(max_digits=5, decimal_places=2, default=0.8)
    min_id_front_quality = models.DecimalField(max_digits=5, decimal_places=2, default=0.7)
    min_id_back_quality = models.DecimalField(max_digits=5, decimal_places=2, default=0.7)
    
    # File size limits (in MB)
    max_portrait_size = models.IntegerField(default=5, help_text='Maximum file size in MB')
    max_id_image_size = models.IntegerField(default=3, help_text='Maximum file size in MB')
    
    # Image dimensions
    min_portrait_width = models.IntegerField(default=300)
    min_portrait_height = models.IntegerField(default=300)
    min_id_width = models.IntegerField(default=600)
    min_id_height = models.IntegerField(default=400)
    
    # Face detection settings
    require_face_detection = models.BooleanField(default=True)
    min_face_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.7)
    
    # ID scan settings
    require_id_text_detection = models.BooleanField(default=True)
    min_text_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.6)
    
    # Auto-crop settings
    auto_crop_images = models.BooleanField(default=True)
    auto_enhance_images = models.BooleanField(default=True)
    
    # Compression settings
    compress_images = models.BooleanField(default=True)
    compression_quality = models.IntegerField(default=85, help_text='Compression quality (1-100)')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Image Quality Configuration'
        verbose_name_plural = 'Image Quality Configurations'
    
    def __str__(self):
        return f"Image Quality Config: {self.config_name}"