from app.db.model.device import Device
from app.db.model.interaction import Interaction
from app.db.model.node import Node
from app.db.model.relation import Relation
from app.db.neo4j_database import driver
from app.db.repository.generic_repository import insert_by_node_label, attach_relation
from app.utils.repository_utils import add_device_to_dict_without, add_interaction_to_dict_without_id, \
    add_interaction_to_dict
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


def insert_two_devices_db(device1: Device, device2: Device):
    with driver.session() as session:
        query = """
        CREATE (d1:Device {device1_props})
        RETURN d1
        CREATE (d2:Device {device2_props})
        RETURN d2
        """

        device1_props = add_device_to_dict_without(device1)
        device1_props['location'] = f"{device1.location.latitude},{device1.location.longitude}"

        device2_props = add_device_to_dict_without(device2)
        device2_props['location'] = f"{device2.location.latitude},{device2.location.longitude}"

        params = {
            'device1_props': device1_props,
            'device2_props': device2_props
        }

        result = session.run(query, **params)
        return [dict(record['d']) for record in result]


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
        MATCH (d1:Device {id: $device1_id}), (d2:Device {id: $device2_id})
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
        return {
            'device1': dict(result['d1']),
            'device2': dict(result['d2']),
            'relation': dict(result['rel'])
        } if result else None


def update_interaction_relation(device1: Device, device2: Device, updated_props: dict):
    with driver.session() as session:
        query = """
        MATCH (d1:Device {id: $device1_id})-[rel:INTERACTION]->(d2:Device {id: $device2_id})
        SET rel += $updated_props
        RETURN d1, d2, rel
        """
        params = {
            'device1_id': device1.id,
            'device2_id': device2.id,
            'updated_props': updated_props
        }

        result = session.run(query, params).single()
        return {
            'device1': dict(result['d1']),
            'device2': dict(result['d2']),
            'relation': dict(result['rel'])
        } if result else None





