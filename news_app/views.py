from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from django.views.generic import TemplateView,ListView
from .models import News,Category
from .forms import ContactForm

def news_list(request):
    #news_list = News.objects.filter(status=News.Status.Published)
    news_list = News.published.all()
    context = {
        'news_list': news_list
    }
    return render(request,'news/news_list.html',context)

def news_detail(request,news):
    news = get_object_or_404(News, slug=news, status=News.Status.Published)
    context = {
        'news': news
    }
    return render(request,'news/news_detail.html', context)
    
'''def homePageView(request):
    categories = Category.objects.all()
    news_list = News.published.all().order_by('-publish_time')
    world_one = News.published.filter(category__name='World').order_by('-publish_time')[:1]
    world_news = News.published.all().filter(category__name='World').order_by('-publish_time')[::5]
    context = {
        'news_list ': news_list,
        'categories': categories,
        'world_news': world_news,
        'world_one': world_one,
    }

    return render(request, 'news/home.html', context)
'''

class HomePageView(ListView):    
    model = News
    template_name = 'news/home.html'
    
    def get_context_data(self, **kwagrs):
        context = super().get_context_data(**kwagrs)
        context['news_list'] = News.published.all()[:5]
        context['categories'] = Category.objects.all()
        context['world_news'] = News.published.all().filter(category__name='World').order_by('-publish_time')[:5]
        context['local_news'] = News.published.all().filter(category__name='Our Country').order_by('-publish_time')[:5]
        context['sport_news'] = News.published.all().filter(category__name='Sport').order_by('-publish_time')[:5]
        context['technology_news'] = News.published.all().filter(category__name='Technology').order_by('-publish_time')[:5]
        return context

'''def contactPageView(request):
    print(request.POST)
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponse("<h2> Biz bilan bog'langaningiz uchun tashakur!</h2>")
    context = {
        'form': form
    }
    return render(request, 'news/contact.html',context=context)
'''

class ContactPageView(TemplateView):
    template_name = 'news/contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        context = {
            'form': form
        }
        return render(request, 'news/contact.html', context)
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return HttpResponse("<h2> Biz bilan bog'langaningiz uchun tashakur!</h2>")
        context = {
            'form': form
        }
        return render(request, 'news/contact.html', context)

class LocalNewsView(ListView):
    model = News
    template_name = 'news/local.html'
    context_object_name = 'local_news'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='Our Country')
        return news

class ForeignNewsView(ListView):
    model = News
    template_name = 'news/world.html'
    context_object_name = 'world_news'
   
    def get_queryset(self):
        news = self.model.published.all().filter(category__name='World')
        return news   

class TechnologyNewsView(ListView):
    model = News
    template_name = 'news/technology.html'
    context_object_name = 'technology_news'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='Technology')
        return news

class SportNewsView(ListView):
    model = News
    template_name = 'news/sport.html'
    context_object_name = 'sport_news'
    
    def get_queryset(self):
        news = self.model.published.all().filter(category__name='Sport')
        return news

# POST --> вставить
# GET --> получить 