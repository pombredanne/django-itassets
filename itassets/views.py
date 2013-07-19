""" Standalone webinterface for Openstack Swift. """
# -*- coding: utf-8 -*-
#pylint:disable=E1101

from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from itassets.models import Hardware, ExportToken


def export_hardware_json(request, token, group):
    try:
        token = ExportToken.objects.get(token=token)
    except ObjectDoesNotExist:
        return None
    hardware = Hardware.objects.filter(hardware_group=group)
    response = HttpResponse(content_type="application/json")
    serializers.serialize("json", hardware, stream=response)
    return response
