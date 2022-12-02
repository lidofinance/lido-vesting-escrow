# @version 0.3.7

"""
@title Fully Revokable Vesting Escrow
@author Curve Finance, Yearn Finance, Lido Finance
@license MIT
@notice Vests ERC20 tokens for a single address
@dev Intended to be deployed many times via `VotingEscrowFactory`
"""

from vyper.interfaces import ERC20


interface IVestingEscrowFactory:
    def voting_adapter() -> address: nonpayable


event Fund:
    recipient: indexed(address)
    amount: uint256


event Claim:
    recipient: indexed(address)
    beneficiary: address
    claimed: uint256


event RevokeUnvested:
    recipient: indexed(address)
    revoked: uint256


event RevokeAll:
    recipient: indexed(address)
    revoked: uint256


event OwnerChanged:
    owner: address


event ManagerChanged:
    manager: address


event ERC20Recovered:
    token: address
    amount: uint256


event ETHRecovered:
    amount: uint256


recipient: public(address)
token: public(ERC20)
start_time: public(uint256)
end_time: public(uint256)
cliff_length: public(uint256)
factory: public(address)
total_locked: public(uint256)

total_claimed: public(uint256)
disabled_at: public(uint256)
initialized: public(bool)
is_fully_revoked: public(bool)

owner: public(address)
manager: public(address)


@external
def __init__():
    """
    @notice Initialize source contract implementation.
    """
    # ensure that the original contract cannot be initialized
    self.initialized = True


@external
@nonreentrant("lock")
def initialize(
    token: address,
    amount: uint256,
    recipient: address,
    owner: address,
    manager: address,
    start_time: uint256,
    end_time: uint256,
    cliff_length: uint256,
    factory: address,
) -> bool:
    """
    @notice Initialize the contract.
    @dev This function is separate from `__init__` because of the factory pattern
         used in `VestingEscrowFactory.deploy_vesting_contract`. It may be called
         once per deployment.
    @param token Address of the ERC20 token being distributed
    @param amount Amount of the ERC20 token to be controleed by escrow
    @param recipient Address to vest tokens for
    @param owner Address of the vesting owner
    @param manager Address of the vesting manager
    @param start_time Epoch time at which token distribution starts
    @param end_time Time until everything should be vested
    @param cliff_length Duration after which the first portion vests
    @param factory Address of the parent factory
    """
    assert not self.initialized, "can only initialize once"
    self.initialized = True

    self.owner = owner
    self.manager = manager
    self.token = ERC20(token)
    self.start_time = start_time
    self.end_time = end_time
    self.cliff_length = cliff_length

    assert self.token.transferFrom(
        msg.sender, self, amount
    ), "could not fund escrow"

    self.total_locked = amount
    self.recipient = recipient
    self.disabled_at = end_time  # Set to maximum time
    self.factory = factory
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
    if self.is_fully_revoked:
        return 0
    return self._total_vested_at(time) - self.total_claimed


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
    if time >= self.disabled_at:
        return 0
    return self.total_locked - self._total_vested_at(time)


@external
@view
def locked() -> uint256:
    """
    @notice Get the number of locked tokens for recipient
    """
    return self._locked(min(block.timestamp, self.disabled_at))


@external
def claim(
    beneficiary: address = msg.sender, amount: uint256 = max_value(uint256)
):
    """
    @notice Claim tokens which have vested
    @param beneficiary Address to transfer claimed tokens to
    @param amount Amount of tokens to claim
    """
    self._check_sender_is_recipient()

    claim_period_end: uint256 = min(block.timestamp, self.disabled_at)
    claimable: uint256 = min(self._unclaimed(claim_period_end), amount)
    self.total_claimed += claimable

    assert self.token.transfer(beneficiary, claimable)
    log Claim(self.recipient, beneficiary, claimable)


@external
def revoke_unvested():
    """
    @notice Disable further flow of tokens and revoke the unvested part to owner
    """
    self._check_sender_is_owner_or_manager()
    # NOTE: Revoking more than once is futile

    revokable: uint256 = self._locked()
    self.disabled_at = block.timestamp

    assert self.token.transfer(self.owner, revokable)
    log RevokeUnvested(self.recipient, revokable)


@external
def revoke_all():
    """
    @notice Disable further flow of tokens and revoke all tokens to owner
    """
    self._check_sender_is_owner()
    # NOTE: Revoking more than once is futile

    self.is_fully_revoked = True
    self.disabled_at = block.timestamp
    # NOTE: do not revoke extra tokens
    revokable: uint256 = self.total_locked - self.total_claimed

    assert self.token.transfer(self.owner, revokable)
    log RevokeAll(self.recipient, revokable)


@external
def change_owner(owner: address):
    """
    @notice Change contract owner.
    @param owner Address of the new owner. Must be non-zero.
    """
    self._check_sender_is_owner()
    assert owner != empty(address), "zero owner address"

    self.owner = owner
    log OwnerChanged(owner)


@external
def change_manager(manager: address):
    """
    @notice Set contract manager.
            Can update manager if it is already set.
            Can be called only by the owner.
    @param manager Address of the new manager
    """
    self._check_sender_is_owner()

    self.manager = manager
    log ManagerChanged(manager)


@external
def revoke_ownership():
    """
    @notice Revoke contract owner and manager
    """
    self._check_sender_is_owner()

    self.manager = empty(address)
    self.owner = empty(address)

    log ManagerChanged(empty(address))
    log OwnerChanged(empty(address))


@external
def recover_erc20(token: address, amount: uint256):
    """
    @notice Recover ERC20 tokens to recipient
    @param token Address of the ERC20 token to be recovered
    """
    recoverable: uint256 = amount
    if token == self.token.address:
        available: uint256 = ERC20(token).balanceOf(self) - (
            self._locked() + self._unclaimed()
        )
        recoverable = min(recoverable, available)
    assert ERC20(token).transfer(self.recipient, recoverable)
    log ERC20Recovered(token, recoverable)


@external
def recover_ether():
    """
    @notice Recover Ether to recipient
    """
    amount: uint256 = self.balance
    send(self.recipient, amount)
    log ETHRecovered(amount)


@external
def aragon_vote(voteId: uint256, supports: bool):
    """
    @notice Participate Aragon vote using all available tokens on the contract's balance
    @param voteId Id of the vote
    @param supports Support flag true - yea, false - nay
    """
    self._check_sender_is_recipient()
    raw_call(
        IVestingEscrowFactory(self.factory).voting_adapter(),
        _abi_encode(
            voteId,
            supports,
            method_id=method_id("aragon_vote(uint256,bool)"),
        ),
        is_delegate_call=True,
    )


@external
def snapshot_set_delegate(delegate: address = msg.sender):
    """
    @notice Delegate Snapshot voting power of all available tokens on the contract's balance
    @param delegate Address of the delegate
    """
    self._check_sender_is_recipient()
    raw_call(
        IVestingEscrowFactory(self.factory).voting_adapter(),
        _abi_encode(
            delegate,
            method_id=method_id("snapshot_set_delegate(address)"),
        ),
        is_delegate_call=True,
    )


@external
def delegate(delegate: address = msg.sender):
    """
    @notice Delegate voting power of all available tokens on the contract's balance
    @param delegate Address of the delegate
    """
    self._check_sender_is_recipient()
    raw_call(
        IVestingEscrowFactory(self.factory).voting_adapter(),
        _abi_encode(
            delegate,
            method_id=method_id("delegate(address)"),
        ),
        is_delegate_call=True,
    )


@internal
def _check_sender_is_owner_or_manager():
    assert (
        msg.sender == self.owner
        or (msg.sender == self.manager and msg.sender != empty(address))
    ), "msg.sender not owner or manager"


@internal
def _check_sender_is_owner():
    assert msg.sender == self.owner, "msg.sender not owner"


@internal
def _check_sender_is_recipient():
    assert msg.sender == self.recipient, "msg.sender not recipient"
