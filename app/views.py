from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Video

def fetch(request):
    data = Video.objects.all().order_by('-published_at')
    paginator = Paginator(data, 7)
    page = request.GET.get('page')
    try:
        result = paginator.get_page(page)
    except PageNotAnInteger:
        result = paginator.get_page(1)
    except EmptyPage:
        result = paginator.get_page(paginator.num_pages)
    return render(request, 'index.html', { "data": result })

def search(request):
    search_term = request.GET.get('q')
    data_title = Video.objects.filter(title__icontains=search_term.lower())
    data_desc = Video.objects.filter(description__icontains=search_term.lower())
    data = data_title | data_desc
    paginator = Paginator(data, 7)
    page = request.GET.get('page')
    try:
        result = paginator.get_page(page)
    except PageNotAnInteger:
        result = paginator.get_page(1)
    except EmptyPage:
        result = paginator.get_page(paginator.num_pages)
    return render(request, 'search.html', { "data": result , "search_query": search_term })
