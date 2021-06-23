from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Location, Experience
from experience import serializers
from rest_framework.decorators import action
from rest_framework.response import Response



class BaseExperienceAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                                mixins.CreateModelMixin):
    """Base Viewset for user owned experience attributes"""
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
        """Retrieve the experiences for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.ExperienceDetailSerializer
        elif self.action == 'upload_image':
            return serializers.ExperienceImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new experience"""
        serializer.save(user=self.request.user)
    
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to an experience"""
        experience = self.get_object()
        serializer = self.get_serializer(
            experience,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
