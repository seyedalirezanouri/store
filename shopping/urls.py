from django.urls import path
from .views import ProductListView, ProductRetrieve, OpinionCreateView, OpinionListView, AddScoreView, AddProductView, RemoveProductView, \
    ShoppingView, TrackListView, TrackRetrieveView

urlpatterns = [
    path("product/list/", ProductListView.as_view(), name="Product List"),
    path("product/get/<int:pk>/", ProductRetrieve.as_view(), name="Product Get"),
    path('opinion/add/<int:product_id>/', OpinionCreateView.as_view(), name="Add Opinion"),
    path('opinion/list/<int:product_id>/', OpinionListView.as_view(), name="Opinion List"),
    path('score/add/<int:product_id>/', AddScoreView.as_view(), name="Add score"),
    path('score/get/<int:pk>/',ProductRetrieve.as_view(), name="Get Product Score"),
    path('cart/add/', AddProductView.as_view(), name='Add Product to Cart'),
    path('cart/remove/', RemoveProductView.as_view(), name='Remove Product from Cart'),
    path('shop/', ShoppingView.as_view(), name='Shop'),
    path('track/list/', TrackListView.as_view(), name='Track List'),
    path('track/get/<str:track_id>/', TrackRetrieveView.as_view(), name="Track Get")
]