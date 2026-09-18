from django.shortcuts import redirect

def switch_language(request):
    lang = request.GET.get('lang', 'en')
    if lang in ['en', 'ar']:
        request.session['lang'] = lang
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)
