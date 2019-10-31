"""webapp URL Configuration

The `urlpatterns` list routes URLs to views
"""
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^contact-us/$', views.contact, name='contact'),
    ]
