from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Application, Job, UserProfile


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser or user.is_staff:
        return 'admin'
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': UserProfile.CANDIDATE})
    return profile.role


def home(request):
    search_query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()

    jobs = Job.objects.select_related('employer').order_by('-created_at')
    if search_query:
        for term in search_query.split():
            jobs = jobs.filter(
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(location__icontains=term)
            )
    if location:
        jobs = jobs.filter(location__icontains=location)

    return render(
        request,
        'home.html',
        {
            'jobs': jobs,
            'search_query': search_query,
            'location_query': location,
            'user_role': get_user_role(request.user),
        },
    )


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', UserProfile.CANDIDATE)

        if role not in dict(UserProfile.ROLE_CHOICES):
            messages.error(request, "Please choose a valid role.")
            return redirect('signup')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, role=role)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'signup.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            return redirect('dashboard')

        messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user_role = get_user_role(request.user)

    if user_role == UserProfile.EMPLOYER:
        jobs = Job.objects.filter(employer=request.user).annotate(application_count=Count('applications')).order_by('-created_at')
        context = {
            'user_role': user_role,
            'jobs': jobs,
            'total_jobs': jobs.count(),
            'total_applications': sum(job.application_count for job in jobs),
        }
    else:
        applications = Application.objects.filter(applicant=request.user).select_related('job', 'job__employer').order_by('-applied_at')
        context = {
            'user_role': user_role,
            'applications': applications,
            'total_applications': applications.count(),
            'jobs_available': Job.objects.count(),
        }

    return render(request, 'dashboard.html', context)


@login_required
def post_job(request):
    if get_user_role(request.user) != UserProfile.EMPLOYER:
        messages.error(request, "Only employers can post jobs.")
        return redirect('dashboard')

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()
        salary = request.POST.get('salary', '').strip()

        if not all([title, description, location, salary]):
            messages.error(request, "All job fields are required.")
            return redirect('post_job')

        Job.objects.create(
            employer=request.user,
            title=title,
            description=description,
            location=location,
            salary=salary,
        )
        messages.success(request, "Job posted successfully.")
        return redirect('dashboard')

    return render(request, 'post.html')


@login_required
def apply_job(request, id):
    if get_user_role(request.user) != UserProfile.CANDIDATE:
        messages.error(request, "Only candidates can apply for jobs.")
        return redirect('dashboard')

    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        if Application.objects.filter(job=job, applicant=request.user).exists():
            messages.info(request, "You have already applied for this job.")
            return redirect('dashboard')

        resume = request.FILES.get('resume')
        if not resume:
            messages.error(request, "Please upload your resume.")
            return redirect('apply_job', id=id)

        Application.objects.create(job=job, applicant=request.user, resume=resume)
        messages.success(request, "Application submitted successfully.")
        return redirect('dashboard')

    return render(request, 'apply_job.html', {'job': job})


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def admin_dashboard(request):
    return render(
        request,
        'admin_dashboard.html',
        {
            'total_users': User.objects.count(),
            'total_employers': UserProfile.objects.filter(role=UserProfile.EMPLOYER).count(),
            'total_candidates': UserProfile.objects.filter(role=UserProfile.CANDIDATE).count(),
            'total_jobs': Job.objects.count(),
            'total_applications': Application.objects.count(),
            'recent_jobs': Job.objects.select_related('employer').order_by('-created_at')[:5],
            'recent_applications': Application.objects.select_related('job', 'applicant').order_by('-applied_at')[:5],
        },
    )
