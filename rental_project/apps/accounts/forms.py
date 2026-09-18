from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from apps.properties.models import University

class StudentRegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'الاسم الأول'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'اسم العائلة'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'البريد الإلكتروني (يفضل الجامعي)'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'كلمة المرور (6 أحرف على الأقل)'
    }))
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, widget=forms.Select(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm'
    }))
    university = forms.ModelChoiceField(queryset=University.objects.all(), required=False, widget=forms.Select(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm'
    }))
    faculty = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'الكلية والتخصص (مثال: هندسة القاهرة)'
    }))
    academic_year = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'الفرقة الأولى / الثانية...'
    }))
    phone = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': '010XXXXXXXX'
    }))
    whatsapp = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': '010XXXXXXXX'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل بالفعل.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'].split('@')[0] + "_" + User.objects.make_random_password(4)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            profile = user.profile
            profile.user_type = 'student'
            profile.gender = self.cleaned_data['gender']
            profile.university = self.cleaned_data['university']
            profile.faculty = self.cleaned_data['faculty']
            profile.academic_year = self.cleaned_data['academic_year']
            profile.phone = self.cleaned_data['phone']
            profile.whatsapp = self.cleaned_data['whatsapp'] or self.cleaned_data['phone']
            profile.save()
        return user


class LandlordRegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'اسم المسؤول / المالك'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'اسم العائلة'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'البريد الإلكتروني'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'كلمة المرور'
    }))
    company_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'اسم مكتب إدارة السكن أو العقار'
    }))
    phone = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'رقم هاتف الاتصال المباشر'
    }))
    whatsapp = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'رقم الواتساب لاستقبال استفسارات الطلاب'
    }))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'rows': 3,
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'نبذة عن السكن الطلابي الذي تديره ومواقعه في القاهرة...'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل بالفعل.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'].split('@')[0] + "_" + User.objects.make_random_password(4)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            profile = user.profile
            profile.user_type = 'landlord'
            profile.company_name = self.cleaned_data['company_name']
            profile.phone = self.cleaned_data['phone']
            profile.whatsapp = self.cleaned_data['whatsapp']
            profile.bio = self.cleaned_data['bio']
            profile.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'البريد الإلكتروني أو اسم المستخدم'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 text-xs sm:text-sm',
        'placeholder': 'كلمة المرور'
    }))


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50, required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
            'placeholder': 'الاسم الأول'
        })
    )
    last_name = forms.CharField(
        max_length=50, required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
            'placeholder': 'اسم العائلة'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['phone', 'whatsapp', 'avatar', 'gender', 'university', 'faculty', 'academic_year', 'company_name', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
                'placeholder': '010XXXXXXXX'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
                'placeholder': '010XXXXXXXX'
            }),
            'avatar': forms.URLInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
                'placeholder': 'https://...'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400'
            }),
            'university': forms.Select(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400'
            }),
            'faculty': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
                'placeholder': 'الكلية والتخصص (مثال: هندسة القاهرة)'
            }),
            'academic_year': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
                'placeholder': 'الفرقة الأولى / الثانية...'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
                'placeholder': 'اسم الشركة أو المكتب'
            }),
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-slate-400',
                'placeholder': 'نبذة عنك...'
            }),
        }
