# KEBA Charging Station (Multi)

Custom Home Assistant integration to manage **multiple KEBA charging stations**
(P20 / P30 series) using the **Smart Home UDP interface**.

This integration is a multi-host extension of the official Home Assistant
`keba` integration and allows adding **one configuration entry per charging station**.

---

## Features

- Support for **multiple KEBA charging stations** (one per host/IP)
- Each charging station is exposed as a **separate Home Assistant device**
- Uses the **official KEBA Smart Home UDP protocol**
- Persistent UDP communication (stateful, reliable)
- Sensors, binary sensors, lock and notification services
- Compatible with external OCPP backends (e.g. **SteVe**)
- Designed for advanced and semi-professional installations

---

## Supported Devices

- KEBA KeContact P20
- KEBA KeContact P30 (c-series / x-series)

Each charging station must:
- Have a **dedicated IP address**
- Have the **Smart Home UDP interface enabled** (via DIP switch)

---

## Installation

### Option 1: HACS (recommended)

1. Open **HACS → Integrations**
2. Click the menu (top right) → **Custom repositories**
3. Add this repository URL
4. Select **Integration** as category
5. Install **KEBA Charging Station (Multi)**
6. Restart Home Assistant

### Option 2: Manual installation

1. Download this repository
2. Copy the folder:

```

custom_components/keba_multi

```

into:

```

/config/custom_components/

```

3. Restart Home Assistant

---

## Configuration

Configuration is done entirely via the Home Assistant UI.

1. Go to **Settings → Devices & Services**
2. Click **Add integration**
3. Search for **KEBA Charging Station (Multi)**
4. Enter the IP address (host) of the charging station
5. Repeat for each KEBA charger

Each charging station will appear as a separate device with its own entities.

---

## Entities

For each charging station, the integration provides:

### Sensors
- Charging power
- Session energy
- Total energy
- Maximum charging current
- Energy target

### Binary Sensors
- Charging state
- Plug state
- Failsafe mode
- Connectivity status

### Controls
- Start / stop charging
- Set charging current
- Authentication lock
- Display notifications

---

## Notes on Master / Slave Setups

- This integration communicates **directly with each charging station**
via UDP.
- Each station must respond independently on the network.
- Hardware load balancing (master/slave) is **not affected**.
- If a slave station does not expose the UDP interface, it cannot be added.

---

## Compatibility with OCPP

This integration **does not interfere** with OCPP connections.

It can be safely used alongside an external OCPP backend such as **SteVe**:
- OCPP is used for backend management
- UDP Smart Home is used for local monitoring and control

---

## Origin

This project is based on the official Home Assistant `keba` integration
and extends it to support **multiple charging stations**.

---

## License

See the `LICENSE` file for details.
