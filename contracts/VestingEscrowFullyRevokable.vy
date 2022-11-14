# @version 0.3.7
"""
@title Fully revokable Vesting Escrow
@author Curve Finance, Yearn Finance, Lido Finance
@license MIT
@notice Vests ERC20 tokens for a single address
@dev Intended to be deployed many times via `VotingEscrowFactory`
"""

from vyper.interfaces import ERC20

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

event Fund:
    recipient: indexed(address)
    amount: uint256

event Claim:
    recipient: indexed(address)
    beneficiary: address
    claimed: uint256

event RevokeUnvested:
    recipient: indexed(address)
    beneficiary: address
    revoked: uint256

event RevokeAll:
    recipient: indexed(address)
    beneficiary: address
    revoked: uint256

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address

event ERC20Recovered:
    recipient: indexed(address)
    token: address
    amount: uint256

ZERO_BYTES32: constant(bytes32) = 0x0000000000000000000000000000000000000000000000000000000000000000

LIDO_VOTING_CONTRACT_ADDR: immutable(address)
SNAPSHOT_DELEGATE_CONTRACT_ADDR: immutable(address)

recipient: public(address)
token: public(ERC20)
start_time: public(uint256)
end_time: public(uint256)
cliff_length: public(uint256)
total_locked: public(uint256)
total_claimed: public(uint256)
disabled_at: public(uint256)
is_fully_revoked: public(bool)
initialized: public(bool)

admin: public(address)
future_admin: public(address)

@external
def __init__(voting_addr: address, snapshot_addr: address):
    """
    @notice Initialize source contract implementation.
    @param voting_addr Address of the Lido Voting contract
    @param snapshot_addr Address of the Shapshot Delegate contract
    """
    # ensure that the original contract cannot be initialized
    self.initialized = True
    LIDO_VOTING_CONTRACT_ADDR = voting_addr
    SNAPSHOT_DELEGATE_CONTRACT_ADDR = snapshot_addr


@external
@nonreentrant('lock')
def initialize(
    admin: address,
    token: address,
    recipient: address,
    amount: uint256,
    start_time: uint256,
    end_time: uint256,
    cliff_length: uint256,
) -> bool:
    """
    @notice Initialize the contract.
    @dev This function is separate from `__init__` because of the factory pattern
         used in `VestingEscrowFactory.deploy_vesting_contract`. It may be called
         once per deployment.
    @param admin Admin address
    @param token Address of the ERC20 token being distributed
    @param recipient Address to vest tokens for
    @param amount Amount of tokens being vested for `recipient`
    @param start_time Epoch time at which token distribution starts
    @param end_time Time until everything should be vested
    @param cliff_length Duration after which the first portion vests
    """
    assert not self.initialized, "can only initialize once"
    self.initialized = True

    self.token = ERC20(token)
    self.admin = admin
    self.start_time = start_time
    self.end_time = end_time
    self.cliff_length = cliff_length
    self.is_fully_revoked = False

    assert self.token.transferFrom(msg.sender, self, amount), "could not fund escrow"

    self.recipient = recipient
    self.disabled_at = end_time  # Set to maximum time
    self.total_locked = amount
    log Fund(recipient, amount)

    return True


@internal
@view
def _total_vested_at(time: uint256 = block.timestamp) -> uint256:
    start: uint256 = self.start_time
    end: uint256 = self.end_time
    locked: uint256 = self.total_locked
    if time < start + self.cliff_length:
        return 0
    return min(locked * (time - start) / (end - start), locked)


@internal
@view
def _unclaimed(time: uint256 = block.timestamp) -> uint256:
    if not self.is_fully_revoked:
        return self._total_vested_at(time) - self.total_claimed
    return 0


@external
@view
def unclaimed() -> uint256:
    """
    @notice Get the number of unclaimed, vested tokens for recipient
    """
    # NOTE: if `revoke_unvested` is activated, limit by the activation timestamp
    return self._unclaimed(min(block.timestamp, self.disabled_at))


@internal
@view
def _locked(time: uint256 = block.timestamp) -> uint256:
    return min(self.total_locked - self._total_vested_at(time), self.token.balanceOf(self))


@external
@view
def locked() -> uint256:
    """
    @notice Get the number of locked tokens for recipient
    """
    # NOTE: if `rug_pull` is activated, limit by the activation timestamp
    return self._locked(min(block.timestamp, self.disabled_at))


@external
def claim(beneficiary: address = msg.sender, amount: uint256 = MAX_UINT256):
    """
    @notice Claim tokens which have vested
    @param beneficiary Address to transfer claimed tokens to
    @param amount Amount of tokens to claim
    """
    assert msg.sender == self.recipient, "not recipient"

    claim_period_end: uint256 = min(block.timestamp, self.disabled_at)
    claimable: uint256 = min(self._unclaimed(claim_period_end), amount)
    self.total_claimed += claimable

    assert self.token.transfer(beneficiary, claimable)
    log Claim(self.recipient, beneficiary, claimable)


@external
def revoke_unvested(beneficiary: address = msg.sender):
    """
    @notice Disable further flow of tokens and revoke the unvested part to the beneficiary
    @param beneficiary Address to revoke tokens to
    """
    assert msg.sender == self.admin, "admin only"
    # NOTE: Revoking more than once is futile

    self.disabled_at = block.timestamp
    revokable: uint256 = self._locked()

    assert self.token.transfer(beneficiary, revokable)
    log RevokeUnvested(self.recipient, beneficiary, revokable)


@external
def revoke_all(beneficiary: address = msg.sender):
    """
    @notice Disable further flow of tokens and revoke all tokens to the beneficiary
    @param beneficiary Address to revoke tokens to
    """
    assert msg.sender == self.admin, "admin only"
    # NOTE: Revoking more than once is futile

    self.is_fully_revoked = True
    self.disabled_at = block.timestamp
    revokable: uint256 = self.token.balanceOf(self)

    assert self.token.transfer(beneficiary, revokable)
    log RevokeAll(self.recipient, beneficiary, revokable)


@external
def commit_transfer_ownership(addr: address):
    """
    @notice Transfer ownership of the contract to `addr`
    @param addr Address to have ownership transferred to
    """
    assert msg.sender == self.admin, "admin only"
    self.future_admin = addr
    log CommitOwnership(addr)


@external
def apply_transfer_ownership():
    """
    @notice Apply pending ownership transfer
    """
    assert msg.sender == self.future_admin, "future admin only"
    self.admin = msg.sender
    self.future_admin = ZERO_ADDRESS
    log ApplyOwnership(msg.sender)


@external
def renounce_ownership():
    """
    @notice Renounce admin control of the escrow
    """
    assert msg.sender == self.admin, "admin only"
    self.future_admin = ZERO_ADDRESS
    self.admin = ZERO_ADDRESS
    log ApplyOwnership(ZERO_ADDRESS)


@external
def recover_erc20(token: address):
    """
    @notice Recover non-escrow tokens from the contract or collect leftovers of the escrow tokens once vesting is done to the recipient address
    @param token Address of the ERC20 token to be recovered
    """
    assert msg.sender == self.recipient, "recipient only"
    assert (token != self.token.address or block.timestamp > self.disabled_at)
    recoverable: uint256 = ERC20(token).balanceOf(self)
    assert ERC20(token).transfer(self.recipient, recoverable)
    log ERC20Recovered(self.recipient, token, recoverable)


@external
def vote(voteId: uint256, supports: bool):
    """
    @notice Participate Aragon vote using all available tokens on the contract's balance
    @param voteId Id of the vote
    @param supports Support flag true - yea, false - nay
    """
    assert msg.sender == self.recipient, "recipient only"
    IVoting(LIDO_VOTING_CONTRACT_ADDR).vote(voteId, supports, False) # dev: third arg is depricated


@external
def set_delegate():
    """
    @notice Delegate Snapshot voting power of all available tokens on the contract's balance
    """
    assert msg.sender == self.recipient, "recipient only"
    IDelegation(SNAPSHOT_DELEGATE_CONTRACT_ADDR).setDelegate(ZERO_BYTES32, self.recipient) # dev: null id allows voting at any snapshot space