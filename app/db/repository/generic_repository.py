from typing import Dict
from returns.maybe import Maybe
from app.db.model.node import Node
from app.db.model.relation import Relation
from app.utils.repository_utils import update_values_to_string, properties_to_string
from app.db.neo4j_database import driver
import toolz as t
import uuid



def get_all_by_node_label(node_label: str):
    with driver.session() as session:
        query = f"""
        match (g:{node_label}) 
        return g
        """
        res = session.run(query).data()
        return t.pipe(
            res,
            t.partial(t.pluck, 'g'),
            list
        )


@t.curry
def insert_by_node_label(node_label: Node, properties: Dict[str, str | int]):
    with driver.session() as session:
        query = f"""
        CREATE (g:{node_label} {{id: $node_id, {properties_to_string(properties)}}})
        return g
        """
        params = {'node_id': node_label.id, **properties}

        result = session.run(query, params)
        res = result.single()
        return dict(res['g'])


@t.curry
def update_node(node: Node, properties: Dict[str, str | int]):
    with driver.session() as session:
        query = f"""
        match (g:{node.label}{{id: $node_id}})
        set {update_values_to_string("g", properties)}
        return g
        """

        params = {'node_id': node.id, **properties}
        res = session.run(query, params).single()

        return t.pipe(res.get('g'), lambda g: dict(g))


def delete_node(node: Node):
    with driver.session() as session:
        query = f"""
        match (g:{node.label}{{id: $node_id}})
        detach delete g
        """
        params = {'node_id': node.id}
        session.run(query, params)


def attach_relation(first_node: Node, second_node: Node, relation: Relation):
    with driver.session() as session:
        query = f"""
                match (g:{first_node.label} {{id: $f_node_id}}), (ge:{second_node.label} {{id: $s_node_id}})
                merge (g) - [rel:{relation.name}] -> (ge)
                {f" set rel += $properties" if relation.properties else ""}
                return g, ge, rel
                """

        params = {'f_node_id': first_node.id, 's_node_id': second_node.id}

        params_pro = Maybe.from_optional(relation.properties).map(lambda p: { **params, **p }).value_or(params)

        res = session.run(query, params_pro).data()
        return res


def update_relation(first_node: Node, second_node: Node, relation: Relation):
    with driver.session() as session:
        query = f"""
                MATCH (g:{first_node.label} {{id: $f_node_id}})-[rel:{relation.name}]->(ge:{second_node.label} {{id: $s_node_id}})
                {"SET rel += $properties" if relation.properties else ""}
                RETURN g, ge, rel
                """

        params = {'f_node_id': first_node.id, 's_node_id': second_node.id}

        if relation.properties:
            params['properties'] = relation.properties

        res = session.run(query, params).data()
        return res

