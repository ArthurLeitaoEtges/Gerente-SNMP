from flask import Flask, jsonify, request
from pysnmp.hlapi import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd,
)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as requisições


def snmp_get(oid, host="127.0.0.1", port=16100, community="public", timeout=0.5, retries=1):
    """Perform an SNMP GET for the given OID on the local agent.

    Returns the value as string on success or raises RuntimeError on failure.
    """
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((host, port), timeout=timeout, retries=retries),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        raise RuntimeError(str(errorIndication))
    if errorStatus:
        # errorIndex is 1-based
        idx = int(errorIndex) - 1 if errorIndex else None
        where = varBinds[idx][0] if idx is not None and idx < len(varBinds) else "?"
        raise RuntimeError(f"{errorStatus.prettyPrint()} at {where}")

    # Return the value (as string) for the first varBind
    for varBind in varBinds:
        # varBind is a tuple (ObjectIdentity, ObjectValue)
        return str(varBind[1])

    return None


@app.route("/api/snmp/<path:oid>", methods=["GET"])
def api_get_oid(oid):
    """HTTP endpoint that returns the SNMP GET result for <oid>.

    Example: GET /api/snmp/1.3.6.1.2.1.1.1.0
    """
    # Optional query params to override target host/port/community
    host = request.args.get("host", "127.0.0.1")
    port = int(request.args.get("port", 16100))
    community = request.args.get("community", "public")

    try:
        value = snmp_get(oid, host=host, port=port, community=community)
        return jsonify({"oid": oid, "value": value, "host": host, "port": port}), 200
    except Exception as exc:
        return (
            jsonify({"error": "SNMP query failed", "details": str(exc), "oid": oid}),
            500,
        )


if __name__ == "__main__":
    # Run development server. Use the venv's python to start this file.
    app.run(host="0.0.0.0", port=5000, debug=True)
