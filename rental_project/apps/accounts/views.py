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


from django.http import JsonResponse

@login_required(login_url='/accounts/login/')
def landlord_dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if not profile.is_landlord:
        messages.warning(request, "هذه الصفحة مخصصة لحسابات أصحاب السكن والمؤجرين فقط.")
        return redirect('accounts:profile')

    # Fetch properties associated with this landlord
    properties = Property.objects.filter(
        Q(agent_phone=profile.phone) | Q(agent_email=user.email) | Q(owner=user)
    ).select_related('university', 'nearest_metro').distinct()

    # Calculate quick stats
    total_properties = properties.count()
    total_capacity = sum(p.total_capacity for p in properties)
    total_available_beds = sum(p.available_beds for p in properties)
    occupied_beds = max(0, total_capacity - total_available_beds)

    # Financial and Occupancy metrics
    monthly_revenue = sum(max(0, p.total_capacity - p.available_beds) * (p.price_egp or 0) for p in properties)
    max_possible_revenue = sum((p.total_capacity or 0) * (p.price_egp or 0) for p in properties)
    occupancy_rate = int((occupied_beds / total_capacity * 100)) if total_capacity > 0 else 0
    avg_price = int(sum((p.price_egp or 0) for p in properties) / total_properties) if total_properties > 0 else 0

    # Tour requests for these properties
    tour_bookings = TourBooking.objects.filter(property__in=properties).select_related('property').order_by('-created_at')[:20]

    context = {
        'profile': profile,
        'properties': properties,
        'total_properties': total_properties,
        'total_capacity': total_capacity,
        'total_available_beds': total_available_beds,
        'occupied_beds': occupied_beds,
        'monthly_revenue': monthly_revenue,
        'max_possible_revenue': max_possible_revenue,
        'occupancy_rate': occupancy_rate,
        'avg_price': avg_price,
        'tour_bookings': tour_bookings,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='/accounts/login/')
def update_beds_view(request, property_id):
    if request.method == 'POST':
        prop = get_object_or_404(Property, pk=property_id)
        profile = getattr(request.user, 'profile', None)
        # Authorization check
        is_owner = (prop.owner == request.user) or (profile and profile.phone and prop.agent_phone == profile.phone) or (prop.agent_email == request.user.email)
        if not is_owner:
            messages.error(request, "غير مصرح لك بتعديل هذا السكن.")
            return redirect('accounts:dashboard')

        try:
            delta = int(request.POST.get('delta', 0))
        except (ValueError, TypeError):
            delta = 0

        new_beds = prop.available_beds + delta
        if new_beds < 0:
            new_beds = 0
        if new_beds > prop.total_capacity:
            new_beds = prop.total_capacity

        prop.available_beds = new_beds
        prop.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'available_beds': prop.available_beds, 'total_capacity': prop.total_capacity})

        messages.success(request, f"تم تحديث الأسِرّة المتاحة لسكن '{prop.title_ar or prop.title}' إلى {prop.available_beds} سرير.")
    return redirect('/accounts/dashboard/#listings')


@login_required(login_url='/accounts/login/')
def update_tour_status_view(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(TourBooking, pk=booking_id)
        profile = getattr(request.user, 'profile', None)
        if booking.property:
            prop = booking.property
            is_owner = (prop.owner == request.user) or (profile and profile.phone and prop.agent_phone == profile.phone) or (prop.agent_email == request.user.email)
            if not is_owner:
                messages.error(request, "غير مصرح لك بتحديث حالة هذا الطلب.")
                return redirect('accounts:dashboard')
        new_status = request.POST.get('status')
        if new_status in dict(TourBooking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, f"تم تحديث حالة طلب المعاينة بنجاح.")
    return redirect('/accounts/dashboard/#tours')
