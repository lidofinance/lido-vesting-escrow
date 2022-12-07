# @version 0.3.7

"""
@title Voting Adapter
@author Curve Finance, Yearn Finance, Lido Finance
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

VOTING_CONTRACT_ADDR: immutable(address)
SNAPSHOT_DELEGATE_CONTRACT_ADDR: immutable(address)
DELEGATION_CONTRACT_ADDR: immutable(address)


@external
def __init__(
    voting_addr: address,
    snapshot_delegate_addr: address,
    delegation_addr: address,
):
    """
    @notice Initialize source contract implementation.
    @param voting_addr Address of the Voting contract
    @param snapshot_delegate_addr Address of the Shapshot Delegate contract
    @param delegation_addr Address of the voting power delegation contract
    """
    VOTING_CONTRACT_ADDR = voting_addr
    SNAPSHOT_DELEGATE_CONTRACT_ADDR = snapshot_delegate_addr
    DELEGATION_CONTRACT_ADDR = delegation_addr


@external
def aragon_vote(voteId: uint256, supports: bool):
    """
    @notice Cast vote on Aragon voting
    @param voteId Id of the vote
    @param supports Support flag true - yea, false - nay
    """
    IVoting(VOTING_CONTRACT_ADDR).vote(
        voteId, supports, False
    )  # dev: third arg is deprecated


@external
def snapshot_set_delegate(delegate: address):
    """
    @notice Delegate Snapshot voting power of all available tokens
    @param delegate Address of the delegate
    """
    IDelegation(SNAPSHOT_DELEGATE_CONTRACT_ADDR).setDelegate(
        ZERO_BYTES32, delegate
    )  # dev: null id allows voting at any snapshot space


@external
def delegate(delegate: address):
    """
    @notice Delegate voting power of all available tokens
    @param delegate Address of the delegate
    """
    assert False, "not implemented"

@external
@view
def voting_contract_addr() -> address:
    return VOTING_CONTRACT_ADDR

@external
@view
def snapshot_delegate_contract_addr() -> address:
    return SNAPSHOT_DELEGATE_CONTRACT_ADDR

@external
@view
def delegation_contract_addr() -> address:
    return DELEGATION_CONTRACT_ADDR
