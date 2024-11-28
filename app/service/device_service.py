from app.db.repository.device_repository import insert_two_devices_to_db, add_interaction_relation, \
    get_device_by_id_and_time_relation, get_device_with_relation_to_device, get_recent_interaction_of_device
from app.utils.repository_utils import add_device_to_model, add_interaction_to_model


def get_data_from_api(json):
    first_device = json['devices'][0]
    second_device = json['devices'][1]
    interaction = json['interaction']
    if not check_devices_validation(first_device, second_device, interaction):
        return
    models = add_data_to_models(first_device, second_device, interaction)
    result = insert_data_to_db(models)
    return 'data inserted successfully' if result else 'data did not insert successfully'


def add_data_to_models(first_device, second_device, interaction):
    first_device = add_device_to_model(first_device)
    second_device = add_device_to_model(second_device)
    interaction = add_interaction_to_model(interaction)
    return {'first_device': first_device, 'second_device': second_device, 'interaction': interaction}


def insert_data_to_db(models: dict):
    devices_inserted = insert_two_devices_to_db(models['first_device'], models['second_device'])
    interaction_result = add_interaction_relation(models['interaction'])
    return True if devices_inserted and interaction_result else False


def check_devices_validation(first_device, second_device, interaction):
    if check_if_device_call_himself(first_device, second_device):
        return False
    if check_if_already_exist_interaction_in_the_same_time(first_device, interaction):
        return False
    if check_if_already_exist_interaction_in_the_same_time(second_device, interaction):
        return False
    return True


def check_if_device_call_himself(first_device, second_device):
    return first_device['name'] == second_device['name']


def check_if_already_exist_interaction_in_the_same_time(device: dict, interaction: dict):
    result = get_device_by_id_and_time_relation(device, interaction)
    return True if result else False


def check_if_there_is_direct_connection(json):
    first_device = json['first_device']
    second_device = json['second_device']
    first_to_second = get_device_with_relation_to_device(first_device, second_device)
    second_to_first = get_device_with_relation_to_device(second_device, first_device)
    return True if first_to_second or second_to_first else False


def get_most_recent_interaction(json):
    device = json['device']
    result = get_recent_interaction_of_device(device)
    return result