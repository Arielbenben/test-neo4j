from flask import Blueprint, request, jsonify
from app.service.device_service import get_data_from_api, check_if_there_is_direct_connection, \
   get_most_recent_interaction


phone_blueprint = Blueprint('phone', __name__)


@phone_blueprint.route("/phone_tracker", methods=['POST'])
def get_interaction():
   try:
      json = request.json
      if not json:
         return jsonify({'Error': 'Expected to get json'}), 500
      print(json)
      result = get_data_from_api(json)
      return jsonify({'message': result}), 200
   except Exception as e:
      return jsonify({'Error': str(e)}), 500


@phone_blueprint.route("/direct_connection", methods=['GET'])
def determine_if_direct_connection_between_two_devices_route():
   try:
      json = request.json
      if not json:
         return jsonify({'Error': 'Expected to get json'}), 500
      result = check_if_there_is_direct_connection(json)
      return jsonify({'message': result}), 200
   except Exception as e:
      return jsonify({'Error': str(e)}), 500


@phone_blueprint.route("/most_recent_interaction", methods=['GET'])
def get_most_recent_interaction_route():
   try:
      json = request.json
      if not json:
         return jsonify({'Error': 'Expected to get json'}), 500
      result = get_most_recent_interaction(json)
      if result:
         return jsonify(result), 200
      return jsonify({'message': 'There is not interaction to this device'}), 200
   except Exception as e:
      return jsonify({'Error': str(e)}), 500