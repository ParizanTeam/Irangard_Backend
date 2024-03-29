from datetime import datetime
import uuid
import requests
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import DefaultPagination
from tours.models import *
from .serializers import *
from .permissions import *
from accounts.models import StagedPayments
from accounts.serializers.payment_serializers import VerifiedPaymentSerializer
from django.template.loader import render_to_string
from django.utils import timezone

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.utils.decorators import method_decorator
from Irangard.settings import CACHE_TTL

class TourViewSet(ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    pagination_class = DefaultPagination
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['owner'] = self.request.user.id
        return context


    @method_decorator(cache_page(CACHE_TTL))
    def list(self, request, *args, **kwargs):
      return super().list(self, request, *args, **kwargs)

    # @method_decorator(cache_page(CACHE_TTL))
    # @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        
        tour = None
        tour_id = "Tour" + str(kwargs.get('pk'))

        if(cache.get(tour_id)):
            tour = cache.get(tour_id)
            print('hit the cache')
        else:
            tour = self.get_object()
            cache.set(tour_id,tour)
            print("hit the db")

        serializer = self.get_serializer(tour)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):

        tour = self.get_object()
        serializer = self.get_serializer(tour, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        cache.set("Tour"+str(tour.id),tour)
        print('update the cache')

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, request)
            return Response('tour deleted', status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response(f"{error}", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def apply_discount_code(self, request, *args, **kwargs):
        tour = self.get_object()
        user = request.user
        cost = tour.cost
        if tour.booked(user):
            return Response('Already booked', status=status.HTTP_400_BAD_REQUEST)
        if tour.capacity < 1:
            return Response("there's no reservation available", status=status.HTTP_400_BAD_REQUEST)

        if('discount_code_code' in request.data):
            try:
                discount_code = tour.discount_codes.get(code=request.data['discount_code_code'])
                if(discount_code.expire_date < timezone.now()):
                    return Response('discount code has expired',status=status.HTTP_400_BAD_REQUEST)
                cost = cost - cost * (discount_code.off_percentage/100)
                return Response({"new_cost":cost},status=status.HTTP_200_OK)
            except DiscountCode.DoesNotExist:
                return Response('discount_code does not exist',status=status.HTTP_400_BAD_REQUEST)
        
        return Response("no discount_code is provieded", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def book(self, request, *args, **kwargs):
        tour = self.get_object()
        user = request.user
        cost = tour.cost
        if tour.booked(user):
            return Response('Already booked', status=status.HTTP_400_BAD_REQUEST)
        if tour.capacity < 1:
            return Response("there's no reservation available", status=status.HTTP_400_BAD_REQUEST)

        if('discount_code_code' in request.data):
            try:
                discount_code = tour.discount_codes.get(code=request.data['discount_code_code'])
                if(discount_code.expire_date < timezone.now()):
                    return Response('discount code has expired',status=status.HTTP_400_BAD_REQUEST)
                cost = cost - cost * (discount_code.off_percentage/100)
            except DiscountCode.DoesNotExist:
                return Response('discount_code does not exist',status=status.HTTP_400_BAD_REQUEST)

        order_id = str(uuid.uuid4())
        my_data = {
            "order_id": order_id,
            "amount": cost,
            "name": f"{request.user.username}",
            "mail": f"{request.user.email}",
            "callback": f"https://api.parizaan.ir/tours/{self.kwargs.get('pk')}/verify/"
        }

        my_headers = {"Content-Type": "application/json",
                      'X-API-KEY': 'e309f6e9-7462-46c4-acc7-e6ba2e39252e',
                      'X-SANDBOX': '0'}

        response = requests.post(url="https://api.idpay.ir/v1.1/payment", data=json.dumps(my_data),
                                 headers=my_headers)
        response.raise_for_status()
        print(response.status_code)
        try:
            obj = StagedPayments.objects.get(user=request.user)
            obj.transaction_id = json.loads(response.content)['id']
            obj.order_id = order_id
            obj.save()

        except StagedPayments.DoesNotExist:
            obj = StagedPayments.objects.create(transaction_id=json.loads(response.content)[
                'id'], order_id=order_id, user=request.user)
            obj.save()
        except:
            return Response(f"bad request", status=status.HTTP_400_BAD_REQUEST)

        return Response(json.loads(response.content), status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST', 'GET'], permission_classes=[permissions.AllowAny])
    def verify(self, request, *args, **kwargs):

        try:
            my_data = {
                "order_id": request.data['order_id'],
                "id": request.data['id'],

            }

            my_headers = {"Content-Type": "application/json",
                          'X-API-KEY': 'e309f6e9-7462-46c4-acc7-e6ba2e39252e',
                          'X-SANDBOX': '0'
                          }

            response = requests.post(url="https://api.idpay.ir/v1.1/payment/verify", data=json.dumps(my_data),
                                     headers=my_headers)
            response.raise_for_status()
# print(response.content, ' ', response.status_code)

            if(response.status_code == 200):

                try:
                    staged_payments_user = StagedPayments.objects.get(
                        transaction_id=request.data['id']).user
                    user = User.objects.get(
                        username=staged_payments_user.username)
                    tour = self.get_object()
                    cost = tour.cost
                    tour.owner.deposit(cost)
                    Transaction.objects.create(
                        tour=tour, sender=user, cost=cost, date=datetime.now())
                    tour.update_revenue(cost)
                    tour.bookers.add(user)
                    tour.update_remaining()
                    tour.save()
                    st_payment = StagedPayments.objects.get(user=user)
                    st_payment.delete()
                    verified_payment_serializer = VerifiedPaymentSerializer(
                        data=json.loads(response.content))
                    verified_payment_serializer.is_valid(raise_exception=True)
                    template = render_to_string('success_registration.html',
                                                {
                                                    'username': user.username,
                                                    'code': '123',
                                                    'WEBSITE_URL': 'kooleposhti.tk',
                                                    'tour_title': tour.title,
                                                    'tour_id' : tour.id
                                                })
                    return HttpResponse(template)
# return Response(verified_payment_serializer.data, status=status.HTTP_200_OK)
                except StagedPayments.DoesNotExist:
                    return Response(f"there is no corresponding payment to be verified", status=status.HTTP_400_BAD_REQUEST)
                except Exception as error:
                    print(error)
                    return Response(f"{error}", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(f"transaction is not verified", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except:
            return Response(f"order id is required", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def withraw(self, request, *args, **kwargs):
        tour = self.get_object()
        if request.user != tour.owner.user:
            return Response('you are not the tour owner',
                            status=status.HTTP_403_FORBIDDEN)
        amount = request.data.get('amount', tour.total_revenue)
        if amount > tour.total_revenue or tour.total_revenue == 0:
            return Response('Insufficient funds', status=status.HTTP_400_BAD_REQUEST)
        tour.owner.withdraw(amount)
        tour.withdraw(amount)
        return Response({'amount': amount}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def is_booked(self, request, pk):
        tour = self.get_object()
        user = request.user

        booked = user in tour.bookers.all()

        if(booked):
            return Response('user has booked', status=status.HTTP_200_OK)
        else:
            return Response('user has not booked', status=status.HTTP_400_BAD_REQUEST)
