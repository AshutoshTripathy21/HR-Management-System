from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from .models import HRAccount, Employee, Attendance, AttendanceHistory, LeaveRequest, Logoff, EmployeeDocument, Group
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.http import FileResponse

# from .forms import EmployeeForm

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            hr_account = HRAccount.objects.get(email=email)
            if hr_account.password == password:
                request.session['logged_in'] = True
                return redirect('home')
            else:
                return HttpResponse("Invalid email or password.")
        except HRAccount.DoesNotExist:
            return HttpResponse("Invalid email or password.")
    return render(request, 'login.html')

def home_view(request):
    if not request.session.get('logged_in'):
        return redirect('login')
    return render(request, 'home.html')


def logout_view(request):
    request.session.flush()  # Clear session data
    return redirect('login')

def add_employee_view(request):
    if not request.session.get('logged_in'):
        return redirect('login')
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        name = request.POST.get('name')
        position = request.POST.get('position')
        department = request.POST.get('department')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        dob = request.POST.get('dob')
        leaves = request.POST.get('leaves')

        # Create a new Employee object
        employee = Employee(
            employee_id=employee_id,
            name=name,
            position=position,
            department=department,
            email=email,
            phone_number=phone_number,
            dob=dob,
            leaves=leaves
        )
        employee.save()
        return redirect('employee_list')
    return render(request, 'add_employee.html')

def employee_list_view(request):
    if not request.session.get('logged_in'):
        return redirect('login')
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})

def employee_detail_view(request, employee_id):
    if not request.session.get('logged_in'):
        return redirect('login')
    employee = get_object_or_404(Employee, employee_id=employee_id)
    return render(request, 'employee_detail.html', {'employee': employee})

def update_employee_view(request, employee_id):
    if not request.session.get('logged_in'):
        return redirect('login')
    employee = get_object_or_404(Employee, employee_id=employee_id)
    if request.method == 'POST':
        employee.name = request.POST.get('name')
        employee.position = request.POST.get('position')
        employee.department = request.POST.get('department')
        employee.email = request.POST.get('email')
        employee.phone_number = request.POST.get('phone_number')
        employee.dob = request.POST.get('dob')
        employee.leaves = request.POST.get('leaves')
        employee.save()
        return redirect('employee_detail', employee_id=employee.employee_id)
    return render(request, 'update_employee.html', {'employee': employee})

def employee_login_view(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        dob = request.POST.get('dob')
        try:
            employee = Employee.objects.get(employee_id=employee_id, dob=dob)
            otp = get_random_string(6, '0123456789')
            employee.otp = otp
            employee.save()
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,  # Use the email from settings
                [employee.email],
                fail_silently=False,
            )
            request.session['employee_id'] = employee_id
            return redirect('otp_verify')
        except Employee.DoesNotExist:
            return render(request, 'employee_login.html', {'error': 'Invalid Employee ID or Date of Birth'})
    return render(request, 'employee_login.html')

def otp_verify_view(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        employee_id = request.session.get('employee_id')
        employee = get_object_or_404(Employee, employee_id=employee_id)
        if employee.otp == otp:
            request.session['employee_logged_in'] = True
            return redirect('employee_welcome')
        else:
            return render(request, 'otp_verify.html', {'error': 'Invalid OTP'})
    return render(request, 'otp_verify.html')

def employee_welcome_view(request):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, employee_id=employee_id)
    return render(request, 'employee_welcome.html', {'employee': employee})


def mark_attendance_view(request):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')
    
    if request.method == 'POST':
        present = request.POST.get('present') == 'on'
        employee_id = request.session.get('employee_id')
        employee = get_object_or_404(Employee, employee_id=employee_id)
        
        status = 'Present' if present else 'Absent'
        today = timezone.now().date()

        # Check if the employee has already marked attendance for today
        existing_attendance = Attendance.objects.filter(employee=employee, date=today).first()
        if existing_attendance:
            return render(request, 'mark_attendance.html', {'error': 'Attendance already marked for today'})
        
        # Record today's attendance
        Attendance.objects.create(
            employee=employee,
            date=today,
            status=status
        )
        
        # Record attendance history
        AttendanceHistory.objects.update_or_create(
            employee=employee,
            date=today,
            defaults={'status': status}
        )
        
        return redirect('employee_welcome')
    
    return render(request, 'mark_attendance.html')



def attendance_logs_view(request):
    today = timezone.now().date()
    attendances = Attendance.objects.filter(date=today)
    context = {'attendances': attendances}
    return render(request, 'attendance_logs.html', context)

def attendance_history_view(request):
    if not request.session.get('logged_in'):
        return redirect('login')

    employee_id = request.GET.get('employee_id')
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    # Get attendance history with logoff details
    history = AttendanceHistory.objects.filter(employee=employee).order_by('-date')
    attendance_with_logoff = []

    for attendance in history:
        logoff = Logoff.objects.filter(attendance__employee=employee, attendance__date=attendance.date).first()
        attendance_with_logoff.append({
            'date': attendance.date,
            'status': attendance.status,
            'work_hours': logoff.work_hours if logoff else None
        })

    context = {'employee': employee, 'attendance_with_logoff': attendance_with_logoff}
    return render(request, 'attendance_history.html', context)


def employee_detail_self_view(request):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')

    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, employee_id=employee_id)

    return render(request, 'employee_details.html', {'employee': employee})


def leave_request_view(request):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')

    if request.method == 'POST':
        employee_id = request.session.get('employee_id')
        employee = get_object_or_404(Employee, employee_id=employee_id)

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        leave_request = LeaveRequest(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )
        leave_request.save()

        return redirect('employee_leave_status')
    return render(request, 'leave_request.html')


def hr_leave_requests_view(request):
    if not request.session.get('logged_in'):
        return redirect('login')

    leave_requests = LeaveRequest.objects.all()
    return render(request, 'hr_leave_requests.html', {'leave_requests': leave_requests})


def update_leave_status_view(request, leave_request_id, status):
    if not request.session.get('logged_in'):
        return redirect('login')

    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    if status == 'Accepted':
        # Calculate the number of leave days requested
        leave_days = (leave_request.end_date - leave_request.start_date).days + 1

        # Deduct the leave days from the employee's available leaves
        employee = leave_request.employee
        if employee.leaves >= leave_days:
            employee.leaves -= leave_days
            employee.save()

            leave_request.status = 'Accepted'
        else:
            # If the employee doesn't have enough leave days, keep the request pending or reject it
            leave_request.status = 'Rejected'  # Or keep it 'Pending' with a message
    elif status == 'Rejected':
        leave_request.status = 'Rejected'
    
    leave_request.save()

    return redirect('hr_leave_requests')


def employee_leave_status_view(request):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')

    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, employee_id=employee_id)
    leave_requests = LeaveRequest.objects.filter(employee=employee)

    return render(request, 'employee_leave_status.html', {'leave_requests': leave_requests})


def logout_view_employee(request):
    request.session.flush()  # Clear session data
    return redirect('employee_login')


def logoff_view(request):
    if request.method == 'POST':
        employee_id = request.session.get('employee_id')
        employee = get_object_or_404(Employee, employee_id=employee_id)

        attendance = get_object_or_404(Attendance, employee=employee, date=timezone.now().date())

        # Check if already logged off
        if Logoff.objects.filter(attendance=attendance).exists():
            return render(request, 'logoff.html', {'error': 'Already logged off for today'})

        # Logoff the employee
        logoff = Logoff(attendance=attendance)
        logoff.save()

        return redirect('employee_welcome')
    return render(request, 'logoff.html')


def attendance_history_view(request):
    if not request.session.get('logged_in'):
        return redirect('login')

    employee_id = request.GET.get('employee_id')
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    # Get attendance history with logoff details
    history = AttendanceHistory.objects.filter(employee=employee).order_by('-date')
    attendance_with_logoff = []

    for attendance in history:
        logoff = Logoff.objects.filter(attendance__employee=employee, attendance__date=attendance.date).first()
        attendance_with_logoff.append({
            'date': attendance.date,
            'status': attendance.status,
            'work_hours': logoff.work_hours if logoff else None
        })

    context = {'employee': employee, 'attendance_with_logoff': attendance_with_logoff}
    return render(request, 'attendance_history.html', context)


def upload_document_view(request):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')
    
    if request.method == 'POST':
        employee_id = request.session.get('employee_id')
        employee = get_object_or_404(Employee, employee_id=employee_id)
        document = request.FILES.get('document')

        if document:
            EmployeeDocument.objects.create(employee=employee, document=document)
            return redirect('employee_welcome')

    return render(request, 'upload_document.html')

# HR view to see all uploaded documents of a specific employee
def employee_documents_view(request, employee_id):
    if not request.session.get('logged_in'):
        return redirect('login')

    employee = get_object_or_404(Employee, employee_id=employee_id)
    documents = employee.documents.all()

    return render(request, 'employee_documents.html', {'employee': employee, 'documents': documents})


def download_document(request, doc_id):
    document = get_object_or_404(EmployeeDocument, id=doc_id)
    try:
        response = FileResponse(document.document.open(), as_attachment=True, filename=document.document.name)
        return response
    except FileNotFoundError:
        return HttpResponseNotFound("Document not found.")
    

def create_group(request):
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        task_details = request.POST.get('task_details')
        deadline = request.POST.get('deadline')
        leader_name = request.POST.get('leader_name')
        leader_id = request.POST.get('leader_id')
        
        # Process members
        members_data = request.POST.get('members', '').splitlines()
        members = []
        for member in members_data:
            if ',' in member:
                name, emp_id = member.split(',', 1)
                members.append({'name': name.strip(), 'id': emp_id.strip()})
        
        # Create Group
        group = Group.objects.create(
            task_name=task_name,
            task_details=task_details,
            deadline=deadline,
            leader_name=leader_name,
            leader_id=leader_id
        )
        
        # Add members to the group
        for member in members:
            emp = get_object_or_404(Employee, employee_id=member['id'])
            group.members.add(emp)
            
            # Send email to member
            send_mail(
                f'You are added to the group for {task_name}',
                f'You are added to the group for {task_name}. Your leader is {leader_name}. Deadline: {deadline}',
                'exampleflask365@outlook.com',
                [emp.email],
                fail_silently=False,
            )

        return redirect('group_created')  # Redirect to a confirmation page

    return render(request, 'create_group.html')


def group_created(request):
    return render(request, 'home.html')

def employee_groups(request):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')
    
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, employee_id=employee_id)
    groups = Group.objects.filter(members__in=[employee])
    
    return render(request, 'employee_groups.html', {'groups': groups})


def group_details_view(request, group_id):
    if not request.session.get('employee_logged_in'):
        return redirect('employee_login')
        
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'group_details.html', {'group': group})