from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import TourBookingForm

def book_tour(request):
    if request.method == 'POST':
        form = TourBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_authenticated:
                booking.user = request.user
            booking.save()
            msg = "Tour Request Confirmed! The agent will contact you shortly."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
                return JsonResponse({'success': True, 'message': msg, 'booking_id': booking.id})
            messages.success(request, msg)
        else:
            err_msg = "Please check the tour booking form fields."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            messages.error(request, err_msg)
            
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)
