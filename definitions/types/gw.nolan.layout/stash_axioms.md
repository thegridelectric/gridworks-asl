# gw.nolan.layout — stashed axioms (deferred)

The `x-gridworks.axioms` for `gw.nolan.layout/000`, lifted out of `000.yaml` so the type
generates a runtime **without** axiom validators (per hardware-layout-pass-one — full layouts
now, axioms implemented later). To re-enable, drop this block back under `x-gridworks:` in
`000.yaml`. Markdown (not yaml) so sema tooling/tests skip it.

```yaml
  axioms:
    - number: 1
      name: "NolanGNodeSet"
      statement: >
        GNodes SHALL contain exactly three elements. The set of their
        GNodeClass values SHALL be exactly {"Scada", "TerminalAsset",
        "LeafTransactiveNode"}.
        The Alias of the LeafTransactiveNode SHALL be the parent alias of both the Scada and
        TerminalAsset aliases (i.e., the Scada alias SHALL equal "<LeafAlias>.scada" and the
        TerminalAsset alias SHALL equal "<LeafAlias>.ta").
    - number:
      name: "GlobalIdUniqueness"
      statement: >
        The following identifiers SHALL be globally unique across the entire layout:
          - ShNode.ShNodeId
          - Component.ComponentId
          - DataChannel.Id
          - DerivedChannel.Id
          - GNode.GNodeId
        No identifier value appearing in any one of the above sets SHALL appear
        in any other set.
    - number:
      name: "DeviceTypeMembership"
      statement: >
        Device-type membership. Every Component's DeviceType SHALL be a member of the
        `gw1.device.type` enum. Furthermore, for every Component whose DeviceType requires a
        specialized device-type record (a category that carries category-level data beyond
        its name — e.g. an electric meter, an ADS111x-based sensor, a GW108 board), the
        DeviceTypes array SHALL contain a `<family>.device.type.gt` whose DeviceType value
        equals the Component's DeviceType. A Component whose category carries no
        category-level data needs no record. Consistency is a layout invariant, not a
        per-component flag.
    - number:
      name: "ComponentConfigListExistence"
      statement: >
        Every Component SHALL contain a ConfigList field, which MAY be empty.
    - number:
      name: "HydronicStructure"
      statement: >
        The Hydronic object SHALL contain:
          - TotalStoreTanks: a non-negative integer
          - StoreTankIndices: a list of integers
          - ZoneList: a list of strings
          - CriticalZoneList: a list of strings
          - ZoneKwhPerDegFList: a list of numeric values
        StoreTankIndices SHALL:
          - contain unique integer values
          - be sorted in ascending order
          - have length equal to TotalStoreTanks
          - contain only integers in the range 1 through 6 inclusive
        ZoneList SHALL:
          - contain at least one element
          - contain unique values
          - contain only valid SpaceheatName values
        CriticalZoneList SHALL:
          - be a sublist of ZoneList
        ZoneKwhPerDegFList SHALL:
          - contain only numeric values greater than or equal to zero
          - have length equal to the length of ZoneList
          - be index-aligned with ZoneList (i.e., the ith element corresponds to ZoneList[i])
    - number: 
      name: "ShNodeNameUniqueness"
      statement: >
        The Name field SHALL be unique across all ShNodes.
    - number: 
      name: "CoreShNodesExistenceAndActorClass"
      statement: >
        The ShNodes list SHALL contain a node with each of the following Names.
        The Name and ActorClass of each such node SHALL match the following mapping:
          "s"                → ActorClass "PrimaryScada"
          "s2"               → ActorClass "SecondaryScada"
          "power-meter"      → ActorClass "PowerMeter"
          "ltn"              → ActorClass "NoActor"
          "la"               → ActorClass "LeafAlly"
          "lc"               → ActorClass "LocalControl"
          "admin"            → ActorClass "NoActor"
          "auto"             → ActorClass "NoActor"
          "derived-generator"→ ActorClass "DerivedGenerator"
        No additional ShNode with any of the above Names SHALL exist.
    - number: 
      name: "HydronicShNodesExistenceAndActorClass"
      statement: >
        The ShNodes list SHALL contain a node with each of the following Names.
        # Local control nodes:
          - "n"
          - "backup"
          - "scada-blind"
          - "pico-cycler"
          - "hp-boss"
        # Transactive asset nodes:
          - "heat-pump"
          - "buffer-top-elt"
          - "buffer-bottom-elt"
          - "store-top-elt"
          - "store-bottom-elt"
        # Pump nodes:
          - "dist-pump"
          - "store-pump"
        # Pipe temperature nodes:
          - "dist-swt"
          - "dist-rwt"
          - "hp-lwt"
          - "hp-ewt"
          - "store-hot-pipe"
          - "store-cold-pipe"
          - "buffer-hot-pipe"
          - "buffer-cold-pipe"
        # Buffer temperature nodes:
          - "buffer-depth1"
          - "buffer-depth2"
          - "buffer-depth3"
        ActorClass constraints:
          - The node with Name "pico-cycler" SHALL have ActorClass "PicoCycler".
          - The node with Name "hp-boss" SHALL have ActorClass "HpBoss"
        All other nodes listed above MAY have ActorClass "NoActor" or another
        ActorClass consistent with their function.
    - number: 
      name: "NolanNodesExistenceAndActorClass"
      statement: >
        The ShNodes list SHALL contain nodes with the following Names.
          Pipe temperature nodes:
            - "floor-swt"
    - number: 
      name: "HandleTopologyRequirements"
      statement: >
        Define the effective Handle of a ShNode as:
          - Handle, if Handle is present
          - otherwise Name
        The following effective Handle values SHALL exist across the ShNodes:
          - "ltn"
          - "auto"
          - "ltn.la"
          - "auto.lc"
          - "auto.pico-cycler"
          - "auto.lc.n"
          - "auto.lc.backup"
          - "auto.lc.scada-blind"
          - "auto.lc.n.hp-boss"
          - "auto.pico-cycler.vdc-relay-gpio-23"
          - "auto.lc.n.buffer-top-relay"
          - "auto.lc.n.buffer-bottom-relay"
          - "auto.lc.n.store-top-relay"
          - "auto.lc.n.store-bottom-relay"
        Closure:
          - For every effective Handle listed above, all prefix handles SHALL
            correspond to the effective Handle of another ShNode.
    - number: 
      name: "ActorHierarchyClosure"
      statement: >
        For every ShNode with a non-null ActorHierarchyName, all prefix handles
        obtained by iteratively removing the final segment SHALL correspond to
        the ActorHierarchyName of another ShNode in the ShNodes list.
        Additionally, each such parent ShNode SHALL have ActorClass not equal to "NoActor".
    - number:
      name: "ZoneShNodeStructure"
      statement: >
        Let ZoneList be the list of zone labels defined in Hydronic.
        For each zone label Z at index i (1-based) in ZoneList:
          1. Required node names:
            - A ShNode with Name equal to "zone{i}-{Z}" SHALL exist.
            - A ShNode with Name equal to "zone{i}-{Z}-whitewire" SHALL exist.
            - A ShNode with Name equal to "zone{i}-{Z}-stat" SHALL exist.
            - A ShNode with Name equal to "zone{i}-{Z}-floor" SHALL exist.
          2. Index constraints:
            - i SHALL be in the range 1 through 6 inclusive.
          3. Uniqueness:
            - No additional ShNode names matching the pattern "zone{i}-{Z}*"
              SHALL exist other than those defined above
    - number:
      name: "TankShNodeStructure"
      statement: >
        Let TotalStoreTanks be the integer defined in Hydronic.
        1. Store tank nodes:
          - For each tank index i in the range 1 through TotalStoreTanks inclusive:
              - A ShNode with Name equal to "tank{i}" SHALL exist.
              - The following ShNodes SHALL exist:
                  - "tank{i}-depth1"
                  - "tank{i}-depth2"
                  - "tank{i}-depth3"
        2. Index constraints:
          - TotalStoreTanks SHALL be in the range 0 through 6 inclusive.
        3. Closure:
          - If a ShNode Name matches either pattern:
              - "tank{i}-depth{j}"
              - "buffer-depth{j}"
            then j SHALL be one of 1, 2, or 3, and i SHALL be a positive integer
            less than or equal to TotalStoreTanks.
    - number:
      name: "ComponentReferenceIntegrity"
      statement: >
        For every ShNode:
          - If ComponentId is present, a component with that ComponentId
            SHALL exist in Components.
          - If BoardComponentId is present, a component with that ComponentId
            SHALL exist in Components.
    - number:
      name: "CoreChannelExistence"
      statement: >
        There SHALL exist exactly one DerivedChannel whose Name is equal to "asset-electric-power".
    - number:
      name: "HydronicChannelExistence"
      statement: >
        The following channels SHALL exist in the union of DataChannels and
        DerivedChannels:
          # Power reading channels
            - "heat-pump-pwr"
            - "dist-pump-pwr"
            - "store-pump-pwr"
            - "buffer-top-elt-pwr"
            - "buffer-bottom-elt-pwr"
            - "store-top-elt-pwr"
            - "store-bottom-elt-pwr"
          # Effective pipe temperature channels
            - "dist-swt"
            - "dist-rwt"
            - "hp-lwt"
            - "hp-ewt"
            - "store-hot-pipe"
            - "store-cold-pipe"
            - "buffer-hot-pipe"
            - "buffer-cold-pipe"
          # Effective buffer temperature channels:
            - "buffer-depth1"
            - "buffer-depth2"
            - "buffer-depth3"
          # Pipe flows
            - "dist-flow"
            - "primary-flow"
            - "store-flow"
          # Energy estimates
            - "required-energy"
            - "usable-energy"
          # Relay states 
            - "vdc-relay"
            - "buffer-top-relay" 
            - "buffer-bottom-relay"
            - "store-top-relay"
            - "store-bottom-relay"
    - number:
      name: "NolanChannelExistence"
      statement: >
        The following channels SHALL exist in the union of DataChannels and
        DerivedChannels:
          - "floor-swt"
    - number:
      name: "TankChannelStructure"
      statement: >
        For every ShNode whose Name is required by TankShNodeStructure and matches
        either pattern:
          - "buffer-depth{j}"
          - "tank{i}-depth{j}"
        there SHALL exist exactly one channel in the union of DataChannels and
        DerivedChannels whose Name is equal to the ShNode Name.
    - number:
        name: "ZoneChannelStructure"
        statement: >
          Let ZoneList be the list of zone labels defined in Hydronic.
          For each zone label Z at index i (1-based) in ZoneList, let base be
          "zone{i}-{Z}".
          The following channels SHALL exist in the union of DataChannels and
          DerivedChannels:
            - "{base}-temp"
            - "{base}-set"
            - "{base}-heat-call"
            - "{base}-failsafe-relay"
            - "{base}-ops-relay"
            - "{base}-floor-temp"
    - number:
      name: "ChannelBindingIntegrity"
      statement: >
        For each DataChannel and DerivedChannel, the following SHALL hold:
          1. ShNode references:
            - If AboutNodeName is present, there SHALL exist a ShNode with
              Name equal to AboutNodeName.
            - If CapturedByNodeName is present, there SHALL exist a ShNode
              with Name equal to CapturedByNodeName.
          2. Channel name uniqueness:
            - The Name field SHALL be unique across the union of all
              DataChannels and DerivedChannels.
    - number:
      name: "ComponentDataChannelBijection"
      statement: >
        Let C be the set of all ChannelName values appearing in the ConfigList
        of all components.
        Let D be the set of all Name values of DataChannels.
          - C SHALL equal D.    
    - name: "ChannelCaptureConsistency"
      statement: >
        For each ShNode N:
        If N is associated with a component whose ConfigList has non-zero length,
        then for each such ChannelName:
          Let DC be the DataChannel with Name equal to ChannelName.
          - DC.CapturedByNodeName SHALL equal N.Name.    
    - number: 
      name: "RelayBoardConfigBijection"
      statement: >
        1. For every ShNode with ActorClass equal to "Relay":
            - BoardComponentId SHALL be present.
            - There SHALL exist exactly one component in Components whose
                ComponentId equals BoardComponentId.
            - Within that component's ConfigList there SHALL exist exactly
            one object with:
                - TypeName equal to "relay.actor.config"
                - Version equal to "003"
                - ActorName equal to the ShNode Name.
        2.For every component in Components, and for every object in that
          component's ConfigList with:
          - TypeName equal to "relay.actor.config"
          - Version equal to "003"
          there SHALL exist exactly one ShNode with:
          - ActorClass equal to "Relay"
          - Name equal to the ActorName of that config.
    - number:
      name: "PowerMeteringNodeChannelConsistency"
      statement: >
        For each ShNode:
          - ShNode.InPowerMetering SHALL be true if and only if there exists
            exactly one DataChannel such that:
              - DataChannel.AboutNodeName equals the ShNode Name
              - DataChannel.TelemetryName equals "PowerW"
              - DataChannel.InPowerMetering is true
    - number:
      name: "AssetElectricPowerSemantics"
      statement: >
        The DerivedChannel with Name equal to "asset-electric-power" SHALL satisfy:
          - Strategy SHALL be "sum".
          - InputChannelNames SHALL equal the set of Names of all DataChannels
            for which InPowerMetering is true.
          - OutputUnit SHALL be "Watts".
          - OutputQuantity SHALL be "Power".
          - EmissionMethod SHALL be "AsyncAndPeriodic".
    - number:
      name: "PowerMeteringChannelSemantics"
      statement: >
        For each DataChannel whose Name is one of:
          - "heat-pump-pwr"
          - "buffer-top-elt-pwr"
          - "buffer-bottom-elt-pwr"
          - "store-top-elt-pwr"
          - "store-bottom-elt-pwr"
        the following SHALL hold:
          - InPowerMetering SHALL be true.
          - AboutNodeName SHALL equal the channel Name with the suffix "-pwr"
            removed.
    - number:
      name: "PipeTemperatureChannelSemantics"
      statement: >
        For each channel whose Name is one of:
          - "dist-swt"
          - "dist-rwt"
          - "hp-lwt"
          - "hp-ewt"
          - "store-hot-pipe"
          - "store-cold-pipe"
          - "buffer-hot-pipe"
          - "buffer-cold-pipe"
        there SHALL exist exactly one channel in the union of DataChannels
        and DerivedChannels such that:
          - AboutNodeName SHALL equal the channel Name.
          - If the channel is a DerivedChannel:
              - OutputUnit SHALL be "FahrenheitX100".
              - OutputQuantity SHALL be "Temperature".
          - If the channel is a DataChannel:
              - TelemetryName SHALL be one of:
                  - "WaterTempCTimes1000"
                  - "CelsiusTimes100"
    - number:
      name: "TankTemperatureChannelSemantics"
      statement: >
        For each channel whose Name matches either pattern:
          - "buffer-depth{j}"
          - "tank{i}-depth{j}"
        there SHALL exist exactly one DerivedChannel such that:
          - Name SHALL equal the channel Name.
          - AboutNodeName SHALL equal the channel Name.
          - OutputUnit SHALL be "FahrenheitX100".
          - OutputQuantity SHALL be "Temperature".
          - Strategy SHALL be "affine" or "identity".
    - number:
      name: "PipeFlowChannelSemantics"
      statement: >
        For each DataChannel whose Name is one of:
          - "dist-flow"
          - "primary-flow"
          - "store-flow"
      the following SHALL hold:
        - TelemetryName SHALL be "GpmTimes100".
        - AboutNodeName SHALL equal the channel Name.
    - number:
      name: "EnergyChannelSemantics"
      statement: >
        For each DerivedChannel whose Name is one of:
          - "usable-energy"
          - "required-energy"
        the following SHALL hold:
          - Strategy SHALL be "system-model".
          - OutputUnit SHALL be "WattHours".
          - OutputQuantity SHALL be "Energy".
          - EmissionMethod SHALL be "Periodic".
          - EmitPeriodS SHALL be 60.
          - InputChannelNames SHALL be empty.
          - Parameters.EnergyModel.TypeName SHALL equal:
              - "gw0.usable.energy.layered" for "usable-energy"
              - "gw0.required.energy.layered" for "required-energy"
    - number:
      name: "VdcRelaySemantics"
      statement: >
        The DataChannel with Name "vdc-relay" SHALL satisfy the following:
        Let N be the ShNode with Name equal to the DataChannel's AboutNodeName
          1. Structural channel properties:
            - TelemetryName SHALL equal "RelayState".
          2. ShNode binding:
            - N SHALL have ActorClass equal to "Relay".
          3. Handle topology:
            - The effective Handle of N SHALL equal
              "auto.pico-cycler.<AboutNodeName>".
          4. Relay configuration:
          - The relay.actor.config associated with N (as defined by
            RelayBoardConfigBijection) SHALL have:
              - StateType equal to "relay.closed.or.open"
              - EventType equal to "change.relay.state"
              - WiringConfig equal to "NormallyClosed"
    - number:
      name: "ElementRelaySemantics"
      statement: >
        For each DataChannel whose Name is one of:
          - "buffer-top-relay"
          - "buffer-bottom-relay"
          - "store-top-relay"
          - "store-bottom-relay"
        let N be the ShNode with Name equal to the DataChannel's AboutNodeName.
        The following SHALL hold:
          1. Channel properties:
            - TelemetryName SHALL equal "RelayState".
          2. ShNode binding:
            - N SHALL have ActorClass equal to "Relay".
          3. Relay configuration:
            - The relay.actor.config associated with N (as defined by
              RelayBoardConfigBijection) SHALL have:
                - StateType equal to "relay.closed.or.open"
                - EventType equal to "change.relay.state"
                - WiringConfig equal to "NormallyOpen"
    - number:
      name: "ZoneFailsafeRelaySemantics"
      statement: >
        For each DataChannel whose Name matches the pattern:
          - "zone{i}-{label}-failsafe-relay{n}"
        let N be the ShNode with Name equal to the DataChannel's AboutNodeName.
        The following SHALL hold:
          1. Channel properties:
            - TelemetryName SHALL equal "RelayState".
          2. ShNode binding:
            - N SHALL have ActorClass equal to "Relay".
          3. Relay configuration:
            - The relay.actor.config associated with N (as defined by
              RelayBoardConfigBijection) SHALL have:
                - StateType equal to "heatcall.source"
                - EventType equal to "change.heatcall.source"
                - WiringConfig equal to "DoubleThrow"
    - number:
      name: "ZoneOpsRelaySemantics"
      statement: >
        For each DataChannel whose Name matches the pattern:
          - "zone{i}-{label}-ops-relay{n}"
        let N be the ShNode with Name equal to the DataChannel's AboutNodeName.
        The following SHALL hold:
          1. Channel properties:
            - TelemetryName SHALL equal "RelayState".
          2. ShNode binding:
            - N SHALL have ActorClass equal to "Relay".
          3. Relay configuration:
            - The relay.actor.config associated with N (as defined by
              RelayBoardConfigBijection) SHALL have:
                - StateType equal to "relay.closed.or.open"
                - EventType equal to "change.relay.state"
                - WiringConfig equal to "NormallyOpen"
    - number:
      name: "ZoneRoomTempChannelSemantics"
      statement: >
        For each zone label Z at index i (1-based) in ZoneList, let base be
        "zone{i}-{Z}".
        The channel with Name "{base}-temp" SHALL be a DerivedChannel such that:
          - AboutNodeName SHALL equal "{base}".
          - OutputUnit SHALL be "FahrenheitX100".
          - OutputQuantity SHALL be "Temperature".
    - number:
      name: "ZoneSetpointChannelSemantics"
      statement: >
        For each zone label Z at index i (1-based) in ZoneList, let base be
        "zone{i}-{Z}".
        The channel with Name "{base}-set" SHALL be a DerivedChannel such that:
          - AboutNodeName SHALL equal "{base}-stat".
          - OutputUnit SHALL be "FahrenheitX100".
          - OutputQuantity SHALL be "Temperature".
    - number:
      name: "ZoneFloorTempChannelSemantics"
      statement: >
        For each zone label Z at index i (1-based) in ZoneList, let base be
        "zone{i}-{Z}".
        The channel with Name "{base}-floor-temp" SHALL be a DerivedChannel such that:
          - AboutNodeName SHALL equal "{base}".
          - OutputUnit SHALL be "FahrenheitX100".
          - OutputQuantity SHALL be "Temperature".
    - number:
      name: "HeatCallChannelSemantics"
      statement: >
        For each zone label Z at index i (1-based) in ZoneList, let base be
        "zone{i}-{Z}".
        The channel with Name "{base}-heat-call" SHALL be a DerivedChannel such that:
          - AboutNodeName SHALL equal "{base}-whitewire".
          - Strategy SHALL be "heat-call".
          - InputChannelNames SHALL contain exactly one element C such that:
            - C SHALL be the Name of a DataChannel.
            - C SHALL match the pattern "{base}-whitewire-*".
            - The DataChannel with Name C SHALL have:
                - AboutNodeName equal to "{base}-whitewire".
          - OutputQuantity SHALL be "Unitless".
          - OutputUnit SHALL be "Unitless".
          - EmissionMethod SHALL be "AsyncAndPeriodic".
          - Parameters SHALL contain:
              - "Interpretation"
          - Parameters SHALL contain:
            - "Interpretation"
            - Parameters["Interpretation"] SHALL be an object with:
              - TypeName equal to "gw1.heat.call.interpretation"
              - Version equal to "000"
    - number:
      name: "MakeModelCacIdConsistency"
      statement: >
        DRAFT / DEFERRED ENFORCEMENT (this layout is draft, so this axiom is
        documentation of intent until the layout publishes). For each DeviceType
        that is a component.attribute.class.gt with a known (non-Unknown) MakeModel,
        ComponentAttributeClassId SHALL equal the canonical id assigned to that
        MakeModel by the GridWorks MakeModel -> ComponentAttributeClassId mapping;
        a DeviceType with MakeModel UnknownMake__UnknownModel MAY use any UUID. This
        is the in-canon home for the bijection currently hardcoded in scada
        (CACS_BY_MAKE_MODEL, component_attribute_class_gt.py). Enforcement stays
        scada-side for now; this axiom goes live when the mapping is formalized as
        gw1.* vocabulary (a gw1.cac.id enum + a gw1.make.model.cac.id projection)
        and this layout type publishes. TODO: formalize the gw1.* projection and
        migrate enforcement from scada into this axiom. Rationale: enforcing here (on
        the layout, the cross-system artifact) keeps device-type + components
        version-stable while making the layout self-validating; enforcing on the
        device-type itself would version-couple it to the mapping and ripple on
        every device-type addition.
```
