from rest_framework.response import Response
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework.views import APIView
from .serializers import ProductSerializer, OpinionSerializer, AddScoreSerializer, AddProductSerializerList, RemoveProductSerializer, \
    TrackListSerializer, TrackRetrieveSerializer
from .models import Product, Opinion, Score, Cart, CartItem
from accounts.permissions import IsActive
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

@extend_schema(
    tags=["product"],
    description="This endpoint returns a list of products. You can filter the products by name, brand, and type with query param.",
    parameters=[
        OpenApiParameter(
            name='name',
            description='Filter products by name',
            required=False,
        ),
        OpenApiParameter(
            name='brand',
            description='Filter products by brand',
            required=False,
        ),
        OpenApiParameter(
            name='type',
            description='Filter products by type',
            required=False,
        ),
    ],
    responses={200: ProductSerializer(many=True)}
)
class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    authentication_classes = ()
    def get_queryset(self):
        queryset = Product.objects.all()
        name = self.request.query_params.get('name', None)
        brand = self.request.query_params.get('brand', None)
        type = self.request.query_params.get('type', None)
        if name:
            queryset = queryset.filter(name=name)
        if brand:
            queryset = queryset.filter(brand=brand)
        if type:
            queryset = queryset.filter(type=type)
        return queryset

@extend_schema(
    tags=["product"],
    description="This endpoint returns the details of the product.",
    responses={200: ProductSerializer}
)    
class ProductRetrieve(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    authentication_classes = ()
    
@extend_schema(
    tags=["opinion"],
    description="This endpoint allows you to add an opinion to the product.",
    request=OpinionSerializer,
    responses={
        201: OpenApiResponse(),
        401: OpenApiResponse(),
        404: OpenApiResponse()
    }
)
class OpinionCreateView(CreateAPIView):
    permission_classes = [IsActive, IsAuthenticated]
    queryset = Opinion.objects.all()
    serializer_class = OpinionSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        opinion = Opinion.objects.create(product=product, user=user, comment=serializer.validated_data['comment'])
        opinion.save()
    
    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        return Response(status=res.status_code)
        
@extend_schema(
    tags=["opinion"],
    description="This endpoint returns a list of opinions for the product.",
    responses={
        200: OpenApiResponse(response=OpinionSerializer(many=True)),
        401: OpenApiResponse(),
        404: OpenApiResponse()
    }
)   
class OpinionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OpinionSerializer
    
    def get_queryset(self):
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        queryset = Opinion.objects.filter(product=product, is_accepted='1')
        return queryset

@extend_schema(
    tags=["score"],
    description="This endpoint allows you to add a score to the product.",
    request=AddScoreSerializer,
    responses={
        201: OpenApiResponse(),
        400: OpenApiResponse(),
        401: OpenApiResponse(),
        404: OpenApiResponse()
    }
)
class AddScoreView(CreateAPIView):
    permission_classes = [IsActive, IsAuthenticated]
    serializer_class = AddScoreSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                product= get_object_or_404(Product,id=self.kwargs['product_id'])
                score = Score.objects.create(user=request.user, product=product, score=serializer.validated_data['score'])
                score.save()
                total_score = (product.score_avg * product.score_num) + serializer.validated_data['score']
                product.score_num += 1
                product.score_avg = total_score / product.score_num
                product.save()
        except IntegrityError:
            return Response({'message':'You have been scored for this product!'},status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message":"Your score has been successfully added!"}, status=status.HTTP_201_CREATED)

@extend_schema(
    tags=["cart"],
    description="This endpoint allows you to add products to the cart.",
    request=AddProductSerializerList,
    responses={
        201: OpenApiResponse(),
        400: OpenApiResponse(),
        401: OpenApiResponse(),
        404: OpenApiResponse()
    }
)   
class AddProductView(CreateAPIView):
    permission_classes = [IsActive, IsAuthenticated]
    serializer_class = AddProductSerializerList
    
    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user,is_purchased=False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():    
            for item in serializer.validated_data['products']:
                product = get_object_or_404(Product,id=item['product_id'])
                cartitem,created = CartItem.objects.get_or_create(cart=cart, product=product)
                if created:
                    cartitem.number = item['number']
                    cartitem.save()
                else:
                    cartitem.number += item['number']
                    cartitem.save()
        return Response({"message": "Products added to cart successfully!"}, status=status.HTTP_201_CREATED)

@extend_schema(
    tags=["cart"],
    description="This endpoint allows you to remove products from the cart. It has body!",
    request=RemoveProductSerializer,
    responses={
        200: OpenApiResponse(),
        400: OpenApiResponse(),
        401: OpenApiResponse(),
        404: OpenApiResponse()
    },
)   
class RemoveProductView(DestroyAPIView):
    permission_classes = [IsActive, IsAuthenticated]
    serializer_class = RemoveProductSerializer
    
    def destroy(self, request, *args, **kwargs):
        cart,created = Cart.objects.get_or_create(user=request.user,is_purchased=False)
        if created:
            return Response({'message': "Your basket is empty!"},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        all = serializer.validated_data.get('all', None)
        products = serializer.validated_data.get('product_ids', None)
        if all is not None:
            with transaction.atomic():
                cart.delete()
                cart = Cart.objects.create(user=request.user)
            return Response({"message":"All of the products have been removed!"}, status=status.HTTP_200_OK)
        else:
            deleted = 0
            with transaction.atomic():   
                for product in products:
                    try:
                        cartitem = CartItem.objects.get(cart=cart,product=product)
                        cartitem.delete()
                        cart.save()
                        deleted += 1
                    except CartItem.DoesNotExist:
                        pass
            return Response({'message':f'{deleted} item(s) have been deleted!'})        

@extend_schema(
    tags=["cart"],
    description="This endpoint allows you to shop.",
    responses={
        200: OpenApiResponse(),
        400: OpenApiResponse(),
        401: OpenApiResponse()
    }
)  
class ShoppingView(RetrieveAPIView):
    permission_classes = [IsActive, IsAuthenticated]
        
    def retrieve(self, request, *args, **kwargs):
        cart,created = Cart.objects.get_or_create(user=request.user,is_purchased=False)
        if created:
            return Response({'message':'The basket is empty!'}, status=status.HTTP_400_BAD_REQUEST)
        cartitems = cart.cartitem_set.all()
        if not cartitems.exists():
            return Response({'message':'The basket is empty!'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            cart.is_purchased = True
            cart.purchased_date = timezone.now()
            cart.save()
            cart = Cart.objects.create(user=request.user)
        return Response({'message':'The purchase was successful!'}, status=status.HTTP_200_OK)

@extend_schema(
    tags=["cart"],
    description="This endpoint returns a list purchased carts.",
    responses={
        200: OpenApiResponse(response=TrackListSerializer(many=True)),
        401: OpenApiResponse()
    }
)            
class TrackListView(ListAPIView):
    permission_classes = [IsActive, IsAuthenticated]
    serializer_class = TrackListSerializer
    
    def get_queryset(self):
        query_set = Cart.objects.filter(user=self.request.user, is_purchased=True)    
        return query_set

@extend_schema(
    tags=["cart"],
    description="This endpoint allows you to track the cart.",
    responses={
        200: OpenApiResponse(TrackRetrieveSerializer),
        401: OpenApiResponse(),
        404: OpenApiResponse()
    }
)   
class TrackRetrieveView(RetrieveAPIView):
    permission_classes = [IsActive, IsAuthenticated]
    queryset = Cart.objects.filter(is_purchased=True)
    serializer_class = TrackRetrieveSerializer
    lookup_field = 'track_id'

    def retrieve(self, request, *args, **kwargs):
        cart = self.get_object() 
        if cart.user != request.user:
            return Response({'message':'It is not your cart!'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
        
        
        
    
        