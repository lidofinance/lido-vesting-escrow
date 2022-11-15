# @version 0.3.7

"""
@title Vesting Escrow Factory
@author Lido Finance
@license MIT
@notice Stores and distributes ERC20 tokens by deploying `VestingEscrow` or `VestingEscrowFullyRevokable` contracts
"""

from vyper.interfaces import ERC20


interface IVestingEscrow:
    def initialize(
        token: address,
        recipient: address,
        start_time: uint256,
        end_time: uint256,
        cliff_length: uint256,
        voting_adapter_addr: address,
    ) -> bool: nonpayable

    def activate(
        amount: uint256,
        owner: address,
        manager: address,
    ) -> bool: nonpayable

    def get_token() -> address: view


struct EscrowAmount:
    escrow: address
    amount: uint256


event VestingEscrowCreated:
    creator: indexed(address)
    token: indexed(address)
    recipient: indexed(address)
    escrow: address
    escrow_type: uint256  # 0 - simple, 1 - fully revokable
    vesting_start: uint256
    vesting_duration: uint256
    cliff_length: uint256
    voting_adapter: address

event VestingEscrowActivated:
    escrow: indexed(address)
    amount: uint256
    owner: indexed(address)
    manager: indexed(address)


target_simple: public(address)
target_fully_revokable: public(address)
default_voting_adapter: public(address)


@external
def __init__(target_simple: address, target_fully_revokable: address, default_voting_adapter: address):
    """
    @notice Contract constructor
    @dev Prior to deployment you must deploy one copy of `VestingEscrowSimple` and `VestingEscrowFullyRevokable` which
         are used as a library for vesting contracts deployed by this factory
    @param target_simple `VestingEscrow` contract address
    @param target_fully_revokable `VestingEscrowFullyRevokable` contract address
    """
    assert target_simple != empty(address), "target_simple should not be ZERO_ADDRESS"
    assert target_fully_revokable != empty(address), "target_fully_revokable should not be ZERO_ADDRESS"
    self.target_simple = target_simple
    self.target_fully_revokable = target_fully_revokable
    self.default_voting_adapter = default_voting_adapter


@external
def deploy_vesting_contract(
    token: address,
    recipient: address,
    vesting_duration: uint256,
    vesting_start: uint256 = block.timestamp,
    cliff_length: uint256 = 0,
    escrow_type: uint256 = 0,  # use simple escrow by default
) -> address:
    """
    @notice Deploy a new vesting contract without funding. Funding should be done separately
    @param token Address of the ERC20 token being distributed
    @param recipient Address to vest tokens for
    @param vesting_duration Time period over which tokens are released
    @param vesting_start Epoch time when tokens begin to vest
    @param cliff_length Duration after which the first portion vests
    @param escrow_type Escrow type to deploy 0 - `VestingEscrow`, 1 - `VestingEscrowFullyRevokable`
    """
    assert cliff_length <= vesting_duration, "incorrect vesting cliff"
    assert escrow_type in [0, 1], "incorrect escrow type"
    escrow: address = empty(address)
    if escrow_type == 1:  # dev: select target based on escrow type
        escrow = create_minimal_proxy_to(self.target_fully_revokable)
    else:
        escrow = create_minimal_proxy_to(self.target_simple)
    IVestingEscrow(escrow).initialize(
        token,
        recipient,
        vesting_start,
        vesting_start + vesting_duration,
        cliff_length,
        self.default_voting_adapter,
    )
    log VestingEscrowCreated(
        msg.sender,
        token,
        recipient,
        escrow,
        escrow_type,
        vesting_start,
        vesting_duration,
        cliff_length,
        self.default_voting_adapter,
    )
    return escrow


@internal
def _activate_vesting_contract(
    escrow: address,
    amount: uint256,
    manager: address = empty(address),
):
    token: address = IVestingEscrow(escrow).get_token()
    assert ERC20(token).transferFrom(msg.sender, self, amount), "funding failed"
    assert ERC20(token).approve(escrow, amount), "approve failed"
    IVestingEscrow(escrow).activate(
        amount,
        msg.sender,
        manager,
    )
    log VestingEscrowActivated(
        escrow,
        amount,
        msg.sender,
        manager,
    )


@external
def activate_vesting_contract(
    escrow: address,
    amount: uint256,
    manager: address = empty(address),
):
    """
    @notice Fund and activate deployed vesting escrow
    @param escrow Address of the deployed vesting escrow
    @param amount Amount of tokens to fund escrow
    @param manager Address of the initial escrow manager
    """
    self._activate_vesting_contract(escrow, amount, manager)


@external
def activate_vesting_contracts(
    escrows_ammounts: DynArray[EscrowAmount, 100],
    manager: address = empty(address),
):
    """
    @notice Fund and activate multiple deployed vesting escrows
    @param escrows_ammounts Array of EscrowAmount
    @param manager Address of the initial escrow manager
    """
    for escrow_ammount in escrows_ammounts:
        self._activate_vesting_contract(escrow_ammount.escrow, escrow_ammount.amount, manager)
    