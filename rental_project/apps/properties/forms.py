from django import forms
from .models import Property, University, MetroStation

class PropertyForm(forms.ModelForm):
    images_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'ضع روابط الصور مفصولة بفواصل أو سطور جديدة (اختياري)',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-xs'
        })
    )
    amenities_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'تكييف، مروحة، ثلاجة، سخان، غسالة، شرفة...',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-xs'
        })
    )
    floor_number = forms.IntegerField(
        required=False,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '1'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': 'English description (optional)'})
    )
    deposit_egp = forms.DecimalField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '1000'})
    )
    total_capacity = forms.IntegerField(
        required=False,
        initial=4,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '4'})
    )
    walking_minutes = forms.IntegerField(
        required=False,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '10'})
    )

    class Meta:
        model = Property
        fields = [
            'title_ar', 'title',
            'gender_policy', 'rental_type',
            'price_egp', 'deposit_egp', 'bills_included',
            'total_capacity', 'available_beds',
            'university', 'nearest_metro', 'walking_minutes',
            'address', 'city',
            'floor_number', 'has_elevator',
            'study_desk', 'wifi_speed', 'curfew_time', 'is_supervised',
            'agent_name', 'agent_phone', 'whatsapp_number',
            'description_ar', 'description',
        ]
        widgets = {
            'title_ar': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': 'مثال: سكن طالبات راقي ومفروش بالدقي'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': 'English title (optional)'}),
            'gender_policy': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs'}),
            'rental_type': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs'}),
            'price_egp': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '2500'}),
            'deposit_egp': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '2000'}),
            'bills_included': forms.CheckboxInput(attrs={'class': 'rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4'}),
            'total_capacity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '4'}),
            'available_beds': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '2'}),
            'university': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs'}),
            'nearest_metro': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs'}),
            'walking_minutes': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '10'}),
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': 'الشارع والحي'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': 'الدقي / بين السرايات / مدينة نصر'}),
            'floor_number': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '3'}),
            'has_elevator': forms.CheckboxInput(attrs={'class': 'rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4'}),
            'study_desk': forms.CheckboxInput(attrs={'class': 'rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4'}),
            'wifi_speed': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '30 Mbps فايبر'}),
            'curfew_time': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '11:00 مساءً أو مفتوح'}),
            'is_supervised': forms.CheckboxInput(attrs={'class': 'rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4'}),
            'agent_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': 'اسمك / مشرف السكن'}),
            'agent_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '010XXXXXXXX'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': '010XXXXXXXX'}),
            'description_ar': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': 'اكتب وصفاً تفصيلياً للسكن وقواعد الإقامة'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs', 'placeholder': 'English description (optional)'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.title:
            instance.title = instance.title_ar
        if not instance.description:
            instance.description = instance.description_ar
        instance.price = instance.price_egp

        img_raw = self.cleaned_data.get('images_text', '')
        if img_raw:
            urls = [u.strip() for u in img_raw.replace('\n', ',').split(',') if u.strip()]
            instance.images = urls
        elif not instance.images:
            instance.images = ["https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200"]

        amenities_raw = self.cleaned_data.get('amenities_text', '')
        if amenities_raw:
            instance.amenities = [a.strip() for a in amenities_raw.split(',') if a.strip()]
        elif not instance.amenities:
            instance.amenities = ["إنترنت فائق السرعة Wi-Fi", "مكتب مذاكرة", "غسالة ملابس", "مطبخ مجهز بالكامل"]

        if commit:
            instance.save()
        return instance
