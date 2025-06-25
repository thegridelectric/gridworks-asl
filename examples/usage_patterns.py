"""Usage patterns for GridWorks TypeRegistry."""

from gridworks_typeregistry import (
    NodeGt, 
    ComponentGt,
    DataChannelGt,
    PowerWatts,
    TelemetryName
)

# Basic node creation
def create_simple_node():
    """Simple node with string-based fields."""
    return NodeGt(
        Name="sensor-001",
        ActorClass="temperature_sensor",
        DisplayName="Living Room Temperature Sensor"
    )

# Working with components  
def create_component():
    """Basic component definition."""
    return ComponentGt(
        ComponentId="comp-abc-123",
        DisplayName="eGauge Power Meter",
        HwUid="BP01349"
    )

# Data channels
def create_data_channel():
    """Data channel for telemetry."""
    return DataChannelGt(
        Name="living-room-temp",
        DisplayName="Living Room Temperature",
        AboutNodeName="temp-sensor-1", 
        CapturedByNodeName="scada-main",
        TelemetryName=TelemetryName.TEMPERATURE_C.value,  # Use enum value
        TerminalAssetAlias="hw1.isone.me.home.ta",
        Id="uuid-abc-123"
    )

# Power reporting
def send_power_reading(watts: int):
    """Send power reading message.""" 
    return PowerWatts(Watts=watts)

# JSON compatibility
def demonstrate_json_compatibility():
    """Show how ASL types work with JSON."""
    node = create_simple_node()
    
    # Serializes with CamelCase
    json_data = node.model_dump_json()
    print(json_data)  
    # {"Name": "sensor-001", "ActorClass": "temperature_sensor", ...}
    
    # Deserializes from CamelCase
    restored = NodeGt.model_validate_json(json_data)
    assert restored.Name == node.Name

if __name__ == "__main__":
    # Run examples
    node = create_simple_node()
    component = create_component() 
    channel = create_data_channel()
    power = send_power_reading(1500)
    
    print("✅ All examples created successfully!")
    demonstrate_json_compatibility()