from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .forms import StudentRegisterForm, LandlordRegisterForm, UserLoginForm, ProfileEditForm
from .models import UserProfile
from apps.properties.models import Property
from apps.roommates.models import RoommatePost
from apps.tours.models import TourBooking

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data['email'].strip()
            password = form.cleaned_data['password']

            # Support login via email or username
            user_obj = User.objects.filter(Q(email__iexact=login_input) | Q(username__iexact=login_input)).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f"مرحباً بعودتك، {user.first_name or user.username}!")
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    if hasattr(user, 'profile') and user.profile.is_landlord:
                        return redirect('accounts:dashboard')
                    return redirect('/')
            messages.error(request, "البريد الإلكتروني أو كلمة المرور غير صحيحة.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "تم تسجيل الخروج بنجاح.")
    return redirect('/')


def register_student_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"أهلاً بك يا {user.first_name}! تم إنشاء حساب الطالب بنجاح.")
            return redirect('/')
    else:
        form = StudentRegisterForm()

    return render(request, 'accounts/register_student.html', {'form': form})


def register_landlord_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = LandlordRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"أهلاً بك يا أستاذ {user.first_name}! تم تسجيل حسابك كصاحب سكن ومؤجر.")
            return redirect('accounts:dashboard')
    else:
        form = LandlordRegisterForm()

    return render(request, 'accounts/register_landlord.html', {'form': form})


@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            form.save()
            messages.success(request, "تم حفظ التعديلات بنجاح.")
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=profile, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

    # Student's roommate posts
    my_roommate_posts = RoommatePost.objects.filter(contact_phone=profile.phone) if profile.phone else []
    # Landlord's properties
    my_properties = Property.objects.filter(agent_phone=profile.phone) if profile.phone else []

    context = {
        'profile': profile,
        'form': form,
        'my_roommate_posts': my_roommate_posts,
        'my_properties': my_properties,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='/accounts/login/')
def landlord_dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Fetch properties associated with this landlord
    properties = Property.objects.filter(
        Q(agent_phone=profile.phone) | Q(agent_email=user.email) | Q(owner=user)
    ).distinct()

    # Calculate quick stats
    total_properties = properties.count()
    total_capacity = sum(p.total_capacity for p in properties)
    total_available_beds = sum(p.available_beds for p in properties)
    occupied_beds = total_capacity - total_available_beds

    # Tour requests for these properties
    tour_bookings = TourBooking.objects.filter(property__in=properties).order_by('-created_at')[:10]

    context = {
        'profile': profile,
        'properties': properties,
        'total_properties': total_properties,
        'total_capacity': total_capacity,
        'total_available_beds': total_available_beds,
        'occupied_beds': occupied_beds,
        'tour_bookings': tour_bookings,
    }
    return render(request, 'accounts/dashboard.html', context)
