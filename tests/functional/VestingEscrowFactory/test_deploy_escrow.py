import brownie
import pytest
from brownie import ZERO_ADDRESS

from tests.utils import mint_or_transfer_for_testing


@pytest.fixture()
def initial_funding(token, balance, vesting_factory, owner, deployed):
    mint_or_transfer_for_testing(owner, owner, token, balance, deployed)
    token.approve(vesting_factory, balance, {"from": owner})


def test_params_are_set(
    vesting_factory,
    vesting_target,
    voting_adapter,
    token,
    owner,
    manager,
):
    assert vesting_factory.target() == vesting_target
    assert vesting_factory.token() == token
    assert vesting_factory.owner() == owner
    assert vesting_factory.manager() == manager
    assert vesting_factory.voting_adapter() == voting_adapter


@pytest.mark.usefixtures("initial_funding")
def test_deploy(owner, recipient, vesting_factory, balance):
    tx = vesting_factory.deploy_vesting_contract(balance, recipient, 86400 * 365, {"from": owner})

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]


def test_deploy_no_approve(owner, recipient, vesting_factory, balance):
    with brownie.reverts(""):
        vesting_factory.deploy_vesting_contract(balance, recipient, 86400 * 365, {"from": owner})


@pytest.mark.no_deploy
def test_deploy_from_factory_with_invalid_token(owner, recipient, vesting_factory_with_invalid_token, balance):
    with brownie.reverts(""):
        vesting_factory_with_invalid_token.deploy_vesting_contract(balance, recipient, 86400 * 365, {"from": owner})


@pytest.mark.usefixtures("initial_funding")
def test_start_and_duration(VestingEscrow, owner, recipient, balance, chain, vesting_factory):
    start_time = chain.time() + 100

    tx = vesting_factory.deploy_vesting_contract(
        balance,
        recipient,
        86400 * 700,
        start_time,
        {"from": owner},
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]

    escrow = VestingEscrow.at(tx.return_value)
    assert escrow.start_time() == start_time
    assert escrow.end_time() == start_time + 86400 * 700


@pytest.mark.usefixtures("initial_funding")
def test_zero_recipient(owner, balance, vesting_factory):
    with brownie.reverts("zero recipient"):
        vesting_factory.deploy_vesting_contract(balance, ZERO_ADDRESS, 86400 * 365, {"from": owner})


def test_invalid_cliff_duration(owner, recipient, balance, chain, vesting_factory):
    start_time = chain.time() + 100
    duration = 86400 * 700
    cliff_time = start_time + duration
    with brownie.reverts("incorrect vesting cliff"):
        vesting_factory.deploy_vesting_contract(
            balance,
            recipient,
            duration,
            start_time,
            cliff_time,
            {"from": owner},
        )


def test_invalid_duration(owner, recipient, balance, vesting_factory, start_time):
    with brownie.reverts("incorrect vesting duration"):
        vesting_factory.deploy_vesting_contract(
            balance,
            recipient,
            0,
            start_time,
            0,
            {"from": owner},
        )


def test_invalid_amount(owner, recipient, vesting_factory, start_time):
    duration = 86400 * 700
    with brownie.reverts("incorrect amount"):
        vesting_factory.deploy_vesting_contract(
            0,
            recipient,
            duration,
            start_time,
            0,
            {"from": owner},
        )


def test_init_vars(deployed_vesting, recipient, balance, token, start_time, end_time):
    assert deployed_vesting.token() == token
    assert deployed_vesting.recipient() == recipient
    assert deployed_vesting.start_time() == start_time
    assert deployed_vesting.end_time() == end_time
    assert deployed_vesting.total_locked() == balance
    assert deployed_vesting.initialized() is True


def test_cannot_call_init(
    vesting_factory,
    deployed_vesting,
    owner,
    recipient,
    token,
    balance,
    start_time,
    end_time,
):
    with brownie.reverts("can only initialize once"):
        deployed_vesting.initialize(
            token,
            balance,
            recipient,
            start_time,
            end_time,
            0,
            0,
            vesting_factory,
            {"from": owner},
        )


def test_cannot_init_factory_target(
    vesting_factory,
    vesting_target,
    owner,
    recipient,
    token,
    balance,
    start_time,
    end_time,
):
    with brownie.reverts("can only initialize once"):
        vesting_target.initialize(
            token,
            balance,
            recipient,
            start_time,
            end_time,
            0,
            0,
            vesting_factory,
            {"from": owner},
        )
