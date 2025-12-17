from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from .models import (
    Project, Supervisor, Labourer, IDVerificationLog, AttendanceLog,
    Task, TaskAssignment, Equipment, EquipmentAssignment, DailyClosureLog,
    ExceptionReport, SystemConfig, ImageQualityConfig, Role, Contract,
    CheckIn, CheckInDenial, SecurityGuard, CheckOut, DailyAttendanceSummary,
    ReportTemplate, GeneratedReport, ContractTemplate, TaskProgressLog
)

# ==================== Project Admin ====================
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'site_identifier', 'company_email', 'is_active', 'created_at', 'geofence_status')
    list_filter = ('is_active', 'timezone')
    search_fields = ('name', 'site_identifier', 'company_email')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'site_identifier', 'company_email', 'company_phone')
        }),
        ('Geofencing', {
            'fields': ('boundary_coordinates', 'entry_points'),
            'description': 'Set project boundaries for location-based check-ins. Format: [[-1.2886, 36.7914], [-1.2886, 36.7919], [-1.2881, 36.7919], [-1.2881, 36.7914]]'
        }),
        ('Operating Hours', {
            'fields': ('operating_hours', 'timezone', 'auto_checkout_time', 'overtime_threshold', 'overtime_multiplier')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def geofence_status(self, obj):
        if obj.boundary_coordinates and len(obj.boundary_coordinates) > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Configured ({} points)</span>',
                len(obj.boundary_coordinates)
            )
        return format_html('<span style="color: orange;">⚠️ Not Set</span>')
    geofence_status.short_description = 'Geofence'

# ==================== Supervisor Admin ====================
@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'phone_number', 'email', 'is_active')
    list_filter = ('is_active', 'project')
    search_fields = ('user__username', 'phone_number', 'email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)

# ==================== Labourer Admin ====================
@admin.register(Labourer)
class LabourerAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number',
        'full_name', 
        'national_id', 
        'designation', 
        'project', 
        'status',
        'photo_preview',
    )
    list_filter = (
        'status',
        'employment_type', 
        'department',
        'project',
        'gender',
        'whitelisted',
    )
    search_fields = (
        'serial_number',
        'full_name', 
        'national_id', 
        'phone_number', 
        'email'
    )
    readonly_fields = ('labourer_id', 'created_at', 'verified_at', 'photo_preview_large')
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'labourer_id',
                'serial_number',
                'full_name',
                'national_id',
                'date_of_birth',
                'gender',
                'district_of_birth',
                'id_serial_number',
            )
        }),
        ('Employment Details', {
            'fields': (
                'designation',
                'department',
                'project',
                'role',
                'employment_type',
                'supervisor',
            )
        }),
        ('Contact Information', {
            'fields': (
                'phone_number',
                'email',
            )
        }),
        ('Images & Documents', {
            'fields': (
                'portrait_photo',
                'photo_preview_large',
                'id_front_photo',
                'id_back_photo',
                'id_document',
            )
        }),
        ('System Status', {
            'fields': (
                'status',
                'whitelisted',
                'created_at',
                'verified_at',
                'facial_encoding',
                'id_scan_quality_score',
                'facial_recognition_confidence',
            )
        }),
    )
    
    def photo_preview(self, obj):
        if obj.portrait_photo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
                obj.portrait_photo.url
            )
        return "No Photo"
    photo_preview.short_description = 'Photo'
    
    def photo_preview_large(self, obj):
        if obj.portrait_photo:
            return format_html(
                '<img src="{}" style="width: 150px; height: 150px; border-radius: 8px; object-fit: cover;" />',
                obj.portrait_photo.url
            )
        return "No Photo Available"
    photo_preview_large.short_description = 'Portrait Photo Preview'


# ==================== IDVerificationLog Admin ====================
@admin.register(IDVerificationLog)
class IDVerificationLogAdmin(admin.ModelAdmin):
    list_display = (
        'labourer',
        'verification_time',  
        'verification_type',  
        'is_successful',      
        'facial_match_score', 
        'id_match_score',     
        'overall_confidence', 
    )
    list_filter = (
        'is_successful',
        'verification_type',
        'verification_time',
    )
    search_fields = (
        'labourer__full_name',
        'labourer__national_id',
    )
    readonly_fields = ('verification_time',)
    date_hierarchy = 'verification_time'
    ordering = ('-verification_time',)

# ==================== AttendanceLog Admin ====================
@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = (
        'labourer',
        'log_type',
        'log_timestamp',
        'verification_method',
        'access_granted',
        'captured_image_preview',
        'supervisor_verified',
        'overall_confidence',
    )
    list_filter = (
        'log_type',
        'verification_method',
        'access_granted',
        'supervisor_verified',
        'security_verified',
        'log_timestamp',
    )
    search_fields = (
        'labourer__full_name',
        'labourer__national_id',
        'device_id',
    )
    readonly_fields = ('log_timestamp', 'captured_image_preview_large')
    date_hierarchy = 'log_timestamp'
    ordering = ('-log_timestamp',)
    
    def captured_image_preview(self, obj):
        if obj.captured_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 4px; object-fit: cover;" />',
                obj.captured_image.url
            )
        return "No Image"
    captured_image_preview.short_description = 'Attendance Image'
    
    def captured_image_preview_large(self, obj):
        if obj.captured_image:
            return format_html(
                '<img src="{}" style="width: 200px; height: 150px; border-radius: 8px; object-fit: cover;" />',
                obj.captured_image.url
            )
        return "No Attendance Image Available"
    captured_image_preview_large.short_description = 'Attendance Image Preview'

# ==================== Task Admin ====================
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'priority', 'status', 'deadline', 'assigned_to')
    list_filter = ('priority', 'status', 'project')
    search_fields = ('title', 'description')
    date_hierarchy = 'deadline'

# ==================== TaskAssignment Admin ====================
@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('labourer', 'task', 'supervisor', 'assigned_date', 'status')
    list_filter = ('status', 'assigned_date')
    search_fields = ('labourer__full_name', 'task__title')
    raw_id_fields = ('labourer', 'task', 'supervisor')

# ==================== Equipment Admin ====================
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment_id', 'category', 'status', 'project')
    list_filter = ('category', 'status', 'project')
    search_fields = ('name', 'equipment_id')

# ==================== EquipmentAssignment Admin ====================
# @admin.register(EquipmentAssignment)
class EquipmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'labourer', 'assigned_date', 'expected_return_date', 'status')
    list_filter = ('status', 'assigned_date')
    search_fields = ('equipment__name', 'labourer__full_name')
    readonly_fields = ('is_overdue',)
    
    def is_overdue(self, obj):
        if obj.expected_return_date and obj.actual_return_date:
            return obj.actual_return_date > obj.expected_return_date
        return False
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'

# ==================== Register Other Models ====================
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'base_wage', 'work_hours_per_day')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'labourer', 'start_date', 'end_date', 'status')

# @admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('labourer', 'timestamp', 'status', 'access_granted', 'project')

@admin.register(CheckInDenial)
class CheckInDenialAdmin(admin.ModelAdmin):
    list_display = ('checkin_attempt', 'reason', 'resolved', 'supervisor_notified')

# @admin.register(SecurityGuard)
class SecurityGuardAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_number', 'project', 'can_override')

@admin.register(CheckOut)
class CheckOutAdmin(admin.ModelAdmin):
    list_display = ('labourer', 'checkout_type', 'completed_at', 'project')

@admin.register(DailyAttendanceSummary)
class DailyAttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('labourer', 'date', 'attendance_status', 'total_hours', 'total_earnings')

# @admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'format', 'schedule')

@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('template', 'project', 'generated_at', 'period_start', 'period_end')

@admin.register(TaskProgressLog)
class TaskProgressLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'labourer', 'update_type', 'timestamp', 'progress_percentage')

@admin.register(DailyClosureLog)
class DailyClosureLogAdmin(admin.ModelAdmin):
    list_display = (
        'closure_date',
        'closure_time',
        'total_labourers_checked_in',
        'total_labourers_checked_out',
        'forced_checkouts',
        'exceptions_count',
        'processed_by_system',
    )
    list_filter = ('closure_date', 'processed_by_system')
    date_hierarchy = 'closure_date'
    readonly_fields = ('processed_timestamp',)

# @admin.register(ExceptionReport)
class ExceptionReportAdmin(admin.ModelAdmin):
    list_display = (
        'labourer',
        'exception_date',
        'exception_type',
        'severity',
        'resolved',
        'resolved_by',
    )
    list_filter = ('exception_type', 'severity', 'resolved', 'exception_date')
    search_fields = ('labourer__full_name', 'description')
    date_hierarchy = 'exception_date'
    raw_id_fields = ('labourer', 'resolved_by')

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key', 'description')
    list_editable = ('value',)

# @admin.register(ImageQualityConfig)
class ImageQualityConfigAdmin(admin.ModelAdmin):
    list_display = (
        'config_name',
        'min_portrait_quality',
        'min_id_front_quality',
        'max_portrait_size',
        'max_id_image_size',
        'is_active',
    )
    list_filter = ('is_active',)
    search_fields = ('config_name',)

# ==================== Custom Admin Site Settings ====================
admin.site.site_header = "Site System Admin"
admin.site.site_title = "Site System"
admin.site.index_title = "Welcome to Site System Admin Portal"