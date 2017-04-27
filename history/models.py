import logging
from enum import Enum

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.apps import apps

logger = logging.getLogger(__name__)


class ModelHistory(models.Model):
    class ChangeType(Enum):
        create = 'create'
        update = 'update'
        delete = 'delete'

    CHANGE_TYPE_CHOICES = ((t.value, t.name.title()) for t in ChangeType)

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
