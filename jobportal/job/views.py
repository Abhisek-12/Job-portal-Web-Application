from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Application, Job, SavedJob, UserProfile


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
    min_salary = request.GET.get('min_salary', '').strip()
    max_salary = request.GET.get('max_salary', '').strip()

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
    if min_salary.isdigit():
        jobs = jobs.filter(salary__gte=int(min_salary))
    if max_salary.isdigit():
        jobs = jobs.filter(salary__lte=int(max_salary))

    title_suggestions = Job.objects.order_by('title').values_list('title', flat=True).distinct()[:20]
    location_suggestions = Job.objects.order_by('location').values_list('location', flat=True).distinct()[:20]

    greeting = 'Welcome, Job Seeker!'

    top_companies = (
        UserProfile.objects
        .filter(role=UserProfile.EMPLOYER)
        .annotate(job_count=Count('user__jobs'))
        .filter(job_count__gt=0)
        .select_related('user')
        .order_by('-job_count')[:6]
    )

    saved_job_ids = []
    if request.user.is_authenticated and get_user_role(request.user) == UserProfile.CANDIDATE:
        saved_job_ids = list(SavedJob.objects.filter(candidate=request.user).values_list('job_id', flat=True))

    return render(
        request,
        'home.html',
        {
            'jobs': jobs,
            'search_query': search_query,
            'location_query': location,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'user_role': get_user_role(request.user),
            'greeting': greeting,
            'job_count': Job.objects.count(),
            'company_count': UserProfile.objects.filter(role=UserProfile.EMPLOYER).count(),
            'candidate_count': UserProfile.objects.filter(role=UserProfile.CANDIDATE).count(),
            'top_companies': top_companies,
            'title_suggestions': title_suggestions,
            'location_suggestions': location_suggestions,
            'saved_job_ids': saved_job_ids,
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
def delete_job(request, id):
    job = get_object_or_404(Job, id=id)
    if request.user != job.employer and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to delete this job.")
        return redirect('dashboard')

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully.")
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    messages.error(request, "Invalid request.")
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('dashboard')


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
def save_job(request, id):
    job = get_object_or_404(Job, id=id)
    if get_user_role(request.user) != UserProfile.CANDIDATE:
        messages.error(request, 'Only candidates can save jobs.')
        return redirect('dashboard')

    if request.method == 'POST':
        saved_job, created = SavedJob.objects.get_or_create(job=job, candidate=request.user)
        if created:
            messages.success(request, 'Job saved successfully.')
        else:
            messages.info(request, 'This job is already in your saved list.')
        return redirect('saved_jobs')

    messages.error(request, 'Invalid request.')
    return redirect('home')


@login_required
def saved_jobs(request):
    if get_user_role(request.user) != UserProfile.CANDIDATE:
        messages.error(request, 'Only candidates can view saved jobs.')
        return redirect('dashboard')

    saved_jobs = SavedJob.objects.filter(candidate=request.user).select_related('job', 'job__employer')
    return render(request, 'saved_jobs.html', {'saved_jobs': saved_jobs})


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


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def admin_users(request):
    role = request.GET.get('role')
    users = User.objects.select_related('profile').order_by('username')
    page_title = 'All Users'
    page_description = 'Review all user accounts registered on the platform.'

    selected_role = role if role in (UserProfile.EMPLOYER, UserProfile.CANDIDATE) else None

    if selected_role:
        users = users.filter(profile__role=selected_role)
        page_title = 'Employers' if selected_role == UserProfile.EMPLOYER else 'Candidates'
        page_description = f'Review all {page_title.lower()} on the platform.'

    return render(request, 'admin_users.html', {
        'users': users,
        'page_title': page_title,
        'page_description': page_description,
        'selected_role': selected_role,
    })


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def admin_delete_user(request, id):
    user_to_delete = get_object_or_404(User, id=id)
    if request.user == user_to_delete:
        messages.error(request, "You cannot delete your own account from this page.")
        return redirect('admin_users')

    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"User '{username}' deleted successfully along with related data.")
        if request.POST.get('return_role') in (UserProfile.EMPLOYER, UserProfile.CANDIDATE):
            return redirect(f"{reverse('admin_users')}?role={request.POST.get('return_role')}")
        return redirect('admin_users')

    messages.error(request, "Invalid request.")
    return redirect('admin_users')


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def admin_jobs(request):
    jobs = Job.objects.select_related('employer').order_by('-created_at')
    return render(request, 'admin_jobs.html', {
        'jobs': jobs,
        'page_title': 'All Jobs',
        'page_description': 'Review all job postings currently in the system.',
    })


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def admin_applications(request):
    applications = Application.objects.select_related('job', 'applicant').order_by('-applied_at')
    return render(request, 'admin_applications.html', {
        'applications': applications,
        'page_title': 'All Applications',
        'page_description': 'Review all job applications submitted by candidates.',
    })
