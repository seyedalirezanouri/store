from django.db import models
from uuid import uuid4
from django.core.validators import MinValueValidator
from accounts.models import User

class Product(models.Model):
    name = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    in_stock = models.BooleanField(default=True)
    score_avg = models.DecimalField(max_digits=50,default=0.0, decimal_places=2)
    score_num = models.IntegerField(default=0)
    
class Opinion(models.Model):
    ACCEPT_CHOICES = (
        ('1', 'accepted'),
        ('2', 'rejected'),
        ('3', 'not determined')
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()
    mentioned_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.CharField(max_length=1, choices=ACCEPT_CHOICES, default='3')

class Score(models.Model):
    SCORE_CHOICES = (
        (5,"perfect"),
        (4,"great"),
        (3,"good"),
        (2,"not good"),
        (1,"bad")
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.CharField(max_length=1, choices=SCORE_CHOICES)
    class Meta:
        unique_together = ("user", "product") 
    
class Cart(models.Model):
    track_id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_purchased = models.BooleanField(default=False)
    purchased_date = models.DateTimeField(blank=True, null=True)
    total_price = models.IntegerField(default=0)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_purchased'],
                condition=models.Q(is_purchased=False),
                name='unique_unpurchased_cart'
            )
        ]
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    number = models.IntegerField(default=1)
    total_price = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.number
        super().save(*args, **kwargs)

        self.cart.total_price = sum(item.total_price for item in self.cart.cartitem_set.all())
        self.cart.save()
    
    def delete(self, *args, **kwargs):
        cart = self.cart
        cart.total_price -= self.total_price
        cart.save()
        super().delete(*args, **kwargs)