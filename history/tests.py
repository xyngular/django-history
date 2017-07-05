# import pytest
# from django_dynamic_fixture import G

# from member.models import Account
# from history.models import ModelHistory


# @pytest.fixture
# def account():
#     account = G(Account)
#     return account


# @pytest.mark.django_db
# def test_history_get_object(account):
#     history_items = (ModelHistory.objects.filter(app_label='member')
#                      .filter(model_name='account')
#                      .filter(detail__pk=account.pk))
#     assert len(history_items) > 0
#     for history in history_items:
#         assert history.get_object() == account
