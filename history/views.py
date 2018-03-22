from rest_framework import viewsets
import rest_framework_filters as filters
from rest_framework_filters.backends import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from . import models
from . import serializers


class ModelHistoryFilter(filters.FilterSet):
    class Meta:
        model = models.ModelHistory
        fields = {
            'id': ['exact', 'in', 'lt', 'lte', 'gt', 'gte'],
            'app_label': ['exact'],
            'model_name': ['exact'],
            'detail': [],
            'timestamp': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


class ModelHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    filter_class = ModelHistoryFilter
    queryset = models.ModelHistory.objects.all()
    serializer_class = serializers.ModelHistorySerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    ordering = ('id', 'timestamp')

    # You'll want to set this to a 'histories-*service*' scope.
    required_scopes = []
