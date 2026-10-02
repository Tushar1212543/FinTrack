from django.urls import path
from .views import *

urlpatterns = [
    path("transactions/",transaction_list, name="transaction-list"),
    path("transactions-page/", transaction_page, name="transaction-page"),
    path("transactions/create/", transaction_create, name="transaction-create"),
    path("transactions/<int:transaction_id>/", transaction_detail, name="transaction-detail"),
    path("transactions/<int:transaction_id>/update/", transaction_update, name="transaction-update"),
    path("transactions/<int:transaction_id>/delete/", transaction_delete, name="transaction-delete"),
    path("transactions/summary/", transaction_summary, name="transaction-summary"),
    path("transactions/category-summary/", category_summary, name="category-summary"),
    path("transactions/monthly-summary/", monthly_summary, name="monthly-summary"),
    path("investments/", investment_list, name="investment-list"),
    path("investments/create/", investment_create, name="investment-create"),
    path("investments/summary/", investment_summary, name="investment-summary"),
    path("investments/<int:investment_id>/", investment_detail, name="investment-detail"),
    path("investments/<int:investment_id>/update/", investment_update, name="investment-update"),
    path("investments/<int:investment_id>/delete/", investment_delete, name="investment-delete"),
    path("transactions/create-page/", transaction_create_page, name="transaction-create-page"),
    path("transactions/<int:transaction_id>/delete-page/", transaction_delete_page, name="transaction-delete-page"),
    path("transactions/<int:transaction_id>/edit-page/", transaction_edit_page, name="transaction-edit-page"),
    path("investments-page/", investment_page, name="investment-page"),
    path("investments/create-page/", investment_create_page, name="investment-create-page"),
    path("investments/<int:investment_id>/delete-page/", investment_delete_page, name="investment-delete-page"),
    path("investments/<int:investment_id>/edit-page/", investment_edit_page, name="investment-edit-page"),
    path("categories/create-page/", category_create_page, name="category-create-page"),
]