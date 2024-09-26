from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView,DetailView,FormView
# Create your views here.


def index(request):
    return HttpResponse("index")


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

# import datetime
# def post_detail(request, id):
#     # try:
#     #     post = Post.published.get(id=id)
#     # except:
#     #     raise Http404("No Post Found!!")
#     post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
#
#     context = {
#         "post": post,
#         "new_date": datetime.datetime.now(),
#     }
#     return render(request, "blog/post_detail.html", context)


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"


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
    return render(request, "forms/ticket.html", {'form':form})