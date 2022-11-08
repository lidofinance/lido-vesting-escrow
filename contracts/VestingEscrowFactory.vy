# @version 0.3.7
"""
@title Vesting Escrow Factory
@author Curve Finance, Yearn Finance, Lido Finance
@license MIT
@notice Stores and distributes ERC20 tokens by deploying `VestingEscrowSimple` or `VestingEscrowOptimised` contracts
"""

from vyper.interfaces import ERC20


interface IVestingEscrow:
    def initialize(
        admin: address,
        token: address,
        recipient: address,
        amount: uint256,
        start_time: uint256,
        end_time: uint256,
        cliff_length: uint256,
    ) -> bool: nonpayable


event VestingEscrowCreated:
    funder: indexed(address)
    token: indexed(address)
    recipient: indexed(address)
    escrow: address
    escrow_type: uint256 # 0 - simple, 1 - optimised
    amount: uint256
    vesting_start: uint256
    vesting_duration: uint256
    cliff_length: uint256


target_simple: public(address)
target_optimised: public(address)

@external
def __init__(target_simple: address, target_optimized: address):
    """
    @notice Contract constructor
    @dev Prior to deployment you must deploy one copy of `VestingEscrowSimple` and `VestingEscrowOptimised` which
         are used as a library for vesting contracts deployed by this factory
    @param target_simple `VestingEscrowSimple` contract address
    @param target_optimised `VestingEscrowOptimised` contract address
    """
    assert target_simple != ZERO_ADDRESS # dev: target_simple should not be ZERO_ADDRESS
    assert target_optimized != ZERO_ADDRESS # dev: target_simple should not be ZERO_ADDRESS
    self.target_simple = target_simple
    self.target_optimized = target_optimised


@external
def deploy_vesting_contract(
    token: address,
    recipient: address,
    amount: uint256,
    vesting_duration: uint256,
    vesting_start: uint256 = block.timestamp,
    cliff_length: uint256 = 0,
    escrow_type: uint256 = 0, # use simple escrow by default
) -> address:
    """
    @notice Deploy a new vesting contract
    @param token Address of the ERC20 token being distributed
    @param recipient Address to vest tokens for
    @param amount Amount of tokens being vested for `recipient`
    @param vesting_duration Time period over which tokens are released
    @param vesting_start Epoch time when tokens begin to vest
    @param cliff_length Duration after which the first portion vests
    @param escrow_type Escrow type to deploy 0 - `VestingEscrowSimple`, 1 - `VestingEscrowOptimised`
    """
    assert cliff_length <= vesting_duration  # dev: incorrect vesting cliff
    assert escrow_type in [0,1] # dev: incorrect escrow type
    if escrow_type == 1: # dev: select target based on escrow type
        escrow: address = create_minimal_proxy_to(self.target_optimised)
    else
        escrow: address = create_minimal_proxy_to(self.target_simple)
    assert ERC20(token).transferFrom(msg.sender, self, amount)  # dev: funding failed
    assert ERC20(token).approve(escrow, amount)  # dev: approve failed
    IVestingEscrow(escrow).initialize(
        msg.sender,
        token,
        recipient,
        amount,
        vesting_start,
        vesting_start + vesting_duration,
        cliff_length,
    )
    log VestingEscrowCreated(msg.sender, token, recipient, escrow, escrow_type, amount, vesting_start, vesting_duration, cliff_length)
    return escrow
