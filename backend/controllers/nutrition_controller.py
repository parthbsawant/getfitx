from flask import request, jsonify

from services.nutrition_service import search_food


def search_foods():

    try:

        query = request.args.get("q")

        if not query:

            return jsonify({
                "success": False,
                "message": "Search query required"
            }), 400

        results = search_food(query)

        return jsonify({
            "success": True,
            "results": results
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500