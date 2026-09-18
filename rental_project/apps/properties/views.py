import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Property
from .forms import PropertyForm
from apps.tours.forms import TourBookingForm

def property_list(request):
    """
    SSR Property Listing with Query Parameter Filters:
    GET /?search=...&listing_type=...&property_type=...&bedrooms=...&price_range=...&family_mode=...&sort=...&view=...
    """
    queryset = Property.objects.all()

    # Query Parameters
    search_query = request.GET.get('search', '').strip()
    listing_type = request.GET.get('listing_type', 'rent')
    property_type = request.GET.get('property_type', 'all')
    bedrooms = request.GET.get('bedrooms', 'all')
    price_range = request.GET.get('price_range', 'all')
    family_mode = request.GET.get('family_mode') in ['true', '1', 'on']
    selected_amenities = request.GET.getlist('amenity')
    sort_by = request.GET.get('sort', 'newest')
    view_mode = request.GET.get('view', 'grid')  # 'grid' or 'map'
    selected_property_id = request.GET.get('property_id')

    # 1. Filter by Listing Type (rent vs buy)
    if listing_type in ['rent', 'buy']:
        queryset = queryset.filter(listing_type=listing_type)

    # 2. Search query filter
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(title_ar__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # 3. Property Type filter
    if property_type and property_type != 'all':
        queryset = queryset.filter(property_type__iexact=property_type)

    # 4. Bedrooms filter
    if bedrooms == '1':
        queryset = queryset.filter(bedrooms=1)
    elif bedrooms == '2-4':
        queryset = queryset.filter(bedrooms__gte=2, bedrooms__lte=4)
    elif bedrooms == '5+':
        queryset = queryset.filter(bedrooms__gte=5)

    # 5. Price range filter
    if price_range and price_range != 'all':
        price_field = 'buy_price' if listing_type == 'buy' else 'price'
        if listing_type == 'buy':
            if price_range == '<150k':
                queryset = queryset.filter(buy_price__lt=150000)
            elif price_range == '150k-300k':
                queryset = queryset.filter(buy_price__gte=150000, buy_price__lte=300000)
            elif price_range == '300k-500k':
                queryset = queryset.filter(buy_price__gte=300000, buy_price__lte=500000)
            elif price_range == '500k+':
                queryset = queryset.filter(buy_price__gt=500000)
        else:
            if price_range == '<2000':
                queryset = queryset.filter(price__lt=2000)
            elif price_range == '2000-3000':
                queryset = queryset.filter(price__gte=2000, price__lte=3000)
            elif price_range == '3000-4000':
                queryset = queryset.filter(price__gte=3000, price__lte=4000)
            elif price_range == '4000+':
                queryset = queryset.filter(price__gt=4000)

    # 6. Family Mode filter
    if family_mode:
        queryset = queryset.filter(is_family_friendly=True)

    # 7. Amenities filter (JSONField containment)
    if selected_amenities:
        for amenity in selected_amenities:
            queryset = queryset.filter(amenities__contains=[amenity])

    # 8. Sorting
    if sort_by == 'price_asc':
        order_field = 'buy_price' if listing_type == 'buy' else 'price'
        queryset = queryset.order_by(order_field)
    elif sort_by == 'price_desc':
        order_field = '-buy_price' if listing_type == 'buy' else '-price'
        queryset = queryset.order_by(order_field)
    elif sort_by == 'popular':
        queryset = queryset.order_by('-featured', 'posted_days_ago', '-created_at')
    else:  # newest
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
        properties_data.append({
            'id': p.id,
            'title': p.title,
            'title_ar': p.title_ar,
            'description': p.description,
            'description_ar': p.description_ar,
            'price': p.price,
            'buy_price': p.buy_price,
            'listing_type': p.listing_type,
            'rental_period': p.rental_period,
            'property_type': p.property_type,
            'address': p.address,
            'city': p.city,
            'state': p.state,
            'zip_code': p.zip_code,
            'country': p.country,
            'bedrooms': p.bedrooms,
            'bathrooms': p.bathrooms,
            'area_sqft': p.area_sqft,
            'images': p.images or [],
            'featured': p.featured,
            'badge': p.badge,
            'posted_days_ago': p.posted_days_ago,
            'is_family_friendly': p.is_family_friendly,
            'family_highlights': p.family_highlights or [],
            'amenities': p.amenities or [],
            'agent_name': p.agent_name,
            'agent_phone': p.agent_phone,
            'agent_email': p.agent_email,
            'agent_avatar': p.agent_avatar,
            'lat': p.lat,
            'lng': p.lng,
        })

    all_amenities_list = [
        "Swimming Pool", "Garage", "Air Conditioning", "Balcony",
        "Garden", "Pet Friendly", "Furnished", "High-speed WiFi"
    ]

    context = {
        'properties': queryset,
        'properties_json': json.dumps(properties_data),
        'count': queryset.count(),
        'selected_property': selected_property,
        'search_query': search_query,
        'listing_type': listing_type,
        'property_type': property_type,
        'bedrooms': bedrooms,
        'price_range': price_range,
        'family_mode': family_mode,
        'selected_amenities': selected_amenities,
        'sort_by': sort_by,
        'view_mode': view_mode,
        'all_amenities_list': all_amenities_list,
        'property_form': PropertyForm(),
        'tour_form': TourBookingForm(),
    }
    return render(request, 'properties/index.html', context)

def property_detail(request, pk):
    """Dedicated Detail Page for SEO and direct links"""
    prop = get_object_or_404(Property, pk=pk)
    context = {
        'property': prop,
        'tour_form': TourBookingForm(initial={'property': prop}),
    }
    return render(request, 'properties/detail.html', context)

def property_create(request):
    """Handle new property submission from frontend modal"""
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            new_prop = form.save()
            messages.success(request, f"Property '{new_prop.title}' has been successfully listed!")
            return redirect(f"/?listing_type={new_prop.listing_type}")
        else:
            messages.error(request, "Please correct the errors in the form.")
    return redirect('/')
