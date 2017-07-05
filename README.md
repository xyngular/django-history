# Model History Tracking

 For every model for which you want to track data changes,
 add to settings

```python
HISTORY = {
    'MODELS': {
        'app_namer.Model': {
            'publish_to_queue': True,
            # 'exchange_name': 'app_name.model.change'  # optional
        },
        'app_name.Model': None,
    },
    'BROKER_URL': os.getenv('HISTORY_BROKER_URL', DEFAULT_BROKER_URL),
    'SERVICE_NAME': 'memberapi',
}

```

Models listed will have their changed saved to a model history table.  If
BROKER_URL is set, all changes for models with `publish_to_queue=True` will be
sent to a kombu exchange (i.e. RabbitMQ) so other services can listen to events.
In that case, `SERVICE_NAME` should also be set.