# SWAP POINT: To connect to a real MES, replace the mock data functions below with API calls
# to your MES system. The tool interfaces remain identical — no changes needed to the agent
# or Flask app.

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MES Mock Server")


def _mock_active_orders():
    return [
        {
            "order_id": "WO-2024-001",
            "product_name": "Hydraulic Valve Assembly",
            "quantity": 500,
            "due_date": "2024-05-22",
            "priority": "high",
            "current_operation": "CNC Machining",
            "percent_complete": 45,
        },
        {
            "order_id": "WO-2024-002",
            "product_name": "Pump Housing",
            "quantity": 200,
            "due_date": "2024-05-23",
            "priority": "high",
            "current_operation": "Assembly",
            "percent_complete": 72,
        },
        {
            "order_id": "WO-2024-003",
            "product_name": "Bearing Bracket",
            "quantity": 1000,
            "due_date": "2024-05-25",
            "priority": "medium",
            "current_operation": "Grinding",
            "percent_complete": 18,
        },
        {
            "order_id": "WO-2024-004",
            "product_name": "Shaft Coupling",
            "quantity": 300,
            "due_date": "2024-05-24",
            "priority": "medium",
            "current_operation": "Heat Treatment",
            "percent_complete": 60,
        },
        {
            "order_id": "WO-2024-005",
            "product_name": "Control Panel Cover",
            "quantity": 150,
            "due_date": "2024-05-26",
            "priority": "low",
            "current_operation": "Sheet Metal Forming",
            "percent_complete": 5,
        },
        {
            "order_id": "WO-2024-006",
            "product_name": "Gear Housing",
            "quantity": 75,
            "due_date": "2024-05-22",
            "priority": "high",
            "current_operation": "Milling",
            "percent_complete": 30,
        },
    ]


def _mock_machine_status():
    return [
        {
            "machine_id": "MCH-101",
            "machine_name": "CNC Machining Center 1",
            "status": "running",
            "oee_percent": 82,
            "current_order_id": "WO-2024-001",
            "fault_code": None,
            "estimated_recovery_minutes": None,
        },
        {
            "machine_id": "MCH-102",
            "machine_name": "CNC Machining Center 2",
            "status": "degraded",
            "oee_percent": 47,
            "current_order_id": "WO-2024-006",
            "fault_code": "F204-SPINDLE-VIBRATION",
            "estimated_recovery_minutes": 90,
        },
        {
            "machine_id": "MCH-103",
            "machine_name": "Surface Grinder",
            "status": "down",
            "oee_percent": 0,
            "current_order_id": "WO-2024-003",
            "fault_code": "E501-COOLANT-PUMP-FAILURE",
            "estimated_recovery_minutes": 240,
        },
        {
            "machine_id": "MCH-104",
            "machine_name": "Assembly Station A",
            "status": "running",
            "oee_percent": 91,
            "current_order_id": "WO-2024-002",
            "fault_code": None,
            "estimated_recovery_minutes": None,
        },
        {
            "machine_id": "MCH-105",
            "machine_name": "Heat Treatment Furnace",
            "status": "running",
            "oee_percent": 78,
            "current_order_id": "WO-2024-004",
            "fault_code": None,
            "estimated_recovery_minutes": None,
        },
        {
            "machine_id": "MCH-106",
            "machine_name": "Sheet Metal Press",
            "status": "degraded",
            "oee_percent": 55,
            "current_order_id": "WO-2024-005",
            "fault_code": "W301-DIE-WEAR",
            "estimated_recovery_minutes": 45,
        },
    ]


def _mock_inventory_levels():
    return [
        {
            "material_id": "MAT-001",
            "material_name": "Stainless Steel Bar Stock (304)",
            "on_hand_units": 2400,
            "allocated_units": 2200,
            "available_units": 200,
            "reorder_point": 500,
            "pending_receipt_date": "2024-05-24",
        },
        {
            "material_id": "MAT-002",
            "material_name": "Aluminum Billet 6061",
            "on_hand_units": 850,
            "allocated_units": 400,
            "available_units": 450,
            "reorder_point": 300,
            "pending_receipt_date": None,
        },
        {
            "material_id": "MAT-003",
            "material_name": "Hydraulic Seal Kit",
            "on_hand_units": 120,
            "allocated_units": 180,
            "available_units": -60,
            "reorder_point": 150,
            "pending_receipt_date": "2024-05-23",
        },
        {
            "material_id": "MAT-004",
            "material_name": "Bearing Assembly 6205",
            "on_hand_units": 340,
            "allocated_units": 280,
            "available_units": 60,
            "reorder_point": 200,
            "pending_receipt_date": None,
        },
        {
            "material_id": "MAT-005",
            "material_name": "Cold Rolled Steel Sheet 16ga",
            "on_hand_units": 75,
            "allocated_units": 120,
            "available_units": -45,
            "reorder_point": 100,
            "pending_receipt_date": "2024-05-25",
        },
        {
            "material_id": "MAT-006",
            "material_name": "Cutting Tool Inserts CNMG",
            "on_hand_units": 48,
            "allocated_units": 60,
            "available_units": -12,
            "reorder_point": 80,
            "pending_receipt_date": "2024-05-22",
        },
        {
            "material_id": "MAT-007",
            "material_name": "Coolant Concentrate",
            "on_hand_units": 200,
            "allocated_units": 80,
            "available_units": 120,
            "reorder_point": 100,
            "pending_receipt_date": None,
        },
        {
            "material_id": "MAT-008",
            "material_name": "Gear Blank Steel 4140",
            "on_hand_units": 90,
            "allocated_units": 75,
            "available_units": 15,
            "reorder_point": 50,
            "pending_receipt_date": None,
        },
    ]


def _mock_workforce_availability():
    return [
        {
            "shift": "Day Shift",
            "start_time": "06:00",
            "end_time": "14:00",
            "required_headcount": 22,
            "available_headcount": 19,
            "certified_operators": 14,
            "gap": 3,
            "critical_roles_unfilled": ["CNC Machinist Level 3", "Quality Inspector"],
        },
        {
            "shift": "Evening Shift",
            "start_time": "14:00",
            "end_time": "22:00",
            "required_headcount": 18,
            "available_headcount": 18,
            "certified_operators": 12,
            "gap": 0,
            "critical_roles_unfilled": [],
        },
        {
            "shift": "Night Shift",
            "start_time": "22:00",
            "end_time": "06:00",
            "required_headcount": 12,
            "available_headcount": 7,
            "certified_operators": 5,
            "gap": 5,
            "critical_roles_unfilled": [
                "CNC Machinist Level 2",
                "Assembly Technician",
                "Maintenance Tech",
            ],
        },
    ]


@mcp.tool()
def get_active_orders() -> list[dict]:
    """Return all active production orders with their current status and progress."""
    return _mock_active_orders()


@mcp.tool()
def get_machine_status() -> list[dict]:
    """Return current status of all production machines including OEF, faults, and recovery estimates."""
    return _mock_machine_status()


@mcp.tool()
def get_inventory_levels() -> list[dict]:
    """Return inventory levels for all tracked materials including allocated quantities and reorder status."""
    return _mock_inventory_levels()


@mcp.tool()
def get_workforce_availability() -> list[dict]:
    """Return workforce headcount and certification data for current and upcoming shifts."""
    return _mock_workforce_availability()


if __name__ == "__main__":
    mcp.run(transport="stdio")
