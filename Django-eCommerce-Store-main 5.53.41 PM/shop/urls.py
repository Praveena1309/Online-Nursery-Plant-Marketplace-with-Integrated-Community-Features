from django.urls import path
from django.utils.regex_helper import normalize
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('about/', views.about, name='about'),
    path('upload_view/', views.upload_view, name='upload_view'),
    path('shop/<slug:category_slug>/', views.shop, name='categries'),
    path('shop/<slug:category_slug>/<slug:product_details_slug>/', views.product_details, name='product_details'),
    path('search/', views.search, name='search'),
    path('review/<int:product_id>/', views.review, name='review'),
     path('like-asset/', views.like_asset, name='like_asset'),
     path('comment-asset/', views.comment_asset, name='comment_asset'),
    path('view-comments/<int:post_id>/', views.view_comments, name='view_comments'),
     
]
