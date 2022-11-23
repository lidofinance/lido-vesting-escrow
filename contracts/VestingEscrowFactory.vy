# @version 0.3.7

"""
@title Vesting Escrow Factory
@author Curve Finance, Yearn Finance, Lido Finance
@license MIT
@notice Stores and distributes ERC20 tokens by deploying `VestingEscrow` or `VestingEscrowFullyRevokable` contracts
"""

from vyper.interfaces import ERC20


interface IVestingEscrow:
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
    ) -> bool: nonpayable


event VestingEscrowCreated:
    creator: indexed(address)
    token: indexed(address)
    amount: uint256
    recipient: indexed(address)
    owner: address
    manager: address
    escrow: address
    escrow_type: uint256  # 0 - simple, 1 - fully revokable
    vesting_start: uint256
    vesting_duration: uint256
    cliff_length: uint256
    voting_adapter: address


target_simple: public(address)
target_fully_revokable: public(address)
default_voting_adapter: public(address)


@external
def __init__(
    target_simple: address,
    target_fully_revokable: address,
    default_voting_adapter: address,
):
    """
    @notice Contract constructor
    @dev Prior to deployment you must deploy one copy of `VestingEscrowSimple` and `VestingEscrowFullyRevokable` which
         are used as a library for vesting contracts deployed by this factory
    @param target_simple `VestingEscrow` contract address
    @param target_fully_revokable `VestingEscrowFullyRevokable` contract address
    """
    assert target_simple != empty(
        address
    ), "target_simple should not be ZERO_ADDRESS"
    assert target_fully_revokable != empty(
        address
    ), "target_fully_revokable should not be ZERO_ADDRESS"
    self.target_simple = target_simple
    self.target_fully_revokable = target_fully_revokable
    self.default_voting_adapter = default_voting_adapter


@external
def deploy_vesting_contract(
    token: address,
    amount: uint256,
    recipient: address,
    owner: address,
    vesting_duration: uint256,
    vesting_start: uint256 = block.timestamp,
    cliff_length: uint256 = 0,
    escrow_type: uint256 = 0,  # use simple escrow by default
    manager: address = empty(address),
) -> address:
    """
    @notice Deploy a new vesting contract without funding. Funding and activationa should be done separately
    @param token Address of the ERC20 token being distributed
    @param recipient Address to vest tokens for
    @param vesting_duration Time period over which tokens are released
    @param vesting_start Epoch time when tokens begin to vest
    @param cliff_length Duration after which the first portion vests
    @param escrow_type Escrow type to deploy 0 - `VestingEscrow`, 1 - `VestingEscrowFullyRevokable`
    """
    assert owner != empty(address), "zero_address owner"
    assert amount != 0, "zero amount"
    assert cliff_length <= vesting_duration, "incorrect vesting cliff"
    assert escrow_type in [0, 1], "incorrect escrow type"
    escrow: address = empty(address)
    if escrow_type == 1:  # dev: select target based on escrow type
        escrow = create_minimal_proxy_to(self.target_fully_revokable)
    else:
        escrow = create_minimal_proxy_to(self.target_simple)
    IVestingEscrow(escrow).initialize(
        token,
        amount,
        recipient,
        owner,
        manager,
        vesting_start,
        vesting_start + vesting_duration,
        cliff_length,
        self.default_voting_adapter,
    )
    log VestingEscrowCreated(
        msg.sender,
        token,
        amount,
        recipient,
        owner,
        manager,
        escrow,
        escrow_type,
        vesting_start,
        vesting_duration,
        cliff_length,
        self.default_voting_adapter,
    )
    return escrow
