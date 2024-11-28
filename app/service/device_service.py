from app.db.repository.device_repository import insert_two_devices_db, add_interaction_relation
from app.utils.repository_utils import add_device_to_model, add_interaction_to_model


def get_data_from_api(json):
    first_device = json['devices'][0]
    second_device = json['devices'][1]
    interaction = json['interaction']
    # if devices_validation(first_device, second_device):
    #     return 'The devices are same devices, did not insert to db'

    models = add_data_to_models(first_device, second_device, interaction)
    result = insert_data_to_db(models)
    return 'data inserted successfully' if result else 'data did not insert successfully'


def add_data_to_models(first_device, second_device, interaction):
    first_device = add_device_to_model(first_device)
    second_device = add_device_to_model(second_device)
    interaction = add_interaction_to_model(interaction)
    return {'first_device': first_device, 'second_device': second_device, 'interaction': interaction}


def insert_data_to_db(models: dict):
    devices_inserted = insert_two_devices_db(models['first_device'], models['second_device'])
    interaction_result = add_interaction_relation(models['interaction'])
    return True if devices_inserted and interaction_result else False

