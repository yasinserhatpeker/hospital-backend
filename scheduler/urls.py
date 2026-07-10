from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (OperationRoomViewSet,SurgeonViewSet,SurgeryViewSet,ScheduleViewSet,AnesthesiaTeamViewSet,ConstraintsViewSet,GenerateScheduleAPIView)


router = DefaultRouter()
router.register(r'rooms',OperationRoomViewSet)
router.register(r'surgeons',SurgeonViewSet)
router.register(r'teams',AnesthesiaTeamViewSet)
router.register(r'surgeries',SurgeryViewSet)
router.register(r'schedules',ScheduleViewSet)
router.register(r'constraints',ConstraintsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-plan/', GenerateScheduleAPIView.as_view(), name='generate-plan')
]

