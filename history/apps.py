import logging

from django.conf import settings
from django.apps import AppConfig, apps
from django.db.models.signals import post_save, post_init, post_delete

logger = logging.getLogger(__name__)


class HistoryConfig(AppConfig):
    name = 'history'

    def _setup_model_signals(self, hist_model, model_config=None):
        from .signals import (model_updated, trackedmodel_post_init,
                              trackedmodel_post_delete)

        app_label, model_name = hist_model.split('.')
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

        if model_config.get('publish_to_queue') is True:
            # add signal to history table publish to queue
            pass

    def ready(self):
        from .signals import model_history_pub_queue_post_save

        # support old config where it was just tuples.  Now we use a dict with
        # optional settings per model
        if hasattr(settings, 'HISTORY_MODELS'):
            for hist_model in settings.HISTORY_MODELS:
                self._setup_model_signals(hist_model=hist_model)
            return None

        if not hasattr(settings, 'HISTORY'):
            logger.warning('django_history is not configured.  '
                           'Please add HISTORY config to settings.py')
            return None

        # New config style
        hist_settings = settings.HISTORY

        for hist_model, model_config in hist_settings['MODELS'].items():
            self._setup_model_signals(hist_model=hist_model,
                                      model_config=model_config or {})

        # add publish to message queue signal if broker url is set
        if settings.HISTORY.get('BROKER_URL'):
            ModelHistory = apps.get_model('history', 'ModelHistory')
            post_save.connect(
                model_history_pub_queue_post_save, sender=ModelHistory,
                dispatch_uid='history.signals.model_history_pub_queue_post_save')   # noqa
