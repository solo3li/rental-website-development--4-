from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import TourBookingForm
from .models import PaymentSettings, DepositReceipt

def book_tour(request):
    if request.method == 'POST':
        form = TourBookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_authenticated:
                booking.user = request.user
            booking.status = 'pending'
            booking.save()

            settings = PaymentSettings.get_settings()
            receipt_img = form.cleaned_data.get('receipt_image')
            if receipt_img:
                DepositReceipt.objects.create(
                    booking=booking,
                    amount=settings.deposit_amount_egp,
                    payment_method=form.cleaned_data.get('payment_method') or 'instapay',
                    sender_info=form.cleaned_data.get('sender_info') or '',
                    reference_number=form.cleaned_data.get('reference_number') or '',
                    receipt_image=receipt_img,
                    status='pending',
                )

            msg = "تم استلام طلب المعاينة وإيصال التحويل بنجاح! سيتم مراجعته وتأكيد الموعد فوراً."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
                return JsonResponse({'success': True, 'message': msg, 'booking_id': booking.id})
            messages.success(request, msg)
        else:
            err_msg = "يرجى التحقق من صحة البيانات وإرفاق صورة إيصال التحويل."
            first_err = next(iter(form.errors.values()))[0] if form.errors else err_msg
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
                return JsonResponse({'success': False, 'message': str(first_err), 'errors': form.errors}, status=400)
            messages.error(request, str(first_err))
            
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)
