from rest_framework import serializers
from core.models import Tag, Location, Experience

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

class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for experience objects"""
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )


    class Meta:
        model = Experience
        fields = ['id', 'title', 'time_minutes', 'price', 'website', 'location', 'tags']
        read_only_field = ['id']