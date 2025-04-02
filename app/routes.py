from flask import Blueprint, jsonify, request
from .models import Country
from .database import db

routes = Blueprint("routes", __name__)

@routes.route("/country", methods=["GET"])
def get_countries():
    try:
        # Sorting configuration
        sort_mappings = {
            'a_to_z': Country.name.asc(),
            'z_to_a': Country.name.desc(),
            'population_high_to_low': Country.population.desc(),
            'population_low_to_high': Country.population.asc(),
            'area_high_to_low': Country.area.desc(),
            'area_low_to_high': Country.area.asc()
        }

        # Get query parameters with defaults
        sort_by = request.args.get('sort_by', 'a_to_z')
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        # Validate minimum values
        page = max(page, 1)
        limit = max(limit, 1)

        # Get sort order
        sort_order = sort_mappings.get(sort_by, Country.name.asc())

        # Create and paginate query
        query = Country.query.order_by(sort_order)
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        # Build country list
        country_list = [{
            "id": c.id,
            "name": c.name,
            "cca3": c.cca3,
            "currency_code": c.currency_code,
            "currency": c.currency,
            "capital": c.capital,
            "region": c.region,
            "subregion": c.subregion,
            "area": c.area,
            "map_url": c.map_url,
            "population": c.population,
            "flag_url": c.flag_url
        } for c in pagination.items]

        return jsonify({
            "message": "Country list",
            "data": {
                "list": country_list,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
                "page": pagination.page,
                "pages": pagination.pages,
                "per_page": pagination.per_page,
                "total": pagination.total
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error fetching countries",
            "data": {"list": []}
        }), 500


def country_to_dict(country):
    return {
        "id": country.id,
        "name": country.name,
        "cca3": country.cca3,
        "currency_code": country.currency_code,
        "currency": country.currency,
        "capital": country.capital,
        "region": country.region,
        "subregion": country.subregion,
        "area": country.area,
        "map_url": country.map_url,
        "population": country.population,
        "flag_url": country.flag_url,
        "neighbours": [n.id for n in country.neighboring_countries]
    }

@routes.route("/country/<int:country_id>/neighbour", methods=["GET"])
def get_country_neighbours(country_id):
    try:
        # Get the requested country
        country = Country.query.get(country_id)
        
        if not country:
            return jsonify({
                "message": "Country not found",
                "data": {"list": []}
            }), 404

        # Get all neighboring countries
        neighbours = country.neighboring_countries
        
        # Convert neighbours to dictionary format
        neighbour_list = [country_to_dict(n) for n in neighbours]

        return jsonify({
            "message": "Country neighbours",
            "data": {
                "list": neighbour_list
            }
        })

    except Exception as e:
        return jsonify({
            "message": "Error retrieving neighbours",
            "data": {"list": []},
            "error": str(e)
        }), 500
    

    