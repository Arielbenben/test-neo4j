from flask import Blueprint, request, jsonify
from app.db.repository.device_repository import count_connected_devices, find_devices_with_strong_signal, \
    find_devices_connected_in_bluetooth_and_how_long_the_path
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


@phone_blueprint.route('/count_connected_devices', methods=['GET'])
def count_devices_route():
    json = request.json
    if not json:
        return jsonify({"Error": "Expected to get json"}), 400

    count = count_connected_devices(json)
    return jsonify({"connected_devices_count": count}), 200


@phone_blueprint.route('/find_strong_signal_devices', methods=['GET'])
def find_strong_signal_devices():
    devices = find_devices_with_strong_signal()
    if devices:
        return jsonify({"devices": devices})
    else:
        return jsonify({"message": "No devices found with signal strength stronger than -60"}), 404


@phone_blueprint.route('/find_bluetooth_devices', methods=['GET'])
def find_bluetooth_devices():
    devices = find_devices_connected_in_bluetooth_and_how_long_the_path()
    if devices:
        return jsonify(devices), 200
    else:
        return jsonify({"message": "No Bluetooth-connected devices found."}), 404
