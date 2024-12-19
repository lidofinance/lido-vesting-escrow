# @version 0.3.7

"""
@notice Mock Aragon voting for testing
"""

from vyper.interfaces import ERC20


event CastVote:
    voteId: indexed(uint256)
    voter: indexed(address)
    supports: bool
    stake: uint256

event AssignDelegate:
    voter: indexed(address)
    assignedDelegate: indexed(address)

event UnassignDelegate:
    voter: indexed(address)
    unassignedDelegate: indexed(address)

token: public(ERC20)
delegates: HashMap[address, address]


@external
def __init__(token: address):
    self.token = ERC20(token)


@external
def vote(
    _voteId: uint256, _supports: bool, _executesIfDecided_deprecated: bool
):
    sender_balance: uint256 = self.token.balanceOf(msg.sender)
    assert sender_balance > 0, "insufficient balance"
    log CastVote(_voteId, msg.sender, _supports, sender_balance)

@external
def assignDelegate(delegate: address):
    self.delegates[msg.sender] = delegate
    log AssignDelegate(msg.sender, delegate)

@external
def unassignDelegate():
    delegate: address = self.delegates[msg.sender]
    log UnassignDelegate(msg.sender, delegate)
