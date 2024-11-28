from flask import Blueprint, request, jsonify
from app.service.device_service import get_data_from_api


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