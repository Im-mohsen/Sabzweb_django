from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, FormView
from django.views.decorators.http import require_POST
from django.db.models import Q
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from random import choice
# Create your views here.
import datetime


def index(request):
    random_posts = choice(Post.objects.all()) if Post.objects.all() else None
    return render(request, "blog/index.html", {'random_posts': random_posts})


def post_list(request, category=None):
    if category is not None:
        posts = Post.objects.filter(category=category)
    else:
        posts = Post.published.all()
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
    context = {
        "posts": posts,
        "category": category,
    }
    return render(request, "blog/post_list.html", context)

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = "posts"
#     paginate_by = 3
#     template_name = "blog/post_list.html"


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


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            return redirect("blog:profile")
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
            # search_query = SearchQuery(query)
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
            # search_vector = (SearchVector('title', weight="A") + SearchVector('description', weight="B")
            #                  + SearchVector('slug', weight="D"))
            # results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)). \
            #     filter(rank__gte=0.3).order_by('-rank')
            # ------------ way 5-------------A
            # results = Post.published.annotate(similarity=TrigramSimilarity('title', query)).\
            #     filter(similarity__gt=0.1).order_by('-similarity')
            # ------------ way 5-------------B
            results1 = Post.published.annotate(similarity=TrigramSimilarity('title', query)).\
                filter(similarity__gt=0.1)
            results2 = Post.published.annotate(similarity=TrigramSimilarity('description', query)).\
                filter(similarity__gt=0.1)
            results3 = Post.published.annotate(similarity=TrigramSimilarity('images__title', query)).\
                filter(similarity__gt=0.1)
            results4 = Post.published.annotate(similarity=TrigramSimilarity('images__description', query)).\
                filter(similarity__gt=0.1)
            results = (results1 | results2 | results3 | results4).order_by('-similarity')

    context = {
        'query': query,
        'results': results
    }
    return render(request, 'blog/search.html', context)


@login_required
def profile(request):
    user = request.user
    pub_posts = Post.published.filter(author=user)
    all_posts = Post.objects.filter(author=user)

    # صفحه بندی
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(page_number.num_pages)
    except PageNotAnInteger:
        page_obj = paginator.page(1)

    context = {
        'page_obj': page_obj,
        'pub_posts': pub_posts,
    }

    return render(request, 'blog/profile.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile')
    return render(request, 'forms/delete_post.html', {'post': post})


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    image.delete()
    return redirect('blog:profile')


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            return redirect("blog:profile")
    else:
        form = PostForm(instance=post)
    return render(request, "forms/new_post.html", {'form': form, 'post': post})


# Way number 1 to make login view
# def user_login(request):
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request, username=cd['username'], password=cd['password'])
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect("blog:profile")
#                 else:
#                     return HttpResponse("Your account is disabled.")
#             else:
#                 return HttpResponse("Invalid login.")
#     else:
#         form = LoginForm()
#     return render(request, "forms/login.html", {'form': form})

# def log_out(request):
#     logout(request)
#     return redirect(request.META.get('HTTP_REFERER'))

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Account.objects.create(user=user)
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = UserRegisterForm()
    return render(request, "registration/register.html", {'form': form})


@login_required
def edit_account(request):
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        account_form = AccountEditForm(request.POST, files=request.FILES, instance=request.user.account)
        if account_form.is_valid() and user_form.is_valid():
            account_form.save()
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        account_form = AccountEditForm(instance=request.user.account)
    context = {
        "account_form": account_form,
        "user_form": user_form
    }
    return render(request, 'registration/edit_account.html', context)


def author_profile(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    posts = Post.published.filter(author__username=username)
    context = {
        "user": user,
        "posts": posts
    }
    return render(request, 'blog/author_profile.html', context)