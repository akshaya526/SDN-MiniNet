from mininet.topo import Topo

class DemoTopo(Topo):
    def build(self):
        # Hosts
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')

        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Links
        self.addLink(h1, s1)

        self.addLink(s1, s2)
        self.addLink(s1, s3)

        self.addLink(s2, h2)
        self.addLink(s3, s4)
        self.addLink(s4, h3)

topos = {'demo': DemoTopo}
