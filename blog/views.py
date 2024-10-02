from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, FormView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
# Create your views here.
import datetime


def index(request):
    return render(request, "blog/index.html")


# def post_list(request):
#     posts = Post.published.all()
#     paginator = Paginator(posts, 2)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     context = {
#         "posts": posts,
#     }
#     return render(request, "blog/post_list.html", context)

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post_list.html"


def post_detail(request, pk):
    # try:
    #     post = Post.published.get(id=id)
    # except:
    #     raise Http404("No Post Found!!")
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    context = {
        "post": post,
        "form": form,
        "comments": comments
    }
    return render(request, "blog/post_detail.html", context)


# class PostDetailView(DetailView):
#     model = Post
#     template_name = "blog/post_detail.html"


def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            ticket_obj = Ticket.objects.create(message=cd['message'], name=cd['name'], email=cd['email']
                                               , phone=cd['phone'], subject=cd['subject'])
            # ticket_obj.message = cd['message']
            # ticket_obj.name = cd['name']
            # ticket_obj.email = cd['email']
            # ticket_obj.phone = cd['phone']
            # ticket_obj.subject = cd['subject']
            # ticket_obj.save()
            return redirect("blog:ticket")
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post': post,
        'form': form,
        'comment': comment
    }
    return render(request, "forms/comment.html", context)


def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.status = 'DF'
            post.save()
            return redirect("blog:post_list")
    else:
        form = PostForm()
    return render(request, "forms/new_post.html", {'form': form})


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_query = SearchQuery(query)
            # ------------ way 1-------------
            # results1 = Post.published.filter(title__icontains=query)
            # results2 = Post.published.filter(description__icontains=query)
            # results = results1 | results2
            # ------------ way 2-------------
            # results = Post.published.filter(Q(title__search=query) | Q(description__search=query))
            # ------------ way 3-------------
            # search_vector = SearchVector('title', 'description', 'slug')
            # results = (Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))
            #            .filter(search=search_query)).order_by('-rank')
            # ------------ way 4-------------
            search_vector = (SearchVector('title', weight="A") + SearchVector('description', weight="B")
                             + SearchVector('slug', weight="D"))
            results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)). \
                filter(rank__gte=0.3).order_by('-rank')
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'blog/search.html', context)
