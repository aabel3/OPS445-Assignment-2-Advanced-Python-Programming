#!/usr/bin/env python3

# OPS435 Assignment 2
# load_balancer_monitor_aabel3.py
# Author: Avraham Abel

import subprocess

# Node class represents a single server (master or slave)
class Node:
    def __init__(self, ip):
        self.ip = ip

    # Validates whether the IP address is syntactically and logically valid
    def canExist(self):
        octets = self.ip.split('.')
        if len(octets) != 4:
            return False
        try:
            octets = [int(octet) for octet in octets]
        except ValueError:
            return False
        # First and last octets must not be zero
        if octets[0] == 0 or octets[3] == 0:
            return False
        # Each octet must be in the range 0–254
        for octet in octets:
            if octet < 0 or octet >= 255:
                return False
        return True

    # Checks if the node is reachable using a single ping attempt
    def isRunning(self):
        cmd = f"ping -W 2 -c 1 {self.ip}"
        status, _ = subprocess.getstatusoutput(cmd)
        return status == 0

# LoadBalancerMonitor class tracks master and slave node status
class LoadBalancerMonitor:
    def __init__(self, networkAddress, bitmask, master):
        self.networkAddress = networkAddress
        self.bitmask = bitmask
        self.master = master
        self.slaves = []

    # Adds a slave node if its IP is valid
    def addSlave(self, node):
        if node.canExist():
            self.slaves.append(node)
        else:
            print(f"Error: Invalid IP address {node.ip}")

    # Removes a slave node by matching its IP address
    def removeSlave(self, slave):
        self.slaves = [s for s in self.slaves if s.ip != slave.ip]

    # Prints the status of the master and all slave nodes
    def getStatus(self):
        print("Checking", end='', flush=True)

        # Check master node status
        master_status = "OFFLINE"
        if self.master.canExist():
            print(".", end='', flush=True)
            if self.master.isRunning():
                master_status = "ONLINE"
        else:
            print(".", end='', flush=True)

        # Check each slave node status
        online_count = 0
        offline_count = 0
        for slave in self.slaves:
            print(".", end='', flush=True)
            if slave.isRunning():
                online_count += 1
            else:
                offline_count += 1

        # Final status report
        print("\n\nLoad Balancer Status")
        print("====================")
        print(f"Master: {master_status}")
        print(f"Slaves: {online_count} ONLINE, {offline_count} OFFLINE")

# Main test block — sets up master and slaves, then checks status
if __name__ == "__main__":
    master = Node("1.1.1.1")  # Public DNS IP, usually reachable
    monitor = LoadBalancerMonitor("1.1.1.0", 24, master)

    # Add slave nodes; 3 loopback IPs (ONLINE), 1 unreachable (OFFLINE)
    monitor.addSlave(Node("127.0.0.1"))
    monitor.addSlave(Node("127.0.0.2"))
    monitor.addSlave(Node("127.0.0.3"))
    monitor.addSlave(Node("10.4.45.100"))

    # Print full load balancer status
    monitor.getStatus()
