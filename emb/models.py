from django.db import models
from django.contrib.auth.models import User


from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)  # Increased max_length for address
    mobile = models.CharField(max_length=20, null=False)

    @property
    def username(self):
        return self.user.username  # Accessing username from User model

    @property
    def email(self):
        return self.user.email  # Accessing email from User model

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    product_image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    product=models.ForeignKey('Product',on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name


class CheatSheet(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="cheatsheets/")
    stitch_count = models.IntegerField(default=0)
    turnaround = models.CharField(max_length=100)
    uploaded_for = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)

    is_paid = models.BooleanField(default=False)  # ✅ Required for payment tracking

    def __str__(self):
        return f"{self.title} (For {self.uploaded_for.username})"



    
# models.py
from django.utils.timezone import now  # Import `now`
from django.db import models

class Quote(models.Model):
    full_name = models.CharField(max_length=255)
    design_name = models.CharField(max_length=255)
    size = models.CharField(
        max_length=50,
        choices=[
            ('capfront', 'Cap Front'),
            ('leftchest', 'Left Chest'),
            ('jacketback', 'Jacket Back'),
            ('other', 'Other')
        ]
    )
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    additional_info = models.TextField(null=True, blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.full_name} - {self.design_name}"

    
class EmbroideryDetails(models.Model):
    complexity = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    file_format = models.CharField(max_length=100)
    turnaround = models.CharField(max_length=100)
    additional_info = models.CharField(max_length=255, db_column='additional_info')
    file_upload = models.FileField(upload_to='files/')
    submission_date = models.DateField(auto_now_add=True)
    email = models.EmailField(null=True, blank=True)  # ✅ Email stored from logged-in user

    
   
class File(models.Model):
    title = models.CharField(max_length=255)
    file_upload = models.FileField(upload_to='uploads/')
    is_completed = models.BooleanField(default=False)  # To track if the file is ready

    def __str__(self):
        return self.title


class EmbFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='emb_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} by {self.user.username}"


class ChatHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user_message} → Bot: {self.bot_response}"
 
 


class Portfolio(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="portfolio_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
