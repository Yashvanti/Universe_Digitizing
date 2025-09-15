from django.shortcuts import get_object_or_404, render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from .forms import EmbroideryForm, QuoteForm
#from django.conf import stripe
from django.http import JsonResponse
from .forms import CustomerUserForm, CustomerForm




def contact_us_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        subject = f"Feedback from {first_name} {last_name} ({phone})"
        full_message = f"Message:\n{message}\n\nFrom: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}"

        try:
            send_mail(subject, full_message, email, [settings.EMAIL_RECEIVING_USER])
            return redirect('contactussuccess')  # ✅ make sure this path exists in urls.py
        except Exception as e:
            return HttpResponse(f"❌ Failed to send email: {e}")

    return render(request, 'embroidery/contactus.html')


def contact_us_success_view(request):
    return render(request, 'embroidery/contactussuccess.html')

def home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'embroidery/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})
      


#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')





from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomerUserForm, CustomerForm

# ✅ Function to check if user is a customer
def is_customer(user):
    return user.groups.filter(name="CUSTOMER").exists()

def customer_signup_view(request):
    if request.method == "POST":
        userForm = CustomerUserForm(request.POST)
        customerForm = CustomerForm(request.POST)

        if userForm.is_valid() and customerForm.is_valid():
            # ✅ Save user and hash password
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data["password"])  
            user.save()

            # ✅ Save customer linked to the user
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()

            # ✅ Add user to CUSTOMER group
            customer_group, _ = Group.objects.get_or_create(name="CUSTOMER")
            customer_group.user_set.add(user)

            messages.success(request, "Account created successfully! Please log in.")
            return redirect(reverse("customerlogin"))

        else:
            messages.error(request, "Signup failed. Please correct the errors below.")
            print(userForm.errors)  # ✅ Debugging errors
            print(customerForm.errors)  # ✅ Debugging errors

    else:
        userForm = CustomerUserForm()
        customerForm = CustomerForm()

    return render(request, "embroidery/customersignup.html", {"userForm": userForm, "customerForm": customerForm})

# ✅ After login, check if the user is a customer or admin
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect("customer-home")
    else:
        return redirect("admin-dashboard")
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    customercount = models.Customer.objects.count()
    productcount = models.Product.objects.count()
    quotecount = models.Quote.objects.count()

    recent_quotes = models.Quote.objects.all().order_by('-submission_date')[:5]

    context = {
        'customercount': customercount,
        'productcount': productcount,
        'quotecount': quotecount,
        'recent_quotes': recent_quotes,
    }
    return render(request, 'embroidery/admin_dashboard.html', context)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'embroidery/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'embroidery/admin_update_customer.html',context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'embroidery/admin_products.html',{'products':products})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm = forms.ProductForm()
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request, 'embroidery/admin_add_products.html', {'productForm': productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'embroidery/admin_update_product.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'embroidery/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'embroidery/update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'embroidery/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    products=models.Product.objects.all().filter(name__icontains=query)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'embroidery/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})
    return render(request,'embroidery/index.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})


# any one can add product to cart, no need of signin
def add_to_cart_view(request,pk):
    products=models.Product.objects.all()

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=1

    response = render(request, 'embroidery/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')

    return response



# for checkout of cart
def cart_view(request):
    #for cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # fetching product details from db whose id is present in cookie
    products=None
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)

            #for total price shown in cart
            for p in products:
                total=total+p.price
    return render(request,'embroidery/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})


def remove_from_cart_view(request,pk):
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # removing product id from cookie
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart=product_ids.split('|')
        product_id_in_cart=list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products=models.Product.objects.all().filter(id__in = product_id_in_cart)
        #for total price shown in cart after removing product
        for p in products:
            total=total+p.price

        #  for update coookie value after removing product id in cart
        value=""
        for i in range(len(product_id_in_cart)):
            if i==0:
                value=value+product_id_in_cart[0]
            else:
                value=value+"|"+product_id_in_cart[i]
        response = render(request, 'embroidery/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
        if value=="":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids',value)
        return response


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'embroidery/feedback_sent.html')
    return render(request, 'embroidery/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    return render(request,'embroidery/customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart})



# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # this is for checking whether product is present in cart or not
    # if there is no product in cart we will not show address form
    product_in_cart=False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart=True
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile=addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            total=0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_in_cart=product_ids.split('|')
                    products=models.Product.objects.all().filter(id__in = product_id_in_cart)
                    for p in products:
                        total=total+p.price

            response = render(request, 'embroidery/payment.html',{'total':total})
            response.set_cookie('email',email)
            response.set_cookie('mobile',mobile)
            response.set_cookie('address',address)
            return response
    return render(request,'embroidery/customer_address.html',{'addressForm':addressForm,'product_in_cart':product_in_cart,'product_count_in_cart':product_count_in_cart})







@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request,'embroidery/my_order.html',{'data':zip(ordered_products,orders)})
 



# @login_required(login_url='customerlogin')
# @user_passes_test(is_customer)
# def my_order_view2(request):

#     products=models.Product.objects.all()
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0
#     return render(request,'embroidery/my_order.html',{'products':products,'product_count_in_cart':product_count_in_cart})    



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,orderID,productID):
    order=models.Orders.objects.get(id=orderID)
    product=models.Product.objects.get(id=productID)
    mydict={
        'orderDate':order.order_date,
        'customerName':request.user,
        'customerEmail':order.email,
        'customerMobile':order.mobile,
        'shipmentAddress':order.address,
        'orderStatus':order.status,

        'productName':product.name,
        'productImage':product.product_image,
        'productPrice':product.price,
        'productDescription':product.description,


    }
    return render_to_pdf('embroidery/download_invoice.html',mydict)






@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'embroidery/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'embroidery/edit_profile.html',context=mydict)



#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'embroidery/aboutus.html')



def add_to_cart_view(request, pk):
    product = models.Product.objects.get(id=pk)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_ids = product_ids + "|" + str(pk)
        else:
            product_ids = str(pk)
    else:
        product_ids = str(pk)
    response = render(request, 'embroidery/index.html')
    response.set_cookie('product_ids', product_ids)
    return response






def vectorart_view(request):
    return render(request,'embroidery/vectorart.html')



def faq_view(request):
    return render(request,'embroidery/faq.html')


def pricing_view(request):
    return render(request,'embroidery/pricing.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Quote
from django.core.files.storage import FileSystemStorage


def add_quote_view(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)  # Use Django Form for validation
        if form.is_valid():
            form.save()
            messages.success(request, "Your quote request has been submitted successfully!")
            return redirect("customer-home")
        else:
            print(form.errors)  # Debugging: Print form errors

    else:
        form = QuoteForm()
    
    return render(request, 'embroidery/add_quote.html', {'form': form})



def quote_added(request):
    return render(request, 'embroidery/quote_added.html', {})

# views.py

from django.shortcuts import render
from .models import Quote

def admin_view_quotes(request):
    quotes = Quote.objects.all()  # Retrieve all quotes from the database
    return render(request, 'embroidery/admin_view_quotes.html', {'quotes': quotes})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Quote
from .forms import QuoteForm

def update_quote(request, id):
    quote = get_object_or_404(Quote, id=id)

    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)

        if form.is_valid():
            form.save()
            messages.success(request, "Quote updated successfully!")
            return redirect('quote_list')
        else:
            print("Form errors:", form.errors)  # Debugging

    else:
        form = QuoteForm(instance=quote)

    return render(request, 'embroidery/update_quote.html', {'form': form, 'quote': quote})


def delete_quote(request, id):
    quote = get_object_or_404(Quote, id=id)
    quote.delete()
    return redirect('quote_list')

def quote_list(request):
    quotes = Quote.objects.all()
    return render(request, 'embroidery/admin_view_quotes.html', {'quotes': quotes})

from django.shortcuts import render

def index_view(request):
    return render(request, 'embroidery/index.html')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import EmbroideryDetails
from django.utils import timezone

@login_required(login_url='customerlogin')  # ✅ Ensures only logged-in users can access
def embdigitizing_view(request):
    if request.method == 'POST':
        form = EmbroideryForm(request.POST, request.FILES)
        if form.is_valid():
            embroidery_detail = form.save(commit=False)
            embroidery_detail.email = request.user.email  # ✅ Safe now
            embroidery_detail.submission_date = timezone.now()
            embroidery_detail.save()
            messages.success(request, 'Information added successfully!')
            return redirect("customer-home")
    else:
        form = EmbroideryForm()
    return render(request, 'embroidery/embroiderydigitizing.html', {'form': form})

@login_required(login_url='adminlogin')
def admin_view_embroidery_orders(request):
    orders = EmbroideryDetails.objects.all()  
    return render(request, 'embroidery/admin_view_embroidery_orders.html', {'orders': orders})


@login_required(login_url='adminlogin')
def admin_delete_embroidery_order(request, order_id):
    order = get_object_or_404(EmbroideryDetails, id=order_id)
    order.delete()
    messages.success(request, 'Embroidery order deleted successfully.')
    return redirect('admin_view_embroidery_orders')



from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
import razorpay
from .models import CheatSheet  # Ensure your model is correctly imported

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

@login_required(login_url='customerlogin')
def payment_view(request, order_id):
    order = get_object_or_404(CheatSheet, id=order_id)

    # If already paid, redirect to download page
    if order.is_paid:
        return redirect('download_file', order_id=order.id)

    # Convert amount to paise (100 INR = 10000 paise)
    amount = int(order.price * 100) if order.price else 10000  # Default ₹100

    try:
        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1",  # Auto-capture payment
            "notes": {
                "order_id": str(order.id),
                "user_id": str(request.user.id)
            }
        })

        # Save Razorpay order ID to your model
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        context = {
            'amount': amount,
            'api_key': settings.RAZORPAY_API_KEY,
            'order_id': razorpay_order['id'],
            'user': request.user,
            'order': order,
        }
        return render(request, 'payment.html', context)

    except Exception as e:
        return HttpResponse(f"Error creating payment order: {str(e)}", status=500)

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
                return HttpResponse("Missing payment details", status=400)

            # Verify Razorpay signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            client.utility.verify_payment_signature(params_dict)

            # Mark order as paid
            order = get_object_or_404(CheatSheet, razorpay_order_id=razorpay_order_id)
            order.is_paid = True
            order.razorpay_payment_id = razorpay_payment_id
            order.save()

            return redirect('payment_success', order_id=order.id)

        except razorpay.errors.SignatureVerificationError:
            return HttpResponse("Payment signature verification failed", status=400)
        except Exception as e:
            return HttpResponse(f"Payment processing error: {str(e)}", status=400)

    return HttpResponse("Invalid request method", status=405)

@login_required(login_url='customerlogin')
def payment_success_view(request, order_id):
    order = get_object_or_404(CheatSheet, id=order_id)
    return render(request, 'payment_success.html', {'order': order})


from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import CheatSheet, Quote, EmbroideryDetails
from .forms import CheatSheetForm
from django.contrib.auth.decorators import login_required


from django.http import FileResponse, HttpResponse

@login_required(login_url='customerlogin')
def preview_file_view(request, order_id):
    file = get_object_or_404(EmbroideryDetails, id=order_id)

    if not file.file_upload.name.endswith('.pdf'):
        return HttpResponse("❌ Only PDF preview is allowed before payment.")

    return FileResponse(file.file_upload.open('rb'), content_type='application/pdf')

from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings  # <-- ADD THIS

from .forms import CheatSheetForm
from .models import CheatSheet

@login_required(login_url='adminlogin')
def upload_cheatsheet(request):
    if request.method == "POST":
        form = CheatSheetForm(request.POST, request.FILES)
        if form.is_valid():
            cheatsheet = form.save(commit=False)
            entered_email = form.cleaned_data['email']

            # Lookup user by email
            try:
                user = User.objects.get(email=entered_email)
            except User.DoesNotExist:
                messages.error(request, f"No user found with email: {entered_email}")
                return redirect('upload-cheatsheet')

            cheatsheet.uploaded_for = user
            cheatsheet.uploaded_at = timezone.now()
            cheatsheet.save()

            # Send notification email
            send_mail(
                subject="A New File Has Been Uploaded for You",
                message=(
                    f"Hi {user.first_name},\n\n"
                    f"A new cheatsheet titled '{cheatsheet.title}' has been uploaded. "
                    "Please log in to complete payment and download.\n\n"
                    "Regards,\nUniverse Digitizing Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, f"\u2705 Cheatsheet '{cheatsheet.title}' uploaded and email sent to {user.email}")
            return redirect('upload-cheatsheet')
    else:
        form = CheatSheetForm()

    return render(request, 'embroidery/cheatsheet_upload.html', {'form': form})


from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import CheatSheet
import mimetypes

@login_required(login_url='customerlogin')
def preview_file_view(request, order_id):
    file = get_object_or_404(CheatSheet, id=order_id)
    file_path = file.file.path
    file_name = file.file.name.lower()

    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        return HttpResponse("❌ Preview not available for this file type.")

    content_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(file.file.open('rb'), content_type=content_type)


from django.http import FileResponse, HttpResponse
import os

@login_required(login_url='customerlogin')
def download_file_view(request, order_id):
    embroidery = get_object_or_404(models.EmbroideryDetails, id=order_id)

    if not embroidery.is_paid:
        # ❌ Not paid → redirect to payment page
        return redirect('create_order')  # No need for order_id if not used in that view

    allowed_formats = ['.emb', '.dst', '.pes', '.melco']
    file_ext = os.path.splitext(embroidery.file_upload.name)[1].lower()

    if file_ext not in allowed_formats:
        return HttpResponse("❌ Only EMB, DST, PES, MELCO formats are allowed for download.")

    return FileResponse(embroidery.file_upload.open('rb'), as_attachment=True)

# ✅ Updated views.py (Stripe Payment Based on Stitch Count + Turnaround)

from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from .models import EmbroideryDetails, Payment
import razorpay
import json
from django.conf import settings
from .models import File


# Use your environment variables in production
from django.conf import settings
import razorpay

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET)
)

def home(request):
    return render(request, 'home.html')

def payment_page(request, order_id):
    embroidery = get_object_or_404(EmbroideryDetails, id=order_id)
    return render(request, 'embroidery/payment.html', {
        'embroidery': embroidery,
        'razorpay_key': settings.RAZORPAY_API_KEY  # 🔥 Pass Key ID for frontend
    })

# views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from .models import EmbroideryDetails
import razorpay
from django.conf import settings

# Initialize Razorpay client once globally
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

# views.py

@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            file_id = request.POST.get("file_id")

            if not file_id:
                return JsonResponse({"error": "File ID is required"}, status=400)

            from .models import CheatSheet  # ✅ Import CheatSheet model if not already
            file = get_object_or_404(CheatSheet, id=file_id)

            amount = int(file.price * 100)  # Price from cheatsheet model

            order = razorpay_client.order.create({
                'amount': amount,
                'currency': 'INR',
                'payment_capture': 1
            })

            return JsonResponse(order)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return HttpResponseBadRequest("Only POST method allowed")

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import CheatSheet, Payment
import razorpay
from django.conf import settings

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

from django.contrib.auth.models import User

def verify_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }

            razorpay_client.utility.verify_payment_signature(params_dict)

            file_id = data.get('file_id')
            if not file_id:
                return JsonResponse({'error': 'File ID missing'}, status=400)

            file = CheatSheet.objects.get(id=file_id)

            # 🔥 get the user linked with the cheatsheet file
            user = file.uploaded_for

            # mark the file as paid
            file.is_paid = True
            file.save()

            # save the payment
            Payment.objects.create(
                user=user,  # ✅ Correct user now
                amount=int(file.price * 100)
            )

            return JsonResponse({'status': 'Payment Verified and Saved', 'file_id': file.id})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'Payment Verification Failed'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



def payment_dashboard(request):
    payments = Payment.objects.all().order_by('-id')
    return render(request, 'dashboard.html', {'payments': payments})


@login_required(login_url='customerlogin')
def preview_file_view(request, order_id):
    file = get_object_or_404(models.CheatSheet, id=order_id)
    file_path = file.file.path
    file_name = file.file.name.lower()

    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        return HttpResponse("❌ Preview not available for this file type.")

    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(file.file.open('rb'), content_type=content_type)

@login_required(login_url='customerlogin')
def download_file_view(request, order_id):
    file = get_object_or_404(models.CheatSheet, id=order_id)
    if not file.is_paid:
        return redirect('payment_page', order_id=order_id)
    return FileResponse(file.file.open('rb'), as_attachment=True)



# ✅ User View: List Their Assigned Cheatsheets
def user_cheatsheet_list(request):
    files = CheatSheet.objects.filter(uploaded_for=request.user)
    return render(request, "embroidery/cheatsheet_list.html", {
        "files": files,
        "razorpay_key": settings.RAZORPAY_API_KEY  # ✅ Pass Razorpay Key
    })


# ✅ Admin View: Delete Cheatsheet
def delete_cheatsheet(request, cheatsheet_id):
    cheatsheet = get_object_or_404(CheatSheet, id=cheatsheet_id)

    if request.user.is_staff:  # ✅ Only admin can delete
        cheatsheet.delete()
        messages.success(request, "Cheatsheet deleted successfully!")
    else:
        messages.error(request, "You are not allowed to delete this file.")

    return redirect("embroidery/cheatsheet_list")

from django.http import JsonResponse
from fuzzywuzzy import process

def chatbot_response(request):
    if request.method == "GET":
        user_message = request.GET.get('message', '').strip().lower()
        response = "I'm sorry, I don't understand. Can you rephrase?"

        # Dictionary of chatbot responses
        responses = {
            "hello": "Hello! How can I assist you today?",
            "hi": "Hi there! Need help with embroidery digitizing?",
            "hey": "Hey! How can I help you?",
            "bye": "Goodbye! Have a great day!",
            "thank you": "You're welcome! Let me know if you need more help.",
            "how are you": "I'm just a chatbot, but I'm here to help you!",
            
            # Order Related Queries
            "order": "To place an order, go to 'Get a Quote' and upload your design.",
            "track order": "Login to your account and go to 'My Orders' to track your order status.",
            
            # Pricing & Payment
            "pricing": "Pricing depends on design complexity and stitch count. Upload your design to get a quote.",
            "cost": "Simple designs start from $5, moderate ones from $10, and complex ones from $20+. Stitch count affects the price.",
            "payment": "We accept PayPal, Stripe, and credit/debit cards.",
            "secure payment": "Yes, we use secure gateways like Stripe.",
            
            # Embroidery Services
            "embroidery digitizing": "Embroidery digitizing is converting artwork into a machine-readable embroidery file.",
            "file formats": "We support DST, PES, EXP, JEF, VP3, and more.",
            "turnaround time": "Standard turnaround is 24 hours, but express service is available.",
            "sample before payment": "Yes, we can provide a small preview before full digitization.",
            
            # File Download
            "download file": "After making payment, go to 'My Orders' and click 'Download'.",
            "can't download": "You need to complete payment before downloading. Go to 'Payments' to check.",
            
            # Customer Support
            "contact support": "You can contact us via email at rutujachikane0@gmail.com or through our live chat.",
            "refund policy": "Refunds are available for quality issues. Contact support for assistance.",
            "bulk discount": "Yes! Contact us for special pricing on bulk orders.",
            
            # Miscellaneous
            "loyalty program": "Yes! Earn points with every order and redeem discounts.",
            "resell designs": "Yes, but copyright rules must be respected.",
            "company location": "We are an online embroidery digitizing service available worldwide.",
        }

        # Use fuzzy matching to find the best response
        best_match, score = process.extractOne(user_message, responses.keys())

        # If similarity score is above 60%, return the matched response
        if score > 60:
            response = responses[best_match]

        return JsonResponse({"response": response})

    return JsonResponse({"response": "Invalid request"})


from django.shortcuts import render
from .models import Product  # ✅ Use Product instead of Portfolio

def portfolio_page(request):
    portfolio_items = Product.objects.all().order_by('-id')  # latest products first
    return render(request, "embroidery/portfolio.html", {"portfolio_items": portfolio_items})

def portfolio_view(request):
    return render(request,'embroidery/portfolio.html')

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout_view(request):
    logout(request)
    return redirect('index')  # Or any other page like 'index' or 'home'
