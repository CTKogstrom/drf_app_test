from rest_framework import serializers
from core.models import Tag, Location

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)

class LocationSerializer(serializers.ModelSerializer):
    """Serializer for location objects"""

    class Meta:
        model= Location
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']
    