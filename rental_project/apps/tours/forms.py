from django import forms
from .models import TourBooking, DepositReceipt, PaymentSettings

class TourBookingForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=DepositReceipt.PAYMENT_METHODS,
        required=False,
        initial='instapay',
        widget=forms.Select(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none'
        })
    )
    sender_info = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none',
            'placeholder': 'رقم المحفظة أو اسم الحساب المحول منه'
        })
    )
    reference_number = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none',
            'placeholder': 'الرقم المرجعي للتحويل (اختياري)'
        })
    )
    receipt_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'id': 'receiptImageInput'
        })
    )

    class Meta:
        model = TourBooking
        fields = ['property', 'full_name', 'email', 'phone', 'tour_date', 'tour_type', 'message']
        widgets = {
            'property': forms.HiddenInput(),
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'محمد أحمد'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'student@cairo.edu.eg'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': '010XXXXXXXX'
            }),
            'tour_date': forms.TextInput(attrs={
                'type': 'date',
                'class': 'w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none'
            }),
            'tour_type': forms.Select(attrs={
                'class': 'w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none'
            }),
            'message': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'أي أسئلة أو ملاحظات خاصة...'
            }),
        }

    def clean_receipt_image(self):
        image = self.cleaned_data.get('receipt_image')
        try:
            settings = PaymentSettings.get_settings()
            if settings.is_deposit_required and not image:
                raise forms.ValidationError("يرجى إرفاق لقطة شاشة لإيصال التحويل (Screenshot) لتأكيد جدية المعاينة.")
        except forms.ValidationError:
            raise
        except Exception:
            pass

        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("حجم الصورة كبير جداً، الحد الأقصى المسموح به 5 ميجابايت.")
        return image
