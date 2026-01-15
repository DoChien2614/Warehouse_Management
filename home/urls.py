from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth.views import LoginView,LogoutView
from .views import custom_logout
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.get_home, name='get_home'),
    path('profile/', views.update_profile),
    path('guide/', views.get_guide),
    path('contact/', views.get_contact),
    path('product/', views.get_product),
    path('register/', views.get_register, name='get_register'),
    path('login/', LoginView.as_view(template_name='page1/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    


    path('product/ton-kho/', login_required(views.get_product_tonKho), name='get_product_tonKho'),
    path('product/add/', login_required(views.add_product), name='add_product'),
    path('product/edit/<int:product_id>/', login_required(views.edit_product), name='edit_product'),
    path('product/delete/<int:product_id>/', login_required(views.delete_product), name='delete_product'),
    path('product/detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/phieu-nhap/', login_required(views.import_receipt_list), name='import_receipt_list'),
    path('edit_import/<int:receipt_id>/', views.edit_import_receipt, name='edit_import_receipt'),
    path('delete_import/<int:id>/', views.delete_import_receipt, name='delete_import_receipt'),
    path('product/statistics/', views.statistics_view, name='product_statistics'),



    path('order/',views.get_order, name='order'),
    path('add_order/',views.add_order, name='add_order'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),    
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('view_order/<int:order_id>/', views.view_order, name='view_order'),
    path('search_orders/', views.search_orders, name='search_orders'),
    path('filter-orders/', views.filter_orders, name='filter_orders'),

    

    path('select_store/', views.select_store, name='select_store'),
    path('create_store/', views.create_store, name='create_store'),
    path('store_info/', views.store_info, name='store_info'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('edit_employee_role/<int:user_id>/', views.edit_employee_role, name='edit_employee_role'),
    path('remove_employee/<int:user_id>/', views.remove_employee, name='remove_employee'),
    path('delete_store', views.delete_store, name='delete_store'),
]
