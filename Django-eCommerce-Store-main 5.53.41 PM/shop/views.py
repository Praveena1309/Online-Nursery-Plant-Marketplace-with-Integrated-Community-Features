from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
from .models import Product, Category
from cart.views import _cart_id
from cart.models import CartItem
from .models import ReviewRating
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
from .models import ProductGallery
from django.shortcuts import render, redirect
from .forms import UploadForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UploadForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Upload, Comment
# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .forms import UploadForm
from .models import Upload
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.utils import timezone


def home(request):
    products = Product.objects.all().filter(is_available=True)
    
    context = {
        'products' : products,
    }
    return render(request, 'shop/index.html', context)

def contact(request):
   
    return render(request, 'shop/shop/contactform.html')

def about(request):
   
    return render(request, 'shop/shop/about.html')


def blog(request):
    
    Asset_Dateils_All=Upload.objects.all() 
    requested_by=Upload.requested_by
    caption=Upload.caption
    image=Upload.image

    return render(request, 'shop/shop/blog.html',{'requested_by':requested_by,'caption':caption,'image':image ,'Asset_Dateils_All':Asset_Dateils_All})



def like_asset(request):
    if request.method == 'POST':
        asset_id = request.POST.get('asset_id')
        session_key = request.session.session_key
        
        if session_key:
            if not Session.objects.filter(session_key=session_key, expire_date__gte=timezone.now()).exists():
                # Session expired or not valid, create a new session
                request.session.save()
                
            liked_assets = request.session.get('liked_assets', [])
            if asset_id in liked_assets:
                # User already liked this post
                return JsonResponse({'error': 'You have already liked this post'})
            
            asset = Upload.objects.get(pk=asset_id)
            asset.rating += 1
            asset.save()
            
            liked_assets.append(asset_id)
            request.session['liked_assets'] = liked_assets
            return JsonResponse({'rating': asset.rating})
        else:
            return JsonResponse({'error': 'Session key not found'})
    else:
        return JsonResponse({'error': 'Invalid request method'})

def comment_asset(request):
    if request.method == 'POST':
        asset_id = request.POST.get('asset_id')
        comment_text = request.POST.get('comment_text')
        username=request.user.username
        print(username,"username")
        asset = Upload.objects.get(pk=asset_id)
        comment = Comment(upload=asset, text=comment_text,created_user=username)
        comment.save()
        
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Invalid request method'})  



@login_required(login_url = 'accounts:login')
def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            requested_by = form.cleaned_data['requested_by']
            caption = form.cleaned_data['caption']
            image = form.cleaned_data['image']
            
            upload_instance = Upload(requested_by=requested_by, caption=caption, image=image)
            upload_instance.save()
            messages.success(request,'Uploaded Successfully')
            return redirect('/blog/')
        
        else:
            # If the form is not valid, return errors to the client
            errors = form.errors
            return JsonResponse({'success': False, 'errors': errors}, status=400)  # Sending JSON response with errors
    else:
        errors = form.errors

    Asset_Dateils_All = Upload.objects.all().order_by('-created_at') 
    return redirect('blog',{'requested_by':requested_by,'caption':caption,'image':image ,'Asset_Dateils_All':Asset_Dateils_All})

from django.shortcuts import render, get_object_or_404
from .models import Upload, Comment

def view_comments(request, post_id):
    post = get_object_or_404(Upload, pk=post_id)
    comments = Comment.objects.filter(upload=post)
    return render(request, 'shop/shop/viewcomments.html', {'post': post, 'comments': comments})


def shop(request, category_slug=None):
    categories = None
    products = None
    

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        products_count = products.count()
        
    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        products_count = products.count()
        
    
    for product in products:
        reviews = ReviewRating.objects.order_by('-updated_at').filter(product_id=product.id, status=True)

    context = {
        'category_slug': category_slug,
        'products' : paged_products,
        'products_count': products_count,
        
    }
    return render(request, 'shop/shop/shop.html', context)


def product_details(request, category_slug, product_details_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_details_slug)
        
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        return e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    reviews = ReviewRating.objects.order_by('-updated_at').filter(product_id=single_product.id, status=True)
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct':orderproduct,
        'reviews': reviews,
        'product_gallery':product_gallery,
    }
    return render(request, 'shop/shop/product_details.html', context)


def search(request):
    products_count = 0
    products = None
    paged_products = None
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword :
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
            
            products_count = products.count()
            
    
    context = {
        'products': products,
        'products_count': products_count,
    }
    return render(request, 'shop/shop/search.html', context)



def review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you, your review updated!')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you, your review Posted!')
                return redirect(url)
