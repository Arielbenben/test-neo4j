from app.db.model.device import Device
from app.db.model.interaction import Interaction
from app.db.model.location import Location


def add_device_to_dict(device_details: Device):
    return {'brand': device_details.brand, 'model': device_details.model, 'name': device_details.name,
            'device_id': device_details.id ,'os': device_details.os, **add_location_to_dict(device_details.location)}


def add_location_to_dict(location: Location):
    return {'latitude': location.latitude, 'longitude': location.longitude, 'altitude_meters': location.altitude_meters,
            'accuracy_meters': location.accuracy_meters}


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


