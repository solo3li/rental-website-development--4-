from django import forms
from .models import RoommatePost

class RoommatePostForm(forms.ModelForm):
    class Meta:
        model = RoommatePost
        fields = [
            'student_name',
            'gender',
            'university',
            'faculty',
            'academic_year',
            'target_area',
            'budget_max_egp',
            'move_in_date',
            'sleep_habit',
            'smoking',
            'bio',
            'contact_phone',
            'whatsapp_number',
        ]
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': 'اسمك بالكامل'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm'}),
            'university': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm'}),
            'faculty': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': 'مثال: هندسة القاهرة / طب بشري'}),
            'academic_year': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': 'مثال: الفرقة الأولى / إعدادي'}),
            'target_area': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': 'مثال: بين السرايات، الدقي، مدينة نصر'}),
            'budget_max_egp': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': '2500'}),
            'move_in_date': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': 'مثال: أول شهر أكتوبر'}),
            'sleep_habit': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': 'مثال: نوم مبكر / هدوء للدراسة'}),
            'smoking': forms.CheckboxInput(attrs={'class': 'rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'rows': 3, 'placeholder': 'اكتب نبذة عن طبيعتك ومواصفات السكن والزميل الذي تبحث عنه'}),
            'contact_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': '010XXXXXXXX'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm', 'placeholder': '010XXXXXXXX'}),
        }
