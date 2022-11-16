# @version 0.3.7

"""
@title Voting Adapter
@author Lido Finance
@license MIT
@notice Used to allow voting with tokens under vesting
"""


interface IDelegation:
    def setDelegate(
        _id: bytes32,
        _delegate: address,
    ): nonpayable


interface IVoting:
    def vote(
        _voteId: uint256,
        _supports: bool,
        _executesIfDecided_deprecated: bool,
    ): nonpayable


ZERO_BYTES32: constant(
    bytes32
) = 0x0000000000000000000000000000000000000000000000000000000000000000


@external
def vote(voting_addr: address, voteId: uint256, supports: bool):
    """
    @notice Cast vote. || Only for delegate calls
    @param voting_addr Address of the voting contrat
    @param voteId Id of the vote
    @param supports Support flag true - yea, false - nay
    """
    IVoting(voting_addr).vote(
        voteId, supports, False
    )  # dev: third arg is deprecated


@external
def set_delegate(delegate_contract_addr: address, delegate: address):
    """
    @notice Delegate Snapshot voting power of all available tokens
    """
    IDelegation(delegate_contract_addr).setDelegate(
        ZERO_BYTES32, delegate
    )  # dev: null id allows voting at any snapshot space
