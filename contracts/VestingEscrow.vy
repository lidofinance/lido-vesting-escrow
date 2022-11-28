# @version 0.3.7

"""
@title Vesting Escrow
@author Curve Finance, Yearn Finance, Lido Finance
@license MIT
@notice Vests ERC20 tokens for a single address
@dev Intended to be deployed many times via `VotingEscrowFactory`
"""

from vyper.interfaces import ERC20


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


event OwnerChanged:
    owner: address


event ManagerChanged:
    manager: address


event ERC20Recovered:
    token: address
    amount: uint256



LIDO_VOTING_CONTRACT_ADDR: immutable(address)
SNAPSHOT_DELEGATE_CONTRACT_ADDR: immutable(address)

recipient: public(address)
token: public(ERC20)
start_time: public(uint256)
end_time: public(uint256)
cliff_length: public(uint256)
voting_adapter_addr: public(address)
total_locked: public(uint256)

total_claimed: public(uint256)
disabled_at: public(uint256)
initialized: public(bool)

owner: public(address)
manager: public(address)


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
    voting_adapter_addr: address,
) -> bool:
    """
    @notice Initialize the contract.
    @dev This function is separate from `__init__` because of the factory pattern
         used in `VestingEscrowFactory.deploy_vesting_contract`. It may be called
         once per deployment.
    @param token Address of the ERC20 token being distributed
    @param amount Address of the ERC20 token to be controleed by escrow
    @param recipient Address to vest tokens for
    @param owner Address of the vesting owner
    @param manager Address of the vesting manager
    @param start_time Epoch time at which token distribution starts
    @param end_time Time until everything should be vested
    @param cliff_length Duration after which the first portion vests
    @param voting_adapter_addr VotingAdapter address
    """
    assert not self.initialized, "can only initialize once"
    self.initialized = True

    self.owner = owner
    self.manager = manager
    self.token = ERC20(token)
    self.start_time = start_time
    self.end_time = end_time
    self.cliff_length = cliff_length

    assert self.token.transferFrom(msg.sender, self, amount), "could not fund escrow"
    
    self.total_locked = amount
    self.recipient = recipient
    self.disabled_at = end_time  # Set to maximum time
    self.voting_adapter_addr = voting_adapter_addr
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
def change_owner(owner: address):
    """
    @notice Change contract owner.
    @param owner Address of the new owner. Must be non-zero and
           not same as the current owner.
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
def recover_erc20(token: address):
    """
    @notice Recover ERC20 tokens to recipient
    @param token Address of the ERC20 token to be recovered
    """
    self._check_sender_is_recipient()
    recoverable: uint256 = ERC20(token).balanceOf(self)
    if token == self.token.address:
        recoverable -= self._locked() + self._unclaimed()
    assert ERC20(token).transfer(self.recipient, recoverable)
    log ERC20Recovered(token, recoverable)


@external
def vote(voteId: uint256, supports: bool):
    """
    @notice Participate Aragon vote using all available tokens on the contract's balance
    @param voteId Id of the vote
    @param supports Support flag true - yea, false - nay
    """
    self._check_sender_is_recipient()
    raw_call(
        self.voting_adapter_addr,
        _abi_encode(
            LIDO_VOTING_CONTRACT_ADDR,
            voteId,
            supports,
            method_id=method_id("vote(address,uint256,bool)"),
        ),
        is_delegate_call=True,
    )


@external
def set_delegate(delegate: address = msg.sender):
    """
    @notice Delegate Snapshot voting power of all available tokens on the contract's balance
    """
    self._check_sender_is_recipient()
    raw_call(
        self.voting_adapter_addr,
        _abi_encode(
            SNAPSHOT_DELEGATE_CONTRACT_ADDR,
            delegate,
            method_id=method_id("set_delegate(address,address)"),
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
