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


event ERC20Recovered:
    token: address
    amount: uint256


event ETHRecovered:
    amount: uint256


target_simple: public(address)
target_fully_revokable: public(address)
token: public(address)
voting_adapter: public(address)
owner: public(address)
manager: public(address)


@external
def __init__(
    target_simple: address,
    target_fully_revokable: address,
    token: address,
    owner: address,
    manager: address,
    voting_adapter: address,
):
    """
    @notice Contract constructor
    @dev Prior to deployment you must deploy one copy of `VestingEscrowSimple` and `VestingEscrowFullyRevokable` which
         are used as a library for vesting contracts deployed by this factory
    @param target_simple `VestingEscrow` contract address
    @param target_fully_revokable `VestingEscrowFullyRevokable` contract address
    @param token Address of the ERC20 token being distributed using escrows
    @param owner Address of the owner of the deployed escrows
    @param manager Address of the manager of the deployed escrows
    @param voting_adapter Address of the Lido Voting Adapter
    """
    assert target_simple != empty(address), "zero target_simple"
    assert target_fully_revokable != empty(
        address
    ), "zero target_fully_revokable"
    assert owner != empty(address), "zero owner"
    assert token != empty(address), "zero token"
    self.target_simple = target_simple
    self.target_fully_revokable = target_fully_revokable
    self.token = token
    self.owner = owner
    self.manager = manager
    self.voting_adapter = voting_adapter


@external
def deploy_vesting_contract(
    amount: uint256,
    recipient: address,
    vesting_duration: uint256,
    vesting_start: uint256 = block.timestamp,
    cliff_length: uint256 = 0,
    escrow_type: uint256 = 0,  # use simple escrow by default
) -> address:
    """
    @notice Deploy and fund a new vesting contract
    @param amount Amount of the tokens to be vested after fundings
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
    assert ERC20(self.token).transferFrom(msg.sender, self, amount), "funding failed"
    assert ERC20(self.token).approve(escrow, amount), "approve failed"
    IVestingEscrow(escrow).initialize(
        self.token,
        amount,
        recipient,
        self.owner,
        self.manager,
        vesting_start,
        vesting_start + vesting_duration,
        cliff_length,
        self.voting_adapter,
    )
    log VestingEscrowCreated(
        msg.sender,
        self.token,
        amount,
        recipient,
        self.owner,
        self.manager,
        escrow,
        escrow_type,
        vesting_start,
        vesting_duration,
        cliff_length,
        self.voting_adapter,
    )
    return escrow


@external
def recover_erc20(token: address, amount: uint256):
    """
    @notice Recover ERC20 tokens to owner
    @param token Address of the ERC20 token to be recovered
    """
    assert ERC20(token).transfer(self.owner, amount)
    log ERC20Recovered(token, amount)


@external
def recover_ether():
    """
    @notice Recover Ether to owner
    """
    amount: uint256 = self.balance
    send(self.owner, amount)
    log ETHRecovered(amount)
