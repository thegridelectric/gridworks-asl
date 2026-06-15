# gw.house0.layout — stashed axioms (deferred)

The `x-gridworks.axioms` for `gw.house0.layout/000`, kept here (markdown, so sema tooling/tests
skip it) until enforcement is wired. To enable, drop the `axioms:` block back under `x-gridworks:`
in `000.yaml` — but note the runtime then generates validators that run against the type's
**example**, so enforcement needs a real (bijection-generated) House0 example first; today the
example is the minimal `{TypeName, Version}` stub. Same pattern as `gw.nolan.layout`.

These are **ported from the live data-class validations** in
`gwsproto/data_classes/house_0_layout.py` and the base `gwsproto/data_classes/hardware_layout.py`
(file:line anchors below) — the invariants the loader enforces today. The bijection harness
(`gw_spaceheat/house0_bijection.py`) guarantees the sema type carries every field these reference.

```yaml
  axioms:
    - number: 1
      name: "House0GNodeSet"
      statement: >
        GNodes SHALL contain exactly three elements, whose GNodeClass values are exactly
        {"Scada", "TerminalAsset", "LeafTransactiveNode"}. The LeafTransactiveNode Alias SHALL be
        the parent of the other two: Scada Alias == "<LtnAlias>.scada", TerminalAsset Alias ==
        "<LtnAlias>.ta". (g.node.gt carries its own BaseClass/Status/PositionPointId axioms.)
    - number: 2
      name: "GlobalIdUniqueness"
      statement: >
        ShNode.ShNodeId, Component.ComponentId, DataChannel.Id, DerivedChannel.Id and
        GNode.GNodeId SHALL each be globally unique; no id value SHALL appear in more than one of
        these sets. (hardware_layout.py check_node_unique_ids.)
    - number: 3
      name: "DeviceTypeMembership"
      statement: >
        Every Component's DeviceType SHALL be a member of the gw1.device.type enum. For every
        Component whose category carries category-level data (e.g. electric meter, ADS111x sensor,
        GW108 board), DeviceTypes SHALL contain a <family>.device.type.gt whose DeviceType equals
        the Component's DeviceType. A category with no category-level data needs no record.
    - number: 4
      name: "ComponentConfigListExistence"
      statement: >
        Every Component SHALL contain a ConfigList field (which MAY be empty).
    - number: 5
      name: "HydronicStructure"
      statement: >
        Hydronic SHALL contain: TotalStoreTanks (integer, 1..6); ZoneList (1..6 strings);
        CriticalZoneList (a subset of ZoneList); ZoneKwhPerDegFList (numeric, length == len(ZoneList));
        TankTempCalibrationMap (with exactly TotalStoreTanks tank entries); FlowManifoldVariant
        (House0 | House0Sieg); UseSiegLoop (bool); Strategy. (house_0_layout.py __init__ lines
        98-156.)
    - number: 6
      name: "EssentialNodesExistence"
      statement: >
        ShNodes SHALL include the primary-scada (s), ltn, leaf-ally (la), local-control (lc) and
        derived-generator nodes. (house_0_layout.py validate_house0 lines 344-388.)
    - number: 7
      name: "PicoCyclerForPicoActors"
      statement: >
        If any ShNode has ActorClass in {ApiFlowModule, ApiTankModule, ApiBtuMeter}, a pico-cycler
        node SHALL exist. (house_0_layout.py lines 363-383 — currently commented out in the loader;
        carried as an owed invariant.)
    - number: 8
      name: "RequiredTopologyNodesExistence"
      statement: >
        ShNodes SHALL include the House0 topology nodes: heat pump (hp-odu, hp-idu); pumps
        (dist-pump, primary-pump, store-pump); pipe temps (dist-swt, dist-rwt, hp-lwt, hp-ewt,
        store-hot-pipe, store-cold-pipe, buffer-hot-pipe); flows (dist-flow, primary-flow,
        store-flow); the relay set; the 0-10V outputs (dist-010v, primary-010v, store-010v); buffer
        depths (buffer-depth1..3); tank depths (tank{i}-depth1..3 for each store tank); and per-zone
        nodes zone{i}-{name}, -stat, -whitewire. (house_0_layout.py required_topology_nodes lines
        558-606.)
    - number: 9
      name: "WebServerDefaultExistence"
      statement: >
        Components SHALL include at least one web.server.component named "default".
        (house_0_layout.py lines 141-150.)
    - number: 10
      name: "TankTempCalibrationConsistency"
      statement: >
        For buffer and each store tank, every depth (1,2,3) SHALL have a DerivedChannel
        "<reader>-depth<d>" whose Strategy is "identity" (iff TMap M==1.0, B==0.0) or "affine"
        (with Parameters.Calibration M,B equal to the TankTempCalibrationMap entry).
        (house_0_layout.py validate_tank_temp_calibration_consistency lines 165-224.)
    - number: 11
      name: "SystemModelEnergyChannels"
      statement: >
        DerivedChannels SHALL include usable-energy and required-energy, each CreatedByNodeName
        "derived-generator", Strategy "system-model", with Parameters.EnergyModel.TypeName one of
        {usable.energy.layered, required.energy.layered} — exactly one of each.
        (house_0_layout.py validate_house0_system_models lines 226-300.)
    - number: 12
      name: "SiegLoopConsistency"
      statement: >
        If UseSiegLoop is true, FlowManifoldVariant SHALL be House0Sieg.
        (house_0_layout.py line 394.)
    - number: 13
      name: "SiegManifoldChannels"
      statement: >
        If FlowManifoldVariant is House0Sieg, DataChannels SHALL include
        hp-loop-on-off-relay<n>-state and hp-loop-keep-send-relay<n>-state.
        (house_0_layout.py check_house0_sieg_manifold lines 422-431.)
    - number: 14
      name: "SiegActorConsistency"
      statement: >
        If UseSiegLoop is true, ShNodes SHALL include a SiegLoop node (ActorClass SiegLoop) and an
        HpBoss node (ActorClass HpBoss); if false, no SiegLoop node SHALL exist.
        (house_0_layout.py check_actors_when_using/not_using_sieg_loop lines 433-449.)
    - number: 15
      name: "HandleTopologyClosure"
      statement: >
        For every ShNode whose Handle contains a ".", the parent handle SHALL resolve to an
        existing ShNode. (hardware_layout.py check_handle_hierarchy.)
    - number: 16
      name: "ActorComponentConsistency"
      statement: >
        A PowerMeter node's Component SHALL be an electric.meter.component.gt; a MultipurposeSensor
        node's Component SHALL be an ads111x.based.component.gt.
        (hardware_layout.py check_actor_component_consistency.)
    - number: 17
      name: "ComponentDataChannelConsistency"
      statement: >
        Every ChannelName in any Component's ConfigList SHALL exist in DataChannels, and every
        DataChannel SHALL be referenced by some Component (no orphans).
        (hardware_layout.py check_data_channel_consistency.)
    - number: 18
      name: "TransactiveMeteringConsistency"
      statement: >
        If a DataChannel has InPowerMetering true, its AboutNode SHALL have InPowerMetering true;
        and every InPowerMetering node SHALL have at least one matching channel.
        (hardware_layout.py check_transactive_metering_consistency.)
    - number: 19
      name: "AdsTerminalBlockValidity"
      statement: >
        For an ADS111x-based component, every ConfigList TerminalBlockIdx SHALL fit within the
        component's TotalTerminalBlocks. (hardware_layout.py, ADS terminal-block check.)
    - number: 20
      name: "DerivedChannelInputIntegrity"
      statement: >
        Every DerivedChannel's InputChannelNames SHALL reference existing DataChannels (or
        DerivedChannels), and each Strategy's required Parameters SHALL be present and well-formed
        (identity, affine, heat-call, simple-falling-edge-setpoint, system-model).
        (hardware_layout.py validate_derived_channels.)

    # --- Zone-related axioms (beyond the data-class set; use gwsproto/names house0
    #     zone naming — see the design's names-sweep note) ---
    - number: 21
      name: "ZoneWhitewirePwrChannel"
      statement: >
        MVP zone axiom. For each zone label Z at 1-based index i in Hydronic.ZoneList, let
        base = "zone{i}-{Z}".lower() (gwsproto/names house0 ZoneChannelNames). A DataChannel named
        "{base}-whitewire-pwr" SHALL exist — the per-zone whitewire power reading
        (house_0_names self.whitewire_pwr). This is the minimal zone requirement; ZoneStructure
        below is the fuller form.
    - number: 22
      name: "ZoneStructure"
      statement: >
        Connect-everything zone axiom (adapted from gw.nolan.layout ZoneShNodeStructure +
        ZoneChannelStructure, using gwsproto/names house0 zone naming). For each zone label Z at
        1-based index i in Hydronic.ZoneList (i in 1..6), let base = "zone{i}-{Z}".lower():
          1. ShNodes SHALL include "{base}", "{base}-stat", and "{base}-whitewire".
          2. The union of DataChannels and DerivedChannels SHALL include "{base}-whitewire-pwr" and
             "{base}-stat-temp".
          3. Those channels SHALL bind to the zone's nodes (AboutNodeName / CapturedByNodeName
             resolve to the zone ShNodes above), per ChannelBindingIntegrity.
          4. No ShNode whose Name matches "zone{i}-{Z}*" SHALL exist beyond those in (1).
```
