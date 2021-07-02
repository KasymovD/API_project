from django.contrib.auth import get_user_model
from django.db.models import Avg, Q
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view, action
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, SimpleRateThrottle
from rest_framework.views import APIView

from .filters import ProductFilter
from .models import Product, Review, WishList, Favorite, Cart
from .permissions import IsAuthorOrAdminPermission, DenyAll
from .serializers import ProductListSerializer, ProductDetailsSerializer, ReviewSerializer, \
    SerializerFavorite, CartListSerializer

User = get_user_model()

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthenticated()]
    queryset = Product.objects.all()
    serializer_class = ProductDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend,  OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ['title', 'price']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        elif self.action in ['create_review', 'like', 'cart', 'favorite']:
            return [IsAuthenticated()]
        return []

# api/v1/products/id/create_view
    @action(detail=True, methods=['POST'])
    def create_review(self, request, pk):
        data = request.data.copy()
        data['product'] = pk
        serializer = ReviewSerializer(data=data,
                                      context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

# /api/v1/products/id/like
    @action(detail=True, methods=['POST'])
    def like(self, request, pk):
        product = self.get_object()
        user = request.user
        like_obj, created = WishList.objects.get_or_create(product=product,
                                                           user=user)
        if like_obj.is_liked:
            like_obj.is_liked = False
            like_obj.save()
            return Response('disliked')
        else:
            like_obj.is_liked = True
            like_obj.save()
            return Response('liked')

    # /api/v1/favorite/
    @action(detail=True, methods=['POST'])
    def favorite(self, request, pk):
        product = self.get_object()
        user = request.user
        favorit, created = Favorite.objects.get_or_create(product=product,
                                                           user=user)
        if favorit.favorite:
            favorit.favorite = False
            favorit.delete()
            return Response('Удаленно из избранного')
        else:
            favorit.favorite = True
            favorit.save()
            return Response('Добавленно в избранное')

# api/v1/products/search
    @action(detail=False, methods=["GET"])
    def search(self, request, pk=None):
        q = request.query_params.get("q")
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(description__icontains=q))
        serializer = ProductDetailsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def cart(self, request, pk):
        product = self.get_object()
        user = request.user
        carte, created = Cart.objects.get_or_create(product=product,
                                                          user=user)
        if carte.add:
            carte.add = False
            carte.delete()
            return Response('Убранно из корзину ')
        else:
            carte.add = True
            carte.save()
            return Response('Добавленно в корзину')

class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthorOrAdminPermission()]


# Security by ddos attack

class UserRateThrottles(SimpleRateThrottle):
    scope = 'user'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

class ExampleView(APIView):
    throttle_classes = [UserRateThrottle]

    def get(self, request, format=None):
        content = {
            'status': 'request was permitted'
        }
        return Response(content)


class Favorites(ListAPIView):
    queryset = Favorite.objects.all()
    serializer_class = SerializerFavorite
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_context(self):
        return {'request': self.request}


class CartProducts(ListAPIView):

    queryset = Cart.objects.all()
    serializer_class = CartListSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_context(self):
        return {'request': self.request}
