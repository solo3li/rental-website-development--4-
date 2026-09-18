from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import RoommatePost
from .forms import RoommatePostForm
from apps.properties.models import University

def roommate_list(request):
    posts = RoommatePost.objects.filter(is_active=True).select_related('university')
    universities = University.objects.all()

    # Query Filters
    gender = request.GET.get('gender')
    university_id = request.GET.get('university')
    search = request.GET.get('search', '').strip()
    max_budget = request.GET.get('max_budget')

    if gender in ['female', 'male']:
        posts = posts.filter(gender=gender)

    if university_id and university_id != 'all':
        posts = posts.filter(university_id=university_id)

    if search:
        posts = posts.filter(
            Q(student_name__icontains=search) |
            Q(faculty__icontains=search) |
            Q(target_area__icontains=search) |
            Q(bio__icontains=search)
        )

    if max_budget:
        try:
            posts = posts.filter(budget_max_egp__lte=int(max_budget))
        except ValueError:
            pass

    # Handle Form Submission for new post
    if request.method == 'POST':
        form = RoommatePostForm(request.POST)
        if form.is_valid():
            post = form.save()
            messages.success(request, 'تم نشر طلبك بنجاح! سيتمكن الطلاب المتوافقون معك من التواصل معك مباشرة.')
            return redirect('roommates:list')
        else:
            messages.error(request, 'يرجى التأكد من صحة البيانات المدخلة في النموذج.')
    else:
        initial_data = {}
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            p = request.user.profile
            initial_data = {
                'student_name': request.user.get_full_name() or request.user.username,
                'gender': p.gender,
                'university': p.university,
                'faculty': p.faculty,
                'academic_year': p.academic_year,
                'contact_phone': p.phone,
                'whatsapp_number': p.whatsapp or p.phone,
            }
        form = RoommatePostForm(initial=initial_data)

    context = {
        'posts': posts,
        'universities': universities,
        'form': form,
        'selected_gender': gender or 'all',
        'selected_university': university_id or 'all',
        'search_query': search,
        'max_budget': max_budget or '',
    }
    return render(request, 'roommates/list.html', context)


def roommate_detail(request, pk):
    from django.shortcuts import get_object_or_404
    post = get_object_or_404(RoommatePost.objects.select_related('university'), pk=pk)
    similar_posts = RoommatePost.objects.filter(
        gender=post.gender, is_active=True
    ).exclude(pk=post.pk).select_related('university')[:3]

    context = {
        'post': post,
        'similar_posts': similar_posts,
    }
    return render(request, 'roommates/detail.html', context)
