from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,Http404
from django.views.generic import TemplateView,ListView,UpdateView,DeleteView,CreateView,DetailView
from .models import News,Category
from .forms import ContactForm,CommentForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from news_project.custom_permissions import OnlyLoggedSuperUser
from django.contrib.auth.models import User
from django.db.models import Q
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountDetailView,HitCountMixin

def news_list(request):
    #news_list = News.objects.filter(status=News.Status.Published)
    news_list = News.published.all()
    context = {
        'news_list': news_list
    }
    return render(request,'news/news_list.html',context)

def news_detail(request,news):
    news = get_object_or_404(News, slug=news, status=News.Status.Published)
    context = {}
    #hitcount logic
    hit_count = get_hitcount_model().objects.get_for_object(news)
    hits = hit_count.hits
    hitcontext = context['hitcount'] = {'pk': hit_count.pk}
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if hit_count_response.hit_counted:
        hits = hits + 1
        hitcontext['hit_counted'] = hit_count_response.hit_counted
        hitcontext['hit_message'] = hit_count_response.hit_message
        hitcontext['total_hits'] = hits

    comments = news.comments.filter(active=True)
    comment_count = comments.count()
    new_comment = None
    

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # new comment object, but we don't save in DataBase
            new_comment = comment_form.save(commit=False)
            new_comment.news = news
            # comment jeberib atirgan userdi biriktirip qoydiq  
            new_comment.user = request.user
            # Database saqlaymiz
            new_comment.save()
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    
    context = {
        'news': news,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'comment_count': comment_count,       
    }
    return render(request,'news/news_detail.html', context)

class NewsDetailView(DetailView):
    model = News
    template_name = 'news/news_detail.html'
    
    def get_object(self):
        return get_object_or_404(News, slug=news, status=News.Status.Published)
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news'] = get_object_or_404(self.model)

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

class NewsUpdateView(OnlyLoggedSuperUser,UpdateView):
    model = News
    fields = ('title','body','image','category','status',)
    template_name = 'crud/news_edit.html'

class NewsDeleteView(OnlyLoggedSuperUser,DeleteView):
    model = News
    template_name = 'crud/news_delete.html'
    success_url = reverse_lazy('home_page')

class NewsCreateView(OnlyLoggedSuperUser,CreateView):
    model = News
    fields = ('title','body','image','category','status',)
    template_name = 'crud/news_edit.html'

@login_required
@user_passes_test(lambda user:user.is_superuser)
def admin_page(request):
    admin_users = User.objects.filter(is_superuser=True)
    context = {
        'admin_users': admin_users
    }
    return render(request, 'pages/admin_page.html', context)
    
class SearchResultList(ListView):
    model = News
    template_name = 'news/search_result.html'
    context_object_name = 'all_news'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return News.objects.filter(Q(title__icontains=query) | Q(body__icontains=query))

# POST --> вставить
# GET --> получить 