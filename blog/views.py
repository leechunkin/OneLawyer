from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Category, Post

PAGE_SIZE = 10

def index(request, category=None):
	search = request.GET.get('search') if request.method == 'GET' else None
	if search == '':
		search = None
	if category is None:
		posts = Post.objects.all()
	else:
		posts = Post.objects.filter(categories__id=category)
	if search:
		posts = posts.filter(
			Q(title__icontains=search) |
			Q(summary__icontains=search) |
			Q(content__icontains=search)
		)
	try:
		page = int(request.GET.get('page'))
	except ValueError:
		page = 1
	except TypeError:
		page = 1
	post_last = page * PAGE_SIZE
	post_first = post_last - PAGE_SIZE
	context = {
		'categories': Category.objects.all(),
		'posts': posts[post_first:post_last],
		'page': page,
		'newer': page-1 if page > 1 else None,
		'older': page+1 if post_last < Post.objects.count() else None,
		'search': search or ''
	}
	return render(request, 'blog/index.html', context)

def article(request, article):
	try:
		post = Post.objects.get(id=article)
	except LawyerPost.DoesNotExist:
		raise Http404("Blog article not found")
	context = {
		'post': post
	}
	return render(request, 'blog/article.html', context)
