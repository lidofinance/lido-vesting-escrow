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

event SetDelegate:
    voter: indexed(address)
    delegate: indexed(address)

event ResetDelegate:
    voter: indexed(address)
    delegate: indexed(address)

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
def setDelegate(delegate: address):
    self.delegates[msg.sender] = delegate
    log SetDelegate(msg.sender, delegate)

@external
def resetDelegate():
    delegate: address = self.delegates[msg.sender]
    log ResetDelegate(msg.sender, delegate)
