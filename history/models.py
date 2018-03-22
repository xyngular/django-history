import logging
from enum import Enum

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.apps import apps
from django.conf import settings
from kombu import Connection, Exchange

logger = logging.getLogger(__name__)


class ModelHistory(models.Model):
    class ChangeType(Enum):
        create = 'create'
        update = 'update'
        delete = 'delete'

    id = models.BigAutoField(primary_key=True)

    CHANGE_TYPE_CHOICES = ((t.value, t.name.title()) for t in ChangeType)

    # Consider indexing these two together?
    app_label = models.CharField(max_length=255, db_index=True)
    model_name = models.CharField(max_length=100, db_index=True)

    detail = JSONField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        index_together = [
            ("app_label", "model_name"),
        ]

    def get_change_type(self):
        return self.ChangeType(self.detail['change_type'])

    def get_model_class(self):
        return apps.get_model(self.app_label, self.model_name)

    def get_object_pk(self):
        return self.detail.get('pk')

    def get_object(self):
        """Get the object for the update record by pk"""
        model = self.get_model_class()
        model_pk = self.get_object_pk()

        if not model_pk:
            logger.warning('ModelHistory record detail missing PK for ID %s' %
                           self.id)
            return None

        try:
            obj = model.objects.get(pk=self.detail['pk'])
            return obj
        except model.DoesNotExist:
            message = ("%s.%s with PK=%s does not exist in database.  It may "
                       "have been deleted (check for 'deleted' history "
                       "record)" % (self.app_label, self.model_name.title(),
                                    model_pk))
            logger.info(message)
            return None

    @property
    def app_model_name(self):
        return '%s.%s' % (self.app_label.lower(), self.model_name.title())

    @property
    def config(self):
        if not hasattr(settings, 'HISTORY') or not settings.HISTORY.get('MODELS'):
            return {}

        return settings.HISTORY['MODELS'].get(self.app_model_name) or {}

    @property
    def should_publish_to_queue(self):
        if self.config.get('publish_to_queue'):
            return self.config.get('publish_to_queue')
        else:
            return False

    @property
    def message_body(self):
        """Format the detail and model attributed for the message body"""
        body = {
            'service_change_id': self.pk,
            'service_name': settings.HISTORY['SERVICE_NAME'],
            'module': self.app_label.lower(),
            'object': self.model_name.lower(),
            'detail': self.detail,
        }
        return body

    def publish_to_queue(self):
        if not self.should_publish_to_queue:
            return None

        broker_url = settings.HISTORY['BROKER_URL']

        exchange_name = self.config.get('exchange_name')
        if not exchange_name:
            exchange_name = '%s.change' % self.app_model_name.lower()

        exchange = Exchange(exchange_name, 'fanout', durable=True)
        with Connection(broker_url) as conn:
            producer = conn.Producer(exchange=exchange, serializer='json')
            producer.publish(self.message_body, retry=True)
