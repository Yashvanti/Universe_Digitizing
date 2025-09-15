"""

Developed By : Yashvanti


"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from emb import views
from django.contrib.auth.views import LoginView,LogoutView
from emb.views import chatbot_response  
from emb.views import upload_cheatsheet, user_cheatsheet_list, delete_cheatsheet
from emb.views import contact_us_view, contact_us_success_view
from emb.views import custom_logout_view




urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name=''),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('aboutus', views.aboutus_view),
    path('contactus', views.contact_us_view,name='contactus'),
    path('contactussuccess/', views.contact_us_success_view, name='contactussuccess'),  # ✅ Success page

    path('search', views.search_view,name='search'),
    path('send-feedback', views.send_feedback_view,name='send-feedback'),
    path('view_feedback/', views.view_feedback_view, name='view_feedback'),

    path('adminclick', views.adminclick_view),
    path('adminlogin', LoginView.as_view(template_name='embroidery/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('view-customer', views.view_customer_view,name='view-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),
    path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),

    path('admin-products', views.admin_products_view,name='admin-products'),
    path('admin-add-product', views.admin_add_product_view,name='admin-add-product'),
    path('delete-product/<int:pk>', views.delete_product_view,name='delete-product'),
    path('update-product/<int:pk>', views.update_product_view,name='update-product'),

    path('admin-view-booking', views.admin_view_booking_view,name='admin-view-booking'),
    path('delete-order/<int:pk>', views.delete_order_view,name='delete-order'),
    path('update-order/<int:pk>', views.update_order_view,name='update-order'),


    path('customersignup', views.customer_signup_view, name='customersignup'),
    path('customerlogin', LoginView.as_view(template_name='embroidery/customerlogin.html'),name='customerlogin'),
    path('customer-home/', views.customer_home_view, name='customer-home'),
    path('customer-home/', views.customer_home_view, name='customer_home'),
    path('my-order', views.my_order_view,name='my-order'),
    # path('my-order', views.my_order_view2,name='my-order'),
    path('my-profile', views.my_profile_view,name='my-profile'),
    path('edit-profile', views.edit_profile_view,name='edit-profile'),
    path('download-invoice/<int:orderID>/<int:productID>', views.download_invoice_view,name='download-invoice'),


    path('add-to-cart/<int:pk>', views.add_to_cart_view,name='add-to-cart'),
    path('cart', views.cart_view,name='cart'),
    path('remove-from-cart/<int:pk>', views.remove_from_cart_view,name='remove-from-cart'),
    path('customer-address', views.customer_address_view,name='customer-address'),

    

    path('embdigitizing', views.embdigitizing_view, name='embdigitizing'),

    path('vectorart', views.vectorart_view, name='vectorart'),

    path('portfolio', views.portfolio_page, name='portfolio'),

    path('faq', views.faq_view, name='faq'),

    path('pricing', views.pricing_view, name='pricing'),


    path('quotes/add/', views.add_quote_view, name='add_quote'),
    path('quotes/update/<int:id>/', views.update_quote, name='update_quote'),
    path('quotes/', views.quote_list, name='quote_list'),

    
    path('admin_view_quotes/', views.admin_view_quotes, name='admin_view_quotes'),
    
    path('update-quote/<int:id>/', views.update_quote, name='update-quote'),  

    path('delete-quote/<int:id>/', views.delete_quote, name='delete-quote'),  
    path('quotes/', views.quote_list, name='quote_list'),

    path('index.html', views.index_view, name='index'),
    
    path('register', views.customer_signup_view, name='register'),
    #path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    #path('payment/', views.payment_page, name='payment_page'),  # Payment page    
    
    
    
    path('embroiderydigitizing/', views.embdigitizing_view, name='embroiderydigitizing'),

    # ✅ Admin Upload Cheatsheet Page
    
    path('cheatsheet_upload/', views.upload_cheatsheet, name='upload-cheatsheet'),


    # ✅ User View: List Their Cheatsheets (optional)
    path('cheatsheet_list/', views.user_cheatsheet_list, name='cheatsheet_list'),

    # ✅ Preview File (PDF only before payment)
    path('preview/<int:order_id>/', views.preview_file_view, name='preview_file'),


    # ✅ Redirected Payment Page
# urls.py
    path('create_order/', views.create_order, name='create_order'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    path('dashboard/', views.payment_dashboard, name='payment_dashboard'),
    path('download/<int:order_id>/', views.download_file_view, name='download_file'),
    path('pay/<int:order_id>/', views.payment_page, name='payment_page'),
   
    path('admin_view_embroidery_orders/', views.admin_view_embroidery_orders, name='admin_view_embroidery_orders'),
    path('embroidery-orders/<int:order_id>/delete/', views.admin_delete_embroidery_order, name='admin_delete_embroidery_order'),

    path('chatbot/', views.chatbot_response, name='chatbot_response'),
    
    path('logout/', custom_logout_view, name='logout'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
