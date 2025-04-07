from flask import Blueprint, jsonify, request
from .models import Country
from .database import db
from sqlalchemy import asc, desc

routes = Blueprint("routes", __name__)

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
        "area": float(country.area) if country.area else 0.0,
        "map_url": country.map_url,
        "population": float(country.population) if country.population else 0.0,
        "flag_url": country.flag_url
    }

@routes.route("/country", methods=["GET"])
def get_countries():
    try:
        # Define valid sorting parameters
        sort_mappings = {
            'a_to_z': Country.name.asc(),
            'z_to_a': Country.name.desc(),
            'population_high_to_low': Country.population.desc(),
            'population_low_to_high': Country.population.asc(),
            'area_high_to_low': Country.area.desc(),
            'area_low_to_high': Country.area.asc()
        }

        # Get query parameters
        sort_by = request.args.get('sort_by', 'a_to_z')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        name = request.args.get('name', '').strip()
        region = request.args.get('region', '').strip()
        subregion = request.args.get('subregion', '').strip()

        # Validate inputs
        page = max(page, 1)
        limit = max(min(limit, 100), 1)
        
        # Validate sort parameter
        if sort_by not in sort_mappings:
            return jsonify({
                "message": "Invalid sort parameter",
                "valid_sorts": list(sort_mappings.keys())
            }), 400

        # Base query
        query = Country.query

        # Apply filters
        if name:
            query = query.filter(Country.name.ilike(f'%{name}%'))
        if region:
            query = query.filter(Country.region.ilike(f'%{region}%'))
        if subregion:
            query = query.filter(Country.subregion.ilike(f'%{subregion}%'))

        # Apply sorting
        query = query.order_by(sort_mappings[sort_by])

        # Pagination
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        # Prepare response
        country_list = [country_to_dict(c) for c in pagination.items]

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

@routes.route("/country/<int:country_id>", methods=["GET"])
def get_country(country_id):
    try:
        country = Country.query.get(country_id)
        
        if not country:
            return jsonify({
                "message": "Country not found",
                "data": {}
            }), 404
            
        return jsonify({
            "message": "Country detail",
            "data": {
                "country": country_to_dict(country)
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error fetching country",
            "data": {}
        }), 500

@routes.route("/country/<int:country_id>/neighbour", methods=["GET"])
def get_country_neighbours(country_id):
    try:
        country = Country.query.get(country_id)
        if not country:
            return jsonify({
                "message": "Country not found",
                "data": {}
            }), 404

        neighbours = country.neighboring_countries
        neighbour_list = [country_to_dict(n) for n in neighbours]

        return jsonify({
            "message": "Country neighbours",
            "data": {
                "countries": neighbour_list
            }
        })

    except Exception as e:
        return jsonify({
            "message": "Error retrieving neighbours",
            "data": {},
            "error": str(e)
        }), 500

@routes.route("/country", methods=["POST"])
def create_country():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["name", "cca3", "currency_code", "currency", "capital", "region"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "required_fields": required_fields
                }), 400

        # Validate numeric fields
        numeric_fields = {
            "area": data.get("area", 0),
            "population": data.get("population", 0)
        }
        for field, value in numeric_fields.items():
            if not isinstance(value, (int, float)):
                return jsonify({
                    "error": f"{field} must be a number",
                    "received_type": type(value).__name__
                }), 400

        # Create country
        new_country = Country(
            name=data["name"],
            cca3=data["cca3"],
            currency_code=data["currency_code"],
            currency=data["currency"],
            capital=data["capital"],
            region=data["region"],
            subregion=data.get("subregion", ""),
            area=data.get("area", 0),
            map_url=data.get("map_url", ""),
            population=data.get("population", 0),
            flag_url=data.get("flag_url", "")
        )

        db.session.add(new_country)
        db.session.commit()

        return jsonify({
            "message": "Country created successfully",
            "data": country_to_dict(new_country)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": str(e),
            "message": "Error creating country"
        }), 500