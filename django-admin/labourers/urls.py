from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Dashboard - now accessible at /labourers/
     path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    # Labourer Management - accessible at /labourers/labourers/
    path('labourers/', views.labourer_list, name='labourer_list'),
    path('labourers/add/', views.add_labourer, name='add_labourer'),
    path('labourers/<int:labourer_id>/', views.labourer_detail, name='labourer_detail'),
    path('labourers/<int:labourer_id>/edit/', views.edit_labourer, name='edit_labourer'),
    path('labourers/<int:labourer_id>/delete/', views.delete_labourer, name='delete_labourer'),
    
    # Image Upload and ID Scanning
    path('labourers/<int:labourer_id>/upload-portrait/', views.upload_portrait, name='upload_portrait'),
    path('labourers/<int:labourer_id>/upload-id-front/', views.upload_id_front, name='upload_id_front'),
    path('labourers/<int:labourer_id>/upload-id-back/', views.upload_id_back, name='upload_id_back'),
    path('labourers/<int:labourer_id>/scan-id/', views.scan_id_card, name='scan_id_card'),
     path('api/verify-location/<int:labourer_id>/', views.verify_location, name='verify_location'),
    path('api/project/<int:project_id>/geofence/', views.get_project_geofence, name='get_project_geofence'),
    path('api/simulate-location/', views.simulate_location, name='simulate_location'),
    # Attendance - accessible at /labourers/attendance/
    path('attendance/', views.attendance, name='attendance'),
    path('camera-test/', views.camera_test, name='camera_test'),
    path('attendance/verify/<int:labourer_id>/<str:action>/', 
         views.face_verification_page, name='face_verification'),
    path('api/verify-face/', views.verify_face_api, name='verify_face_api'),
    path('attendance/process/<int:labourer_id>/', 
         views.process_attendance, name='process_attendance'),
    # Check-in/Check-out with Face Verification
    path('attendance/check-in/<int:labourer_id>/', views.check_in, name='check_in'),
    path('attendance/check-out/<int:labourer_id>/', views.check_out, name='check_out'),
    path('verify-checkin/<int:checkin_id>/<str:action>/', views.verify_checkin, name='verify_checkin'),
    
    # Attendance History
    path('attendance/history/', views.attendance_history, name='attendance_history'),
    
    # API Endpoints
    path('api/upload-image/', views.api_upload_image, name='api_upload_image'),
    path('api/verify-attendance/', views.api_verify_attendance, name='api_verify_attendance'),
    path('api/attendance-history/', views.get_attendance_history, name='get_attendance_history'),
    path('api/labourers/', views.labourers_json, name='labourers_json'),
    
    # Projects & Supervisors
    path('projects/', views.project_list, name='project_list'),
    path('projects/geofence-setup/', views.project_geofence_setup, name='project_geofence_setup'),
    path('projects/<int:project_id>/update-boundary/', views.update_project_boundary, name='update_project_boundary'),
    path('supervisors/', views.supervisor_list, name='supervisor_list'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports'),
    path('reports/export/csv/', views.export_attendance_csv, name='export_attendance_csv'),
    path('reports/export/excel/', views.export_attendance_excel, name='export_attendance_excel'),
    path('reports/export/pdf/', views.export_attendance_pdf, name='export_attendance_pdf'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    
    # Face registration
    path('labourers/<int:labourer_id>/register-face-simple/', views.register_face_simple, name='register_face_simple'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)