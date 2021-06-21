from django.urls import path, include
from rest_framework.routers import DefaultRouter
from experience import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)

app_name = 'experience'

urlpatterns = [
    path('', include(router.urls)),
]
