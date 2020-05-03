from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Video

def fetch(request):
    data = Video.objects.all().order_by('-published_at')
    paginator = Paginator(data, 20)
    page = request.GET.get('page')
    try:
        result = paginator.get_page(page)
    except PageNotAnInteger:
        result = paginator.get_page(1)
    except EmptyPage:
        result = paginator.get_page(paginator.num_pages)
    return render(request, 'index.html', { "data": result })
