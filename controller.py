from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3


class StaticRouting(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # ---------------- FLOW INSTALL ----------------
    def add_flow(self, datapath, priority, match, actions):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst
        )
        datapath.send_msg(mod)

    # ---------------- TABLE MISS RULE ----------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Send unknown packets to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER,
            ofproto.OFPCML_NO_BUFFER
        )]

        self.add_flow(datapath, 0, match, actions)

    # ---------------- STATIC ROUTING ----------------
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        in_port = msg.match['in_port']

        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        print(f"Switch {dpid}, in_port {in_port}")

        # ----------- PATH: h1 → s1 → s3 → s4 → h3 -----------

        # s1
        if dpid == 1:
            if in_port == 1:      # h1
                out_port = 3      # → s3
            elif in_port == 3:    # from s3
                out_port = 1      # → h1
            else:
                return

        # s3
        elif dpid == 3:
            if in_port == 1:      # from s1
                out_port = 2      # → s4
            elif in_port == 2:    # from s4
                out_port = 1      # → s1
            else:
                return

        # s4
        elif dpid == 4:
            if in_port == 1:      # from s3
                out_port = 2      # → h3
            elif in_port == 2:    # from h3
                out_port = 1      # → s3
            else:
                return

        # s2 (unused path)
        elif dpid == 2:
            return

        else:
            return

        # ----------- INSTALL FLOW -----------

        actions = [parser.OFPActionOutput(out_port)]
        match = parser.OFPMatch(in_port=in_port)

        print(f"Flow: s{dpid} {in_port} -> {out_port}")

        self.add_flow(datapath, 10, match, actions)

        # ----------- FORWARD PACKET -----------

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=ofproto.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )
        datapath.send_msg(out)
