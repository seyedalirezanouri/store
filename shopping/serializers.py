from rest_framework.serializers import Serializer, ModelSerializer, ChoiceField, IntegerField, ValidationError, CharField, ListField, DateTimeField
from .models import Product, Opinion, Cart, CartItem

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('name','brand', 'type', 'price', 'in_stock', 'score_avg', 'score_num')

class OpinionSerializer(ModelSerializer):
    class Meta:
        model = Opinion
        fields = ('comment', 'user', 'product', 'mentioned_at')
        read_only_fields = ('user', 'product')

class AddScoreSerializer(Serializer):
    SCORE_CHOICES = (
        (5,"perfect"),
        (4,"great"),
        (3,"good"),
        (2,"not good"),
        (1,"bad")
    )
    score = ChoiceField(choices = SCORE_CHOICES)
    
class AddProductSerializer(Serializer):
    product_id = IntegerField()
    number = IntegerField()
    
    def validate(self, data):
        if data['number'] < 1:
            raise ValidationError("Number should be more than zero!!")
        return data

class AddProductSerializerList(Serializer):
    products = ListField(child= AddProductSerializer(), required=True, min_length=1, max_length=100)
            
class RemoveProductSerializer(Serializer):
    all = CharField(required=False)
    product_ids = ListField(child=IntegerField(), required=False)
    
    def validate(self, data):
        all = data.get('all', None)
        products = data.get('product_ids', None)
        if all is None and products is None:
            raise ValidationError('At least one product should be chosen!')
        if all is not None and all != 'all':
            raise ValidationError()
        return data

class TrackListSerializer(ModelSerializer):
    username = CharField(source="user.username", read_only=True)
    class Meta:
        model = Cart
        fields = ('track_id','username', 'purchased_date', 'total_price')

class CartItemSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('product', 'number', 'total_price')    
        
class TrackRetrieveSerializer(ModelSerializer):
    items = CartItemSerializer(source='cartitem_set',many=True, read_only=True)
    username = CharField(source="user.username", read_only=True)
    class Meta:
        model = Cart
        fields = ('track_id','username', 'purchased_date', 'total_price','items')

        
            
    