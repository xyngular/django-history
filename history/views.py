from rest_framework import viewsets
import rest_framework_filters as filters
from . import models
from . import serializers


class ModelHistoryFilter(filters.FilterSet):
    class Meta:
        model = models.ModelHistory
        fields = {
            'id': ['exact', 'in'],
            'app_label': ['exact'],
            'model_name': ['exact'],
            'detail': [],
            'timestamp': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


class ModelHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    filter_class = ModelHistoryFilter
    queryset = models.ModelHistory.objects.all()
    serializer_class = serializers.ModelHistorySerializer
    required_scopes = []