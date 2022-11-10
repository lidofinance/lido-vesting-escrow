# @version 0.3.7

"""
@notice Mock Snapshot delegation for testing
"""


event SetDelegate:
    delegator: indexed(address)
    id: indexed(bytes32)
    delegate: indexed(address)

@external
def setDelegate(id: bytes32, delegate: address):
    log SetDelegate(msg.sender, id, delegate)

