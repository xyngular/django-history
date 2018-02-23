from rest_framework import serializers
from drf_queryfields import QueryFieldsMixin
from . import models
from rest_framework.reverse import reverse


class ModelHistorySerializer(QueryFieldsMixin, serializers.ModelSerializer):
    include_arg_name = 'field__in'
    exclude_arg_name = 'field!__in'

    resource_url = serializers.SerializerMethodField()
    endpoint_url = serializers.SerializerMethodField()

    class Meta:
        model = models.ModelHistory
        fields = (
            'id', 'app_label', 'model_name', 'detail', 'timestamp', 'resource_url', 'endpoint_url'
        )

    model_to_detail_can_generate = {}
    model_to_endpoint_cache = {}

    def get_resource_url(self, obj):
        model_name = obj.model_name
        can_generate = self.model_to_detail_can_generate.get(model_name)
        generated_url = ""

        if can_generate is True or can_generate is None:
            endpoint_url = self.get_endpoint_url(obj)
            generated_url = f'{endpoint_url}/{obj.detail["pk"]}'

        if can_generate is True:
            return generated_url

        url = reverse(
            f'v1:{obj.model_name}-detail',
            [obj.detail["pk"], ],
            request=self.context['request']
        )

        if can_generate is False:
            return url

        # can_generate is None, check to see if we can generate.
        self.model_to_detail_can_generate[model_name] = True if generated_url == url else False
        return url

    def get_endpoint_url(self, obj):
        model_name = obj.model_name
        key = model_name
        url = self.model_to_endpoint_cache.get(key)
        if url is not None:
            return url

        url = reverse(f'v1:{obj.model_name}-list', request=self.context['request'])
        self.model_to_endpoint_cache[key] = url
        return url
