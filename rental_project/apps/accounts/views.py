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


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    active_tab = request.GET.get('tab', 'account')
    valid_tabs = ['account', 'tours', 'roommates', 'saved', 'security']
    if active_tab not in valid_tabs:
        active_tab = 'account'

    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'change_password':
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                updated_user = password_form.save()
                update_session_auth_hash(request, updated_user)
                messages.success(request, "تم تغيير كلمة المرور بنجاح!")
                return redirect('/accounts/profile/?tab=security')
            else:
                active_tab = 'security'
                messages.error(request, "يرجى تصحيح أخطاء كلمة المرور الموضحة أدناه.")
                form = ProfileEditForm(instance=profile, initial={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                })
        else:
            form = ProfileEditForm(request.POST, instance=profile)
            if form.is_valid():
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()
                form.save()
                messages.success(request, "تم حفظ وتحديث بياناتك الشخصية بنجاح.")
                return redirect('/accounts/profile/?tab=account')
            else:
                active_tab = 'account'
                messages.error(request, "يرجى تصحيح الأخطاء في نموذج البيانات أدناه.")
    else:
        form = ProfileEditForm(instance=profile, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

    # Student's tour bookings (matched by user, email, or phone)
    tour_filter = Q(user=user) | Q(email__iexact=user.email)
    if profile.phone:
        tour_filter |= Q(phone=profile.phone)
    my_tours = TourBooking.objects.filter(tour_filter).select_related('property', 'property__university').order_by('-created_at')
    pending_tours_count = my_tours.filter(status='pending').count()
    confirmed_tours_count = my_tours.filter(status='confirmed').count()

    # Student's roommate posts (matched by user, phone, or whatsapp)
    roommate_filter = Q(user=user)
    if profile.phone:
        roommate_filter |= Q(contact_phone=profile.phone) | Q(whatsapp_number=profile.phone)
    if profile.whatsapp:
        roommate_filter |= Q(contact_phone=profile.whatsapp) | Q(whatsapp_number=profile.whatsapp)
    my_roommate_posts = RoommatePost.objects.filter(roommate_filter).order_by('-created_at')

    # Landlord's properties
    my_properties = Property.objects.filter(
        Q(agent_phone=profile.phone) | Q(agent_email=user.email) | Q(owner=user)
    ) if profile.is_landlord else []

    context = {
        'profile': profile,
        'form': form,
        'password_form': password_form,
        'active_tab': active_tab,
        'my_tours': my_tours,
        'pending_tours_count': pending_tours_count,
        'confirmed_tours_count': confirmed_tours_count,
        'my_roommate_posts': my_roommate_posts,
        'my_properties': my_properties,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='/accounts/login/')
def student_cancel_tour_view(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(TourBooking, pk=booking_id)
        profile = getattr(request.user, 'profile', None)
        is_owner = (booking.user == request.user) or (booking.email.lower() == request.user.email.lower()) or (profile and profile.phone and booking.phone == profile.phone)
        if is_owner:
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, "تم إلغاء طلب المعاينة بنجاح.")
        else:
            messages.error(request, "غير مصرح لك بإلغاء هذا الطلب.")
    return redirect('/accounts/profile/?tab=tours')


@login_required(login_url='/accounts/login/')
def student_toggle_roommate_post_view(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(RoommatePost, pk=post_id)
        profile = getattr(request.user, 'profile', None)
        is_owner = (post.user == request.user) or \
                   (profile and profile.phone and (post.contact_phone == profile.phone or post.whatsapp_number == profile.phone)) or \
                   (profile and profile.whatsapp and (post.whatsapp_number == profile.whatsapp or post.contact_phone == profile.whatsapp))
        if is_owner:
            post.is_active = not post.is_active
            post.save()
            msg = "تم تنشيط إعلان رفيق السكن بنجاح." if post.is_active else "تم إيقاف الإعلان (تم إيجاد رفيق السكن بنجاح)."
            messages.success(request, msg)
        else:
            messages.error(request, "غير مصرح لك بتعديل هذا المنشور.")
    return redirect('/accounts/profile/?tab=roommates')


@login_required(login_url='/accounts/login/')
def student_delete_roommate_post_view(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(RoommatePost, pk=post_id)
        profile = getattr(request.user, 'profile', None)
        is_owner = (post.user == request.user) or \
                   (profile and profile.phone and (post.contact_phone == profile.phone or post.whatsapp_number == profile.phone)) or \
                   (profile and profile.whatsapp and (post.whatsapp_number == profile.whatsapp or post.contact_phone == profile.whatsapp))
        if is_owner:
            post.delete()
            messages.success(request, "تم حذف إعلان رفيق السكن بنجاح.")
        else:
            messages.error(request, "غير مصرح لك بحذف هذا المنشور.")
    return redirect('/accounts/profile/?tab=roommates')


from django.http import JsonResponse

@login_required(login_url='/accounts/login/')
def landlord_dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if not profile.is_landlord:
        messages.warning(request, "هذه الصفحة مخصصة لحسابات أصحاب السكن والمؤجرين فقط.")
        return redirect('accounts:profile')

    active_tab = request.GET.get('tab', 'overview')
    if active_tab not in ['overview', 'listings', 'tours', 'financials']:
        active_tab = 'overview'

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
    all_tours_qs = TourBooking.objects.filter(property__in=properties)
    pending_tours_count = all_tours_qs.filter(status='pending').count()
    tour_bookings = all_tours_qs.select_related('property').order_by('-created_at')[:50]

    # Per-property financial breakdown for financials tab
    properties_stats = []
    for p in properties:
        occ = max(0, p.total_capacity - p.available_beds)
        rev = occ * (p.price_egp or 0)
        max_rev = (p.total_capacity or 0) * (p.price_egp or 0)
        rate = int((occ / p.total_capacity * 100)) if p.total_capacity > 0 else 0
        properties_stats.append({
            'prop': p,
            'occupied': occ,
            'revenue': rev,
            'max_revenue': max_rev,
            'rate': rate,
        })

    context = {
        'profile': profile,
        'properties': properties,
        'properties_stats': properties_stats,
        'active_tab': active_tab,
        'total_properties': total_properties,
        'total_capacity': total_capacity,
        'total_available_beds': total_available_beds,
        'occupied_beds': occupied_beds,
        'monthly_revenue': monthly_revenue,
        'max_possible_revenue': max_possible_revenue,
        'occupancy_rate': occupancy_rate,
        'avg_price': avg_price,
        'tour_bookings': tour_bookings,
        'pending_tours_count': pending_tours_count,
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
            return redirect('/accounts/dashboard/?tab=listings')

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
    return redirect('/accounts/dashboard/?tab=listings')


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
                return redirect('/accounts/dashboard/?tab=tours')
        new_status = request.POST.get('status')
        if new_status in dict(TourBooking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, f"تم تحديث حالة طلب المعاينة بنجاح.")
    return redirect('/accounts/dashboard/?tab=tours')
