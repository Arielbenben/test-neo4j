from app.db.model.device import Device
from app.db.model.interaction import Interaction
from app.db.neo4j_database import driver
from app.utils.repository_utils import add_device_to_dict,add_interaction_to_dict
import toolz as t
from dataclasses import asdict



def get_all_devices():
    with driver.session() as session:
        query = f"""
        match (d:Device) 
        return d
        """
        res = session.run(query).data()
        return t.pipe(
            res,
            t.partial(t.pluck, 'd'),
            list
        )


def insert_two_devices_to_db(device1: Device, device2: Device):
    try:
        with driver.session() as session:
            query = """
            CREATE (d1:Device $device1_props)
            CREATE (d2:Device $device2_props)
            RETURN d1, d2
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


def update_device_in_db(device: Device):
    with driver.session() as session:
        device_props = asdict(device)
        device_id = device_props.pop('id')

        props = ', '.join(f"d.{key} = ${key}" for key in device_props.keys())

        query = f"""
        MATCH (d:Device {{id: $device_id}})
        SET {props}
        RETURN d
        """

        params = {'device_id': device_id, **device_props}

        result = session.run(query, params).single()

        return dict(result['d']) if result else None


def delete_device_from_db(device: Device):
    with driver.session() as session:
        query = """
        MATCH (d:Device {id: $device_id})
        DELETE d
        RETURN COUNT(d) = 0 AS deleted
        """

        params = {'device_id': device.id}
        result = session.run(query, params).single()

        return result['deleted'] if result else False


def add_interaction_relation(interaction: Interaction):
    with driver.session() as session:
        query = """
        MATCH (d1:Device {device_id: $device1_id}), (d2:Device {device_id: $device2_id})
        MERGE (d1)-[rel:INTERACTION]->(d2)
        SET rel += $interaction_props
        RETURN d1, d2, rel
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


def update_interaction_relation(device1: Device, device2: Device, interaction: Interaction):
    with driver.session() as session:
        query = """
        MATCH (d1:Device {id: $device1_id})-[rel:INTERACTION]->(d2:Device {id: $device2_id})
        SET rel += $updated_props
        RETURN d1, d2, rel
        """
        params = {
            'device1_id': device1.id,
            'device2_id': device2.id,
            'updated_props': add_interaction_to_dict(interaction)
        }

        result = session.run(query, params).single()
        return {
            'device1': dict(result['d1']),
            'device2': dict(result['d2']),
            'relation': dict(result['rel'])
        } if result else None


def get_device_by_id_and_time_relation(device: dict, interaction: dict):
    try:
        with driver.session() as session:
            query = """
            MATCH (d:Device {device_id: $device_id})-[:INTERACTION {timestamp: $timestamp}]->(d2:Device)
            RETURN d
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
            MATCH (d1:Device {device_id: $device1_id})-[:INTERACTION]->(d2:Device {device_id: $device2_id})
            RETURN d1, d2
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
            MATCH (d:Device {device_id: $device_id})-[rel:INTERACTION]->(d2:Device)
            RETURN d
            ORDER BY rel.timestamp
            DESC LIMIT 1
            """
            params = {"device_id": device['id']}
            result = session.run(query, params)

            record = result.single()

            return dict(record["d"]) if record else None
    except Exception as e:
        return str(e)
