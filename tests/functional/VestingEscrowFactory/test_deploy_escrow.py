import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def initial_funding(token, vesting_factory, accounts):
    token._mint_for_testing(10**21, {"from": accounts[0]})
    token.approve(vesting_factory, 10**21, {"from": accounts[0]})


def test_funding_fail(accounts, vesting_factory, token):
    with brownie.reverts(""):  # revert is happening in ERC20 code
        vesting_factory.deploy_vesting_contract(
            token,
            accounts[2],
            10**22,
            86400 * 365,
            {"from": accounts[0]},
        )


def test_targets_are_set(
    vesting_factory, vesting_target_simple, vesting_target_fully_revokable
):
    assert vesting_factory.target_simple() == vesting_target_simple
    assert vesting_factory.target_fully_revokable() == vesting_target_fully_revokable


def test_deploy_simple(accounts, vesting_factory, token):
    tx = vesting_factory.deploy_vesting_contract(
        token, accounts[1], 10**18, 86400 * 365, {"from": accounts[0]}
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]


def test_deploy_fully_revokable(accounts, vesting_factory, token, start_time):
    tx = vesting_factory.deploy_vesting_contract(
        token,
        accounts[1],
        10**18,
        86400 * 365,
        start_time,
        0,
        1,
        {"from": accounts[0]},
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]


@pytest.mark.parametrize("type", [2, 154])
def test_deploy_invalid_type(accounts, vesting_factory, token, start_time, type):
    with brownie.reverts("incorrect escrow type"):
        vesting_factory.deploy_vesting_contract(
            token,
            accounts[1],
            10**18,
            86400 * 365,
            start_time,
            0,
            type,
            {"from": accounts[0]},
        )


def test_start_and_duration(
    VestingEscrowSimple, accounts, chain, vesting_factory, token
):
    start_time = chain.time() + 100

    tx = vesting_factory.deploy_vesting_contract(
        token,
        accounts[1],
        10**18,
        86400 * 700,
        start_time,
        {"from": accounts[0]},
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]

    escrow = VestingEscrowSimple.at(tx.return_value)
    assert escrow.start_time() == start_time
    assert escrow.end_time() == start_time + 86400 * 700


def test_invalid_cliff_duration(accounts, chain, vesting_factory, token):
    start_time = chain.time() + 100
    duration = 86400 * 700
    cliff_time = start_time + duration
    with brownie.reverts("incorrect vesting cliff"):
        vesting_factory.deploy_vesting_contract(
            token,
            accounts[1],
            10**18,
            duration,
            start_time,
            cliff_time,
            {"from": accounts[0]},
        )


def test_token_xfer(vesting, token):
    # exactly 10**18 tokens should be transferred
    assert token.balanceOf(vesting) == 10**20


def test_token_approval(vesting, vesting_factory, token):
    # remaining approval should be zero
    assert token.allowance(vesting, vesting_factory) == 0


def test_init_vars(vesting, accounts, token, start_time, end_time):
    assert vesting.token() == token
    assert vesting.admin() == accounts[0]
    assert vesting.recipient() == accounts[1]
    assert vesting.start_time() == start_time
    assert vesting.end_time() == end_time
    assert vesting.total_locked() == 10**20


def test_cannot_call_init(vesting, accounts, token, start_time, end_time):
    with brownie.reverts():
        vesting.initialize(
            accounts[0],
            token,
            accounts[1],
            10**20,
            start_time,
            end_time,
            0,
            {"from": accounts[0]},
        )


def test_cannot_init_factory_target_simple(
    vesting_target_simple, accounts, token, start_time, end_time
):
    with brownie.reverts("can only initialize once"):
        vesting_target_simple.initialize(
            accounts[0],
            token,
            accounts[1],
            10**20,
            start_time,
            end_time,
            0,
            {"from": accounts[0]},
        )


def test_cannot_init_factory_targe_fully_revokable(
    vesting_target_fully_revokable, accounts, token, start_time, end_time
):
    with brownie.reverts("can only initialize once"):
        vesting_target_fully_revokable.initialize(
            accounts[0],
            token,
            accounts[1],
            10**20,
            start_time,
            end_time,
            0,
            {"from": accounts[0]},
        )
