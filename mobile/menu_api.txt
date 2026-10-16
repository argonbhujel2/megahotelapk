"""Public menu endpoints."""
from flask import Blueprint, request, jsonify
from app.models.menu import Category, FoodItem

bp = Blueprint("menu", __name__)


@bp.route("/categories", methods=["GET"])
def list_categories():
    lang = request.args.get("lang", "en")
    cats = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return jsonify({"success": True, "categories": [c.to_dict(lang) for c in cats]})


@bp.route("/foods", methods=["GET"])
def list_foods():
    lang = request.args.get("lang", "en")
    category_id = request.args.get("category_id")
    q = request.args.get("q", "").strip()
    vegetarian = request.args.get("vegetarian")
    available_only = request.args.get("available") == "1"

    query = FoodItem.query.filter_by(is_published=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if q:
        query = query.filter(
            (FoodItem.name_en.ilike(f"%{q}%")) | (FoodItem.name_ne.ilike(f"%{q}%"))
        )
    if vegetarian == "1":
        query = query.filter_by(is_vegetarian=True)
    elif vegetarian == "0":
        query = query.filter_by(is_vegetarian=False)

    foods = query.order_by(FoodItem.sort_order).limit(100).all()
    result = []
    for f in foods:
        d = f.to_dict(lang)
        if available_only and not d["available"]:
            continue
        result.append(d)
    return jsonify({"success": True, "foods": result})


@bp.route("/foods/<food_id>", methods=["GET"])
def food_detail(food_id):
    lang = request.args.get("lang", "en")
    food = FoodItem.query.get(food_id)
    if not food or not food.is_published:
        return jsonify({"success": False, "error": "not_found"}), 404
    return jsonify({"success": True, "food": food.to_dict(lang, include_options=True)})
