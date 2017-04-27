import datetime
import copy
from decimal import Decimal

from django.db import models

from .models import ModelHistory


def trackedmodel_post_init(sender, instance, **kwargs):
    '''update original data for model after init to enable data tracking'''
    for field in instance._meta.get_fields():
        if isinstance(field, models.Field):
            field_name = field.get_attname()
            setattr(instance, '_original_%s' % field_name,
                    getattr(instance, field_name))


def process_field_value(value):
    '''
    Utility to convert field to string if it is not JSON serializable

    i.e. date and Decimal
    '''
    if isinstance(value, datetime.date):
        str_value = value.isoformat()
    elif isinstance(value, Decimal):
        str_value = str(value)
    else:
        str_value = value

    return str_value


def model_updated(sender, instance, created, **kwargs):
    '''signal callback to log changes when a model is updated'''
    app_label = sender._meta.app_label.lower()
    model_name = sender._meta.object_name.lower()

    change_type = (ModelHistory.ChangeType.create.value if created
                   else ModelHistory.ChangeType.update.value)

    detail = {
        "pk": instance.pk,
        "change_type": change_type,
        "fields": {}
    }

    auto_update_fields = []

    for field in instance._meta.get_fields():
        if isinstance(field, models.Field):
            field_name = field.get_attname()
            orig_field_name = '_original_%s' % field_name

            if getattr(field, 'auto_now', False):
                auto_update_fields.append(field_name)

            orig_value = None if created else getattr(instance,
                                                      orig_field_name)
            new_value = getattr(instance, field_name)

            if created or orig_value != new_value:
                detail['fields'][field_name] = {
                    "original_value": process_field_value(orig_value),
                    "new_value": process_field_value(new_value)
                }

            # update original values for future updates on same instance
            setattr(instance, orig_field_name, new_value)

    # if auto_update_now fields are the only ones updated, then don't
    # write a history records as nothing was updated.
    detail_copy = copy.deepcopy(detail)
    for update_field in auto_update_fields:
        try:
            del detail_copy['fields'][update_field]
        except KeyError:
            continue

    if len(detail_copy['fields'].keys()) > 0:
        ModelHistory.objects.create(app_label=app_label,
                                    model_name=model_name,
                                    detail=detail)


def trackedmodel_post_delete(sender, instance, **kwargs):
    app_label = sender._meta.app_label.lower()
    model_name = sender._meta.object_name.lower()
    change_type = ModelHistory.ChangeType.delete.value

    detail = {
        "pk": instance.pk,
        "change_type": change_type,
        "fields": {}
    }

    for field in instance._meta.get_fields():
        if isinstance(field, models.Field):
            field_name = field.get_attname()
            detail['fields'][field_name] = {
                "original_value":
                    process_field_value(getattr(instance, field_name)),
                "new_value": None
            }

    ModelHistory.objects.create(
        app_label=app_label, model_name=model_name, detail=detail)
