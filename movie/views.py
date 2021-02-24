from django.shortcuts import render
from django.views.generic import ListView , DetailView
from django.views.generic.dates import YearArchiveView
from .models import Movie , MovieLinks
from wsgiref.util import FileWrapper
import os
from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from Ashik.settings import MEDIA_ROOT
# Create your views here.

class VideoFileView(View):
    
    def get(self, request,id):
        movie_by_id = Movie.objects.get(id=id)
        file_name = MovieLinks.objects.filter(movie = movie_by_id)[0].link
        if movie_by_id :
            file = FileWrapper(open(MEDIA_ROOT+'\\'+file_name, 'rb'))
            response = HttpResponse(file, content_type='video/mp4')
            response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
            return response
        else:
            return HttpResponse("<p>Download is not available</p>")


class VideoView(View):
    template_name = 'movie/show.html'

    def get(self, request, id):
        #fetch video from DB by ID
        movie_by_id = Movie.objects.get(id=id)
        link = MovieLinks.objects.filter(movie = movie_by_id)[0].link
        MEDIA_URL = "/media/"
        if movie_by_id:
            context = {'movie':movie_by_id,
            'media':MEDIA_URL,
            'link' :link
            }
            return render(request, self.template_name, context)
        else:
            return HttpResponse("<p>show is not available</p>")


class HomeView(ListView):
    model = Movie
    template_name = 'movie/home.html'

    def get_context_data(self , **kwargs):
        context = super(HomeView , self).get_context_data(**kwargs)
        context['top_rated'] = Movie.objects.filter(status='TR')
        context['most_watched'] = Movie.objects.filter(status='MW')
        context['recently_added'] = Movie.objects.filter(status='RA') 
        return context


class MovieList(ListView):
    model = Movie
    paginate_by = 2


class MovieDetail(DetailView):
    model = Movie

    def get_object(self):
        self.object = super(MovieDetail , self).get_object()
        return self.object

    def get_context_data(self , **kwargs):
        context = super(MovieDetail , self).get_context_data(**kwargs)
        context['links'] = MovieLinks.objects.filter(movie=self.get_object())
        context['related_movies'] = Movie.objects.filter(category=self.get_object().category)#.order_by['created'][0:6]
        self.object.views_count += 1
        self.object.save()
        return context


class MovieCategory(ListView):
    model = Movie
    paginate_by = 2

    def get_queryset(self):
        self.category = self.kwargs['category']
        return Movie.objects.filter(category=self.category)

    def get_context_data(self , **kwargs):
        context = super(MovieCategory , self).get_context_data(**kwargs)
        context['movie_category'] = self.category
        return context



class MovieLanguage(ListView):
    model = Movie
    paginate_by = 2

    def get_queryset(self):
        self.language = self.kwargs['lang']
        return Movie.objects.filter(language=self.language)

    def get_context_data(self , **kwargs):
        context = super(MovieLanguage , self).get_context_data(**kwargs)
        context['movie_language'] = self.language
        return context




class MovieSearch(ListView):
    model = Movie
    paginate_by = 2

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            object_list = self.model.objects.filter(title__icontains=query)
        
        else:
            object_list = self.model.objects.none()

        return object_list

class MovieYear(YearArchiveView):
    queryset = Movie.objects.all()
    date_field = 'year_of_production'
    make_object_list = True
    allow_future = True
    template_name = "movie\movie_archive_year.html"

    
    def get_dated_queryset(self, **lookup):
        qs = self.get_queryset().filter(**lookup)
        date_field = self.get_date_field()
        allow_future = self.get_allow_future()
        allow_empty = self.get_allow_empty()
        paginate_by = self.get_paginate_by(qs)
        if not allow_future:
            now = timezone.now() if self.uses_datetime_field else timezone_today()
            qs = qs.filter(**{'%s__lte' % date_field: now})
       
        return qs

    def get_date_list(self, queryset, date_type=None, ordering='ASC'):
        date_field = self.get_date_field()
        allow_empty = self.get_allow_empty()
        if date_type is None:
            date_type = self.get_date_list_period()
        if self.uses_datetime_field:
            date_list = queryset.datetimes(date_field, date_type, ordering)
        else:
            date_list = queryset.dates(date_field, date_type, ordering)
    
        return date_list

    def get_queryset(self):
        try:
            queryset = super(MovieYear,self).get_queryset()
        except:
            queryset = None
        return queryset

    def get_context_data(self , **kwargs):
        context = super(MovieYear , self).get_context_data(**kwargs)
        return context
