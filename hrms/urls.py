from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('add-employee/', views.add_employee_view, name='add_employee'),
    path('employee-list/', views.employee_list_view, name='employee_list'),
    path('employee/<str:employee_id>/', views.employee_detail_view, name='employee_detail'),
    path('employee/<str:employee_id>/update/', views.update_employee_view, name='update_employee'),
    path('employee-login/', views.employee_login_view, name='employee_login'),
    path('otp-verify/', views.otp_verify_view, name='otp_verify'),
    path('employee-welcome/', views.employee_welcome_view, name='employee_welcome'),
    path('mark-attendance/', views.mark_attendance_view, name='mark_attendance'),
    path('attendance-logs/', views.attendance_logs_view, name='attendance_logs'),
    path('attendance-history/', views.attendance_history_view, name='attendance_history'),
    path('employee-details/', views.employee_detail_self_view, name='employee_detail_self'),
    path('leave-request/', views.leave_request_view, name='leave_request'),
    path('leave-status/', views.employee_leave_status_view, name='employee_leave_status'),
    path('hr-leave-requests/', views.hr_leave_requests_view, name='hr_leave_requests'),
    path('update-leave-status/<int:leave_request_id>/<str:status>/', views.update_leave_status_view, name='update_leave_status'),
    path('employee-logout/', views.logout_view_employee, name='employee-logout'),
    path('logoff/', views.logoff_view, name='logoff'),
    path('upload-document/', views.upload_document_view, name='upload_document'),
    path('employee/<str:employee_id>/documents/', views.employee_documents_view, name='employee_documents'),
    path('download/<int:doc_id>/', views.download_document, name='download_document'),
    path('create-group/', views.create_group, name='create_group'),
    path('group-created/', views.group_created, name='group_created'),
    path('groups/', views.employee_groups, name='employee_groups'),
    path('group/<int:group_id>/', views.group_details_view, name='group_details'),
]