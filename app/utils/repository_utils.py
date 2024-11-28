from typing import Dict
import toolz as t
from app.db.model.device import Device
from app.db.model.interaction import Interaction
from app.db.model.location import Location


def add_device_to_dict_without(device_details: Device):
    return {'brand': device_details.brand, 'model': device_details.model, 'name': device_details.name,
            'device_id': device_details.id ,'os': device_details.os, **device_details.location}


def add_interaction_to_dict(interaction: Interaction):
    return {'from_device': interaction.method, 'to_device': interaction.bluetooth_version,
            'method': interaction.method, 'duration_seconds': interaction.duration_seconds,
            'distance_meters': interaction.distance_meters, 'bluetooth_version': interaction.bluetooth_version,
            'signal_strength_dbm': interaction.signal_strength_dbm, 'timestamp': interaction.timestamp}


def add_device_to_model(device: dict):
    location = Location(**device['location'])
    return Device(id=device['id'], name=device['name'], brand=device['brand'], model=device['model'],
                  os=device['os'], location=location)


def add_interaction_to_model(interaction: dict):
    return Interaction(**interaction)


def check_if_devices_valid(first_device, second_device):
    return first_device['name'] == second_device['name']