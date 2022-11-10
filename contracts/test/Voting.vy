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

token: public(ERC20)

@external
def __init__(token: address):
    self.token = ERC20(token)

@external
def vote(_voteId: uint256, _supports: bool, _executesIfDecided_deprecated: bool):
    log CastVote(_voteId, msg.sender, _supports, self.token.balanceOf(msg.sender))
