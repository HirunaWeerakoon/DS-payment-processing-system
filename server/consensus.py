# server/consensus.py
from pysyncobj import SyncObj, replicated
from ledger import record_payment, get_all_payments

class PaymentNode(SyncObj):
    """
    A Raft-replicated payment node.
    Any method decorated with @replicated runs on ALL nodes
    in the cluster in the exact same order — that's the guarantee.
    """

    def __init__(self, self_addr, partner_addrs):
        # self_addr   : this node's Raft address, e.g. "127.0.0.1:4001"
        # partner_addrs : list of OTHER nodes' Raft addresses
        super().__init__(self_addr, partner_addrs)

    @replicated
    def add_payment(self, payment):
        """
        Write a payment via Raft consensus.
        This method is automatically replicated to every node in the cluster.
        pysyncobj guarantees it runs in the same order everywhere.
        """
        record_payment(payment)

    def get_payments(self):
        """
        Read all payments from local SQLite.
        Reads don't need Raft consensus — just query locally.
        """
        return get_all_payments()