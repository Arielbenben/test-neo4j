from app.db.model.device import Device
from app.db.model.interaction import Interaction
from app.db.neo4j_database import driver
from app.utils.repository_utils import add_device_to_dict,add_interaction_to_dict


def insert_two_devices_to_db(device1: Device, device2: Device):
    try:
        with driver.session() as session:
            query = """
            create (d1:Device $device1_props)
            create (d2:Device $device2_props)
            return d1, d2
            """

            device1_props = add_device_to_dict(device1)
            device2_props = add_device_to_dict(device2)

            params = {
                'device1_props': device1_props,
                'device2_props': device2_props
            }

            result = session.run(query, params).single()

            if result:
                return [dict(result['d1']), dict(result['d2'])]
            return []
    except Exception as e:
        print(f"Error inserting devices: {e}")
        return []


def add_interaction_relation(interaction: Interaction):
    with driver.session() as session:
        query = """
        match (d1:Device {device_id: $device1_id}), (d2:Device {device_id: $device2_id})
        merge (d1) - [rel:INTERACTION] -> (d2)
        set rel += $interaction_props
        return d1, d2, rel
        """

        params = {
            'device1_id': interaction.from_device,
            'device2_id': interaction.to_device,
            'interaction_props': add_interaction_to_dict(interaction)
        }

        result = session.run(query, params).single()

        if result:
            return {
                'device1': dict(result['d1']),
                'device2': dict(result['d2']),
                'relation': dict(result['rel'])
            }
        return None


def get_device_by_id_and_time_relation(device: dict, interaction: dict):
    try:
        with driver.session() as session:
            query = """
            match (d:Device {device_id: $device_id}) - [:INTERACTION {timestamp: $timestamp}] -> (d2:Device)
            return d
            """

            params = {
                'device_id': device['id'],
                'timestamp': interaction['timestamp']
            }

            result = session.run(query, params).single()

            if result:
                return dict(result['d'])
            return None
    except Exception as e:
        print(str(e))


def get_device_with_relation_to_device(first_device, second_device):
    try:
        with driver.session() as session:
            query = """
            match (d1:Device {device_id: $device1_id}) - [:INTERACTION] -> (d2:Device {device_id: $device2_id})
            return d1, d2
            """

            params = {
                'device1_id': first_device['id'],
                'device2_id': second_device['id']
            }

            result = session.run(query, params).single()

            if result:

                device1_data = dict(result['d1'])
                device2_data = dict(result['d2'])

                return {
                    'device1': device1_data,
                    'device2': device2_data
                }
            return None

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def get_recent_interaction_of_device(device: dict):
    try:
        with driver.session() as session:
            query = """
            match (d:Device {device_id: $device_id}) - [rel:INTERACTION] -> (d2:Device)
            return d
            order by rel.timestamp
            desc limit 1
            """
            params = {"device_id": device['id']}
            result = session.run(query, params)

            record = result.single()

            return dict(record["d"]) if record else None
    except Exception as e:
        return str(e)


def count_connected_devices(json):
    try:
        with driver.session() as session:
            query = """
            match (d:Device) - [:INTERACTION] -> (d2:Device{device_id: $device_id})
            return count(d) as connected_devices
            """
            params = {'device_id': json['device_id']}
            result = session.run(query, params).single()

            if result:
                return result["connected_devices"]
            return 0
    except Exception as e:
        return str(e)


def find_devices_with_strong_signal():
    try:
        with driver.session() as session:
            query = """
               match (d1:Device) - [rel:INTERACTION] -> (d2:Device)
               where rel.signal_strength_dbm > -60
               return d1, d2
               """
            result = session.run(query).data()

            if result:
                devices = []
                for record in result:
                    devices.append({
                        "device1": dict(record['d1']),
                        "device2": dict(record['d2'])
                    })
                return devices
            else:
                return None
    except Exception as e:
        return str(e)


def find_devices_connected_in_bluetooth_and_how_long_the_path():
    try:
        with driver.session() as session:
            query = """
                match (start:Device), (end:Device)
                where start <> end
                match path = shortestPath((start) - [:INTERACTION*] -> (end))
                where ALL(r IN relationships(path) where r.method = 'Bluetooth')
                with path, length(path) as pathLength, start, end
                order by pathLength DESC
                limit 1
                return start, end, pathLength
            """
            result = session.run(query).data()

            if result:
                devices = []
                for record in result:
                    devices.append({
                        "device1": dict(record['start']),
                        "device2": dict(record['end']),
                        'path_length': record['pathLength']
                    })
                return devices
            else:
                return None
    except Exception as e:
        return str(e)


