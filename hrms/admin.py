from django.contrib import admin
from .models import HRAccount, Employee, Attendance, EmployeeDocument, Group

@admin.register(HRAccount)
class HRAccountAdmin(admin.ModelAdmin):
    list_display = ('email',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'position', 'department', 'email', 'phone_number', 'dob', 'leaves')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time', 'status')
    list_filter = ('date', 'status')
    search_fields = ('employee__employee_id', 'employee__name')


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document', 'uploaded_at')
    search_fields = ('employee__employee_id', 'employee__name', 'document')
    list_filter = ('uploaded_at',)


admin.site.register(Group)