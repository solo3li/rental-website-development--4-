from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    images_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Paste image URLs separated by commas or newlines',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    amenities_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Swimming Pool, Garage, Air Conditioning, Balcony...',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    class Meta:
        model = Property
        fields = [
            'title', 'title_ar', 'description', 'description_ar',
            'listing_type', 'property_type', 'price', 'buy_price',
            'address', 'city', 'state', 'zip_code',
            'bedrooms', 'bathrooms', 'area_sqft',
            'agent_name', 'agent_phone', 'agent_email',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'title_ar': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'description_ar': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'listing_type': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'property_type': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'buy_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'state': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'zip_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'area_sqft': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'agent_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'agent_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'agent_email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        img_raw = self.cleaned_data.get('images_text', '')
        if img_raw:
            urls = [u.strip() for u in img_raw.replace('\n', ',').split(',') if u.strip()]
            instance.images = urls
        elif not instance.images:
            instance.images = ["https://images.pexels.com/photos/8134745/pexels-photo-8134745.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200"]

        amenities_raw = self.cleaned_data.get('amenities_text', '')
        if amenities_raw:
            instance.amenities = [a.strip() for a in amenities_raw.split(',') if a.strip()]

        if commit:
            instance.save()
        return instance
