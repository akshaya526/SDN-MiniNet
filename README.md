# 🌐 Static Routing using SDN Controller in Mininet

> **Course:** Computer Networks — UE24CS252B
> **Name:** Akshaya M | **SRN:** PES2UG24CS050 | **Sec:** A

---

## 📌 Problem Statement

This project implements **static routing** using a **Software Defined Networking (SDN)** controller in a simulated network environment built with Mininet and the Ryu controller framework.

Key demonstrations:
- Controller–switch interaction via OpenFlow 1.3
- Flow rule (match–action) design and installation
- Controlled and predictable network behavior
- Static path enforcement without dynamic routing

> Unlike traditional networks, routing decisions are made **centrally by the controller** rather than by distributed routers.

---

## 🎯 Objectives

- Design a custom network topology using **Mininet**
- Implement an SDN controller using **Ryu**
- Manually define routing paths using **OpenFlow flow rules**
- Analyze network behavior under **normal and failure conditions**

---

## 🛠️ Tools & Technologies

| Tool | Description |
|------|-------------|
| **Mininet** | Network emulator for creating virtual topologies |
| **Ryu** | Python-based SDN controller framework |
| **Open vSwitch (OVS)** | Software-based OpenFlow-capable switch |
| **Ubuntu / Linux** | Host operating system |
| **OpenFlow 1.3** | Protocol for controller-switch communication |

---

## 🗂️ Project Structure

```
.
├── controller.py       # Ryu SDN controller with static routing logic
├── topo.py             # Custom Mininet topology definition
└── README.md           # Project documentation
```

---

## 🚀 Setup & Execution

### Prerequisites

```bash
# Install Mininet
sudo apt-get install mininet -y

# Install Ryu
pip install ryu --break-system-packages
```

### Step 1: Start the Ryu Controller

Open **Terminal 1**:

```bash
export PATH=$PATH:/home/seed/.local/bin
ryu-manager controller.py
```

**Expected output:**
```
loading app controller.py
loading app ryu.controller.ofp_handler
instantiating app controller.py of StaticRouting
instantiating app ryu.controller.ofp_handler of OFPHandler
```

### Step 2: Start Mininet with Custom Topology

Open **Terminal 2**:

```bash
sudo mn --custom topo.py --topo demo --controller=remote --switch ovsk,protocols=OpenFlow13
```

### Step 3: View the Network Topology

Inside the Mininet CLI:

```
mininet> net
```

---

## 🖧 Network Topology

```
         h1 (10.0.0.1)
          |
         s1
        /   \
       s2    s3
        \   /
         s4
        /  \
       h2   h3
 (10.0.0.2) (10.0.0.3)
```

### Components

| Component | IP Address | Description |
|-----------|-----------|-------------|
| `h1` | 10.0.0.1 | Source host |
| `h2` | 10.0.0.2 | Host on alternate path (s2) |
| `h3` | 10.0.0.3 | Destination host |
| `s1` | — | Root switch |
| `s2` | — | Alternate switch (unused path) |
| `s3` | — | Intermediate switch on static path |
| `s4` | — | Terminal switch connected to h3 |

### ✅ Static Path Enforced

```
h1 → s1 → s3 → s4 → h3
```

The path through `s2` is intentionally **not routed**.

---

## ⚙️ Implementation Details

### Controller Logic (`controller.py`)

The controller uses **OpenFlow 1.3** and handles two event types:

**1. `switch_features_handler` (CONFIG_DISPATCHER)**
- Installs a table-miss rule at priority 0
- All unmatched packets are sent to the controller

**2. `packet_in_handler` (MAIN_DISPATCHER)**
- Triggered when a packet arrives with no matching flow rule
- Reads `dpid` (switch ID) and `in_port`
- Installs a directional flow rule at priority 10
- Forwards the packet immediately

### Flow Rule Logic per Switch

| Switch | in_port | out_port | Direction |
|--------|---------|----------|-----------|
| s1 (dpid=1) | 1 (h1) | 3 (→s3) | Forward |
| s1 (dpid=1) | 3 (←s3) | 1 (→h1) | Reverse |
| s3 (dpid=3) | 1 (←s1) | 2 (→s4) | Forward |
| s3 (dpid=3) | 2 (←s4) | 1 (→s1) | Reverse |
| s4 (dpid=4) | 1 (←s3) | 2 (→h3) | Forward |
| s4 (dpid=4) | 2 (←h3) | 1 (→s3) | Reverse |
| s2 (dpid=2) | any | DROP | Unused |

---

## 📊 Results & Observations

### ✅ Scenario 1 — Successful Routing (h1 → h3)

```bash
mininet> h1 ping h3
```

**Screenshot — Successful ping h1 → h3:**

![h1 ping h3 success](screenshots/ping_h1_h3.png)

- ✔ 0% packet loss
- ✔ Static path `h1 → s1 → s3 → s4 → h3` followed
- ✔ RTT consistently under 1ms in steady state

---

### ❌ Scenario 2 — Unused Path (h1 → h2)

```bash
mininet> h1 ping h2
```

**Screenshot — Blocked ping h1 → h2:**

![h1 ping h2 blocked](screenshots/ping_h1_h2.png)

- ❌ 100% packet loss — "Destination Host Unreachable"
- ✔ Confirms `s2` path is intentionally not programmed by the controller

---

### 📋 Scenario 3 — Flow Table Verification

```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s3
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s4
```

**Screenshot — Flow table dump:**

![Flow table dump](screenshots/flow_table.png)

- ✔ Priority=10 rules installed for static path
- ✔ Priority=0 table-miss rule sends unmatched packets to controller
- ✔ `n_packets` counters confirm traffic is flowing through correct ports

---

### ❌ Scenario 4 — Failure Scenario (link down)

```bash
mininet> link s3 s4 down
mininet> h1 ping h3
```

**Screenshot — Ping failure after link down:**

![Failure scenario](screenshots/failure_scenario.png)

- ❌ 100% packet loss after link brought down
- ✔ No automatic rerouting — confirms **static routing behavior**
- ✔ Controller does not install alternate rules through s2

---

### 📋 Controller Log Output

**Screenshot — Ryu controller terminal:**

![Controller log](screenshots/controller_log.png)

Shows flow installations: `Flow: s1 1 -> 3`, `Flow: s3 1 -> 2`, `Flow: s4 1 -> 2`, etc.

---

## 🔍 Analysis

| Aspect | Observation |
|--------|-------------|
| **Path Predictability** | Static routing enforces deterministic, fixed paths every time |
| **Centralized Control** | All forwarding decisions made by the Ryu controller |
| **Fault Tolerance** | No automatic failover — static paths fail hard on link failure |
| **Flow Validation** | `dump-flows` confirms correct match-action rule installation |
| **Alternate Path** | s2 path never receives flow rules — packets to h2 are dropped |

---

## 📝 Conclusion

This project successfully demonstrates:

- ✅ SDN-based static routing in a simulated Mininet environment
- ✅ Controller-driven flow rule installation using Ryu + OpenFlow 1.3
- ✅ Fixed path enforcement via match-action rules on specific switch ports
- ✅ Predictable failure behavior confirming no dynamic rerouting
- ✅ Two-scenario validation: allowed path (h1→h3) and blocked path (h1→h2)

The implementation highlights both the **advantages** (predictability, centralized control) and **limitations** (no fault tolerance) of static routing in SDN.

---

## 📚 References

- [Mininet Documentation](http://mininet.org/walkthrough/)
- [Ryu Controller Documentation](https://ryu.readthedocs.io/)
- [OpenFlow 1.3 Specification](https://opennetworking.org/sdn-resources/openflow/)
- Course Notes — Computer Networks UE24CS252B, PES University
