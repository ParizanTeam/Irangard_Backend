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
from datetime import datetime


class TourViewSet(ModelViewSet):
	queryset = Tour.objects.all()
	serializer_class = TourSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

	pagination_class = DefaultPagination
	permission_classes = [IsOwnerOrReadOnly]

	def create(self, request, *args, **kwargs):
		data = request.data.copy()
		data['owner'] = request.user

		serializer = self.get_serializer(data=data)
		serializer.is_valid(raise_exception=True)
		tour = serializer.save()

		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def update(self, request, *args, **kwargs):

		tour = self.get_object()
		serializer = self.get_serializer(tour, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	# @action(detail=True, methods=['POST'], permission_classes=[IsOwnerOrReadOnly])
	# def add_discount_code(self, request, pk, *args, **kwargs):
	#     data = request.data
	#     tour = self.get_object()

	#     discount_code = DiscountCode.objects.create(
	#         off_percentage=data['off_percentage'], expire_date=data['expire_date'], code=data['code'], tour=tour)
		
	#     discount_code.save()
	#     serializer = DiscountCodeSerializer(discount_code)
		
		
	#     return Response(serializer.data, status=status.HTTP_201_CREATED)
	
	# @action(detail=True, methods=['POST'], permission_classes=[IsOwnerOrReadOnly])
	# def remove_discount_code(self, request, pk, *args, **kwargs):
	#     data = request.data
	#     tour = self.get_object()

	#     discount_code = DiscountCode.objects.create(
	#         off_percentage=data['off_percentage'], expire_date=data['expire_date'], code=data['code'], tour=tour)
		
	#     discount_code.save()
	#     serializer = DiscountCodeSerializer(discount_code)
		
		
	#     return Response(serializer.data, status=status.HTTP_201_CREATED)


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
		tour.owner.deposit(cost)
		Transaction.objects.create(tour=tour, sender=user, cost=cost, date=datetime.now())
		tour.update_revenue(cost)
		tour.bookers.add(user)
		tour.update_remaining()

		return Response({'booked': True}, status=status.HTTP_200_OK)


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
		tour.owner.withraw(amount)
		tour.withraw(amount)
		return Response({'amount': amount}, status=status.HTTP_200_OK)
