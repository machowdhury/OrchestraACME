"""Flask routes for Cisco AI Defense integration and MLTK hunt enrichment."""

from __future__ import annotations

from flask import Flask, jsonify, request

from framework.cisco_integration import (
    cisco_scan_telemetry,
    foundation_sec_enrich,
    integration_status,
    run_aibom_scan,
    run_mcp_scan,
)


def register_cisco_routes(app: Flask) -> None:
    @app.route("/api/v1/cisco/status", methods=["GET"])
    def cisco_status():
        return jsonify(integration_status())

    @app.route("/api/v1/cisco/scan/aibom", methods=["POST"])
    def cisco_scan_aibom():
        return jsonify(run_aibom_scan())

    @app.route("/api/v1/cisco/scan/mcp", methods=["POST"])
    def cisco_scan_mcp():
        return jsonify(run_mcp_scan())

    @app.route("/api/v1/cisco/scan/preflight", methods=["POST"])
    def cisco_preflight():
        return jsonify({
            "status": integration_status(),
            "aibom": run_aibom_scan(),
            "mcp": run_mcp_scan(),
            "telemetry": cisco_scan_telemetry(),
        })

    @app.route("/api/v1/hunt/foundation-sec", methods=["POST"])
    def hunt_foundation_sec():
        body = request.get_json(silent=True) or {}
        context = body.get("context") or body.get("hunt_context") or ""
        if not context.strip():
            return jsonify({"error": "context or hunt_context required"}), 400
        return jsonify(foundation_sec_enrich(
            hunt_context=context,
            technique_id=body.get("technique_id", ""),
            incident_id=body.get("incident_id", ""),
        ))
