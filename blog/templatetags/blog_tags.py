from django import template
from ..models import Post, Comment
from django.db.models import Count
from markdown import markdown
from django.utils.safestring import mark_safe
register = template.Library()


@register.simple_tag()
def total_posts():
    return Post.published.count()


@register.simple_tag()
def total_comments():
    return Comment.objects.filter(active=True).count()


@register.simple_tag()
def last_post_date():
    return Post.published.last().publish


@register.simple_tag()
def most_popular_posts(count=3):
    return Post.published.annotate(comments_count=Count('comments')).order_by('-comments_count')[:count]


@register.inclusion_tag("partials/latest_posts.html")
def latest_posts(count=4):
    lasts_post = Post.published.order_by('-publish')[:count]
    context = {
        'lasts_post': lasts_post
    }
    return context


@register.filter(name='markdown')
def to_markdown(text):
    return mark_safe(markdown(text))


@register.inclusion_tag("partials/maximum_reading_time.html")
def max_reading_time(count=3):
    max_post = Post.published.order_by('-reading_time')[:count]
    context = {
        'max_post': max_post
    }
    return context


@register.inclusion_tag("partials/min_reading_time.html")
def min_reading_time(count=3):
    min_post = Post.published.order_by('reading_time')[:count]
    context = {
        'min_post': min_post
    }
    return context


@register.filter(name='censor')
def to_censorship(text):
    censor_list = ['بیشعور', 'احمق', 'اشغال', 'کصافت', 'بی تربیت', 'خنگ', 'عوضی']
    for word in censor_list:
        text = text.replace(word, '*' * len(word))
    return text
