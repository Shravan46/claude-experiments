import asyncio
import json
from datetime import datetime

from flask import Flask, jsonify, render_template

from dxm_agent import analyze_production_risk

app = Flask(__name__)


def run_analysis():
    """Run the async agent from a synchronous Flask route."""
    return asyncio.run(analyze_production_risk())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze")
def api_analyze():
    try:
        orders = run_analysis()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "orders": orders,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    try:
        orders = run_analysis()
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "orders": orders,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001, debug=False)
