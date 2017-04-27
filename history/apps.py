from django.conf import settings
from django.apps import AppConfig, apps
from django.db.models.signals import post_save, post_init, post_delete


class HistoryConfig(AppConfig):
    name = 'history'

    def ready(self):
        from .signals import (model_updated, trackedmodel_post_init,
                              trackedmodel_post_delete)
        for hist_models in settings.HISTORY_MODELS:
            app_label, model_name = hist_models.split('.')
            model = apps.get_model(app_label, model_name)
            post_init.connect(trackedmodel_post_init, sender=model)
            post_save.connect(
                model_updated, sender=model,
                dispatch_uid='%s.%s.history.signals.model_updated' %
                (app_label.lower(), model_name.lower()))
            post_delete.connect(
                trackedmodel_post_delete, sender=model,
                dispatch_uid='%s.%s.history.signals.trackedmodel_post_delete' %
                (app_label.lower(), model_name.lower()))
