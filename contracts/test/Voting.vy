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

event DelegateSet:
    voter: indexed(address)
    previousDelegate: indexed(address)
    newDelegate: indexed(address)

token: public(ERC20)


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
    log DelegateSet(msg.sender, ZERO_ADDRESS, delegate)

@external
def removeDelegate():
    log DelegateSet(msg.sender, ZERO_ADDRESS, ZERO_ADDRESS)
