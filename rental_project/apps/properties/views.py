import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.gis.db.models.functions import Distance
from .models import Property, University, MetroStation
from .forms import PropertyForm
from apps.tours.forms import TourBookingForm

def property_list(request):
    """
    SSR Student Housing Property Listing with Cairo University Proximity & Student Filters:
    GET /?search=...&university=...&gender=...&rental_type=...&price_range=...&bills=...&sort=...&view=...
    """
    queryset = Property.objects.select_related('university', 'nearest_metro').all()
    universities = University.objects.all()
    metro_stations = MetroStation.objects.all()

    # Query Parameters
    search_query = request.GET.get('search', '').strip()
    university_id = request.GET.get('university')
    gender = request.GET.get('gender')  # 'female', 'male'
    rental_type = request.GET.get('rental_type', 'all')  # 'bed', 'room', 'apartment'
    price_range = request.GET.get('price_range', 'all')
    bills_included = request.GET.get('bills') in ['true', '1', 'on']
    has_elevator = request.GET.get('elevator') in ['true', '1', 'on']
    has_study_desk = request.GET.get('study_desk') in ['true', '1', 'on']
    selected_amenities = request.GET.getlist('amenity')
    sort_by = request.GET.get('sort', 'proximity' if university_id and university_id != 'all' else 'newest')
    view_mode = request.GET.get('view', 'grid')  # 'grid' or 'map'
    selected_property_id = request.GET.get('property_id')

    selected_university = None
    if university_id and university_id != 'all':
        try:
            selected_university = University.objects.get(pk=university_id)
            if selected_university.location:
                # PostGIS Spatial distance annotation (in meters/kilometers)
                queryset = queryset.annotate(spatial_distance=Distance('location', selected_university.location))
                if sort_by == 'proximity' or not sort_by:
                    queryset = queryset.order_by('spatial_distance')
        except University.DoesNotExist:
            selected_university = None

    # 1. Filter by Gender Policy
    if gender == 'female':
        queryset = queryset.filter(gender_policy='female_only')
    elif gender == 'male':
        queryset = queryset.filter(gender_policy='male_only')

    # 2. Filter by Rental Type
    if rental_type and rental_type != 'all':
        queryset = queryset.filter(rental_type=rental_type)

    # 3. Search query filter
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(title_ar__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(description_ar__icontains=search_query) |
            Q(university__name_ar__icontains=search_query) |
            Q(nearest_metro__name_ar__icontains=search_query)
        )

    # 4. Price range filter in EGP
    if price_range and price_range != 'all':
        if price_range == '<2000':
            queryset = queryset.filter(price_egp__lt=2000)
        elif price_range == '2000-3500':
            queryset = queryset.filter(price_egp__gte=2000, price_egp__lte=3500)
        elif price_range == '3500-5000':
            queryset = queryset.filter(price_egp__gte=3500, price_egp__lte=5000)
        elif price_range == '5000+':
            queryset = queryset.filter(price_egp__gt=5000)

    # 5. Student Specific Filters
    if bills_included:
        queryset = queryset.filter(bills_included=True)
    if has_elevator:
        queryset = queryset.filter(has_elevator=True)
    if has_study_desk:
        queryset = queryset.filter(study_desk=True)

    # 6. Amenities filter
    if selected_amenities:
        for amenity in selected_amenities:
            queryset = queryset.filter(amenities__contains=[amenity])

    # 7. Sorting
    if sort_by == 'price_asc':
        queryset = queryset.order_by('price_egp')
    elif sort_by == 'price_desc':
        queryset = queryset.order_by('-price_egp')
    elif sort_by == 'beds_available':
        queryset = queryset.order_by('-available_beds')
    elif sort_by == 'popular':
        queryset = queryset.order_by('-featured', 'posted_days_ago', '-created_at')
    elif sort_by == 'proximity' and selected_university:
        queryset = queryset.order_by('spatial_distance')
    else:
        if not selected_university:
            queryset = queryset.order_by('-created_at')

    # Selected Property for detail view/modal if requested via URL
    selected_property = None
    if selected_property_id:
        try:
            selected_property = Property.objects.get(pk=selected_property_id)
        except Property.DoesNotExist:
            selected_property = None

    # Serialization of properties for interactive Map & Drawer
    properties_data = []
    for p in queryset:
        dist_str = ""
        if hasattr(p, 'spatial_distance') and p.spatial_distance:
            km = p.spatial_distance.km
            dist_str = f"{km:.1f} كم من الجامعة"
        else:
            dist_str = f"{p.distance_to_university_km} كم من الجامعة"

        properties_data.append({
            'id': p.id,
            'title': p.title,
            'title_ar': p.title_ar,
            'description': p.description,
            'description_ar': p.description_ar,
            'price_egp': p.price_egp,
            'deposit_egp': p.deposit_egp,
            'bills_included': p.bills_included,
            'rental_type': p.rental_type,
            'rental_type_display': p.get_rental_type_display_ar(),
            'gender_policy': p.gender_policy,
            'gender_display': p.get_gender_display_ar(),
            'total_capacity': p.total_capacity,
            'available_beds': p.available_beds,
            'university_name': p.university.name_ar if p.university else "بالقرب من الجامعات",
            'nearest_metro': p.nearest_metro.name_ar if p.nearest_metro else None,
            'distance_to_university': dist_str,
            'walking_minutes': p.walking_minutes,
            'address': p.address,
            'city': p.city,
            'bedrooms': p.bedrooms,
            'bathrooms': p.bathrooms,
            'area_sqft': p.area_sqft,
            'images': p.images or [],
            'featured': p.featured,
            'badge': p.badge,
            'study_desk': p.study_desk,
            'wifi_speed': p.wifi_speed,
            'curfew_time': p.curfew_time,
            'has_elevator': p.has_elevator,
            'agent_name': p.agent_name,
            'agent_phone': p.agent_phone,
            'whatsapp_number': p.whatsapp_number,
            'whatsapp_url': p.get_whatsapp_url(is_ar=True),
            'lat': p.lat,
            'lng': p.lng,
        })

    all_amenities_list = [
        "إنترنت فائق السرعة Wi-Fi", "تكييف", "مكتب مذاكرة", "غسالة ملابس",
        "مطبخ مجهز بالكامل", "مصعد (أسانسير)", "سخان مياه", "أمن وإشراف"
    ]

    context = {
        'properties': queryset,
        'properties_json': json.dumps(properties_data),
        'count': queryset.count(),
        'universities': universities,
        'selected_university': selected_university,
        'selected_university_id': university_id or 'all',
        'metro_stations': metro_stations,
        'selected_property': selected_property,
        'search_query': search_query,
        'gender': gender or 'all',
        'rental_type': rental_type,
        'price_range': price_range,
        'bills_included': bills_included,
        'has_elevator': has_elevator,
        'has_study_desk': has_study_desk,
        'selected_amenities': selected_amenities,
        'sort_by': sort_by,
        'view_mode': view_mode,
        'all_amenities_list': all_amenities_list,
        'property_form': PropertyForm(),
        'tour_form': TourBookingForm(),
    }
    return render(request, 'properties/index.html', context)

def property_detail(request, pk):
    """Dedicated Detail Page for student accommodations"""
    prop = get_object_or_404(Property.objects.select_related('university', 'nearest_metro'), pk=pk)
    context = {
        'property': prop,
        'tour_form': TourBookingForm(initial={'property': prop}),
    }
    return render(request, 'properties/detail.html', context)

def property_create(request):
    """Handle new student property submission from frontend modal"""
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            new_prop = form.save(commit=False)
            if request.user.is_authenticated:
                new_prop.owner = request.user
                if hasattr(request.user, 'profile') and request.user.profile.phone:
                    if not new_prop.agent_phone:
                        new_prop.agent_phone = request.user.profile.phone
                    if not new_prop.whatsapp_number:
                        new_prop.whatsapp_number = request.user.profile.whatsapp or request.user.profile.phone
            new_prop.save()
            messages.success(request, f"تم إضافة السكن '{new_prop.title_ar or new_prop.title}' بنجاح!")
            if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_landlord:
                return redirect('accounts:dashboard')
            return redirect('/')
        else:
            messages.error(request, "يرجى تصحيح الأخطاء في النموذج والتأكد من ملء البيانات.")
    return redirect('/')
