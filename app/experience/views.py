from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Location, Experience
from experience import serializers


class BaseExperienceAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                                mixins.CreateModelMixin):
    """Base Viewset for user owned recipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    def perform_create(self, serializer):
        """Create an new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseExperienceAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class LocationViewSet(BaseExperienceAttrViewSet):
    """Manage Locations in the database"""
    queryset = Location.objects.all()
    serializer_class = serializers.LocationSerializer

class ExperienceViewSet(viewsets.ModelViewSet):
    """Manage Experiences in the database"""
    serializer_class = serializers.ExperienceSerializer
    queryset = Experience.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
