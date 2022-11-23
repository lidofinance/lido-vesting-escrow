import brownie
from brownie import ZERO_ADDRESS
import pytest


def test_targets_are_set(
    vesting_factory, vesting_target_simple, vesting_target_fully_revokable
):
    assert vesting_factory.target_simple() == vesting_target_simple
    assert vesting_factory.target_fully_revokable() == vesting_target_fully_revokable


def test_deploy_simple(owner, recipient, vesting_factory, token, balance):
    tx = vesting_factory.deploy_vesting_contract(
        token, balance, recipient, owner, 86400 * 365, {"from": owner}
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]


def test_deploy_fully_revokable(owner, recipient, balance, vesting_factory, token, start_time):
    tx = vesting_factory.deploy_vesting_contract(
        token,
        balance,
        recipient,
        owner,
        86400 * 365,
        start_time,
        0,
        1,
        {"from": owner},
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]


@pytest.mark.parametrize("type", [2, 154])
def test_deploy_invalid_type(
    owner, recipient, balance, vesting_factory, token, start_time, type
):
    with brownie.reverts("incorrect escrow type"):
        vesting_factory.deploy_vesting_contract(
            token,
            balance,
            recipient,
            owner,
            86400 * 365,
            start_time,
            0,
            type,
            {"from": owner},
        )


def test_start_and_duration(
    VestingEscrow, owner, recipient, balance, chain, vesting_factory, token
):
    start_time = chain.time() + 100

    tx = vesting_factory.deploy_vesting_contract(
        token,
        balance,
        recipient,
        owner,
        86400 * 700,
        start_time,
        {"from": owner},
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]

    escrow = VestingEscrow.at(tx.return_value)
    assert escrow.start_time() == start_time
    assert escrow.end_time() == start_time + 86400 * 700


def test_invalid_cliff_duration(owner, recipient, balance, chain, vesting_factory, token):
    start_time = chain.time() + 100
    duration = 86400 * 700
    cliff_time = start_time + duration
    with brownie.reverts("incorrect vesting cliff"):
        vesting_factory.deploy_vesting_contract(
            token,
            balance,
            recipient,
            owner,
            duration,
            start_time,
            cliff_time,
            {"from": owner},
        )


def test_invalid_owner(owner, recipient, balance, chain, vesting_factory, token):
    start_time = chain.time() + 100
    duration = 86400 * 700
    with brownie.reverts("zero_address owner"):
        vesting_factory.deploy_vesting_contract(
            token,
            balance,
            recipient,
            ZERO_ADDRESS,
            duration,
            start_time,
            0,
            {"from": owner},
        )


def test_invalid_amount(owner, recipient, chain, vesting_factory, token):
    start_time = chain.time() + 100
    duration = 86400 * 700
    with brownie.reverts("zero amount"):
        vesting_factory.deploy_vesting_contract(
            token,
            0,
            recipient,
            owner,
            duration,
            start_time,
            0,
            {"from": owner},
        )


def test_init_vars(deployed_vesting, recipient, owner, manager, balance, token, start_time, end_time):
    assert deployed_vesting.token() == token
    assert deployed_vesting.recipient() == recipient
    assert deployed_vesting.start_time() == start_time
    assert deployed_vesting.end_time() == end_time
    assert deployed_vesting.owner() == owner
    assert deployed_vesting.manager() == manager
    assert deployed_vesting.total_locked() == balance
    assert deployed_vesting.activated() == False
    assert deployed_vesting.initialized() == True



def test_cannot_call_init(
    deployed_vesting, owner, recipient, manager, token, balance, start_time, end_time, voting_adapter
):
    with brownie.reverts():
        deployed_vesting.initialize(
            token,
            balance,
            recipient,
            owner,
            manager,
            start_time,
            end_time,
            0,
            voting_adapter,
            {"from": owner},
        )


def test_cannot_init_factory_target_simple(
    vesting_target_simple,
    owner,
    recipient,
    token,
    balance,
    manager,
    start_time,
    end_time,
    voting_adapter,
):
    with brownie.reverts("can only initialize once"):
        vesting_target_simple.initialize(
            token,
            balance,
            recipient,
            owner,
            manager,
            start_time,
            end_time,
            0,
            voting_adapter,
            {"from": owner},
        )


def test_cannot_init_factory_targe_fully_revokable(
    vesting_target_fully_revokable,
    owner,
    recipient,
    token,
    balance,
    manager,
    start_time,
    end_time,
    voting_adapter,
):
    with brownie.reverts("can only initialize once"):
        vesting_target_fully_revokable.initialize(
            token,
            balance,
            recipient,
            owner,
            manager,
            start_time,
            end_time,
            0,
            voting_adapter,
            {"from": owner},
        )
