from rest_framework import serializers
from .models import equipmentdata

class equipmentdataserializer(serializers.ModelSerializer):
    class Meta:
        model = equipmentdata
        fields = '__all__'