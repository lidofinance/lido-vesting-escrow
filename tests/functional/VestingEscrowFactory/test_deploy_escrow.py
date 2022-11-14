import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def initial_funding(token, vesting_factory, admin, balance):
    token._mint_for_testing(balance * 10, {"from": admin})
    token.approve(vesting_factory, balance * 10, {"from": admin})


def test_funding_fail(accounts, admin, vesting_factory, token, balance):
    with brownie.reverts(""):  # revert is happening in ERC20 code
        vesting_factory.deploy_vesting_contract(
            token,
            accounts[2],
            balance * 10**2,
            86400 * 365,
            {"from": admin},
        )


def test_targets_are_set(
    vesting_factory, vesting_target_simple, vesting_target_fully_revokable
):
    assert vesting_factory.target_simple() == vesting_target_simple
    assert vesting_factory.target_fully_revokable() == vesting_target_fully_revokable


def test_deploy_simple(admin, recipient, vesting_factory, token, balance):
    tx = vesting_factory.deploy_vesting_contract(
        token, recipient, balance, 86400 * 365, {"from": admin}
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]


def test_deploy_fully_revokable(
    admin, recipient, vesting_factory, token, start_time, balance
):
    tx = vesting_factory.deploy_vesting_contract(
        token,
        recipient,
        balance,
        86400 * 365,
        start_time,
        0,
        1,
        {"from": admin},
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]


@pytest.mark.parametrize("type", [2, 154])
def test_deploy_invalid_type(
    admin, recipient, vesting_factory, token, start_time, type, balance
):
    with brownie.reverts("incorrect escrow type"):
        vesting_factory.deploy_vesting_contract(
            token,
            recipient,
            balance,
            86400 * 365,
            start_time,
            0,
            type,
            {"from": admin},
        )


def test_start_and_duration(
    VestingEscrowSimple, admin, recipient, chain, vesting_factory, token, balance
):
    start_time = chain.time() + 100

    tx = vesting_factory.deploy_vesting_contract(
        token,
        recipient,
        balance,
        86400 * 700,
        start_time,
        {"from": admin},
    )

    assert len(tx.new_contracts) == 1
    assert tx.return_value == tx.new_contracts[0]

    escrow = VestingEscrowSimple.at(tx.return_value)
    assert escrow.start_time() == start_time
    assert escrow.end_time() == start_time + 86400 * 700


def test_invalid_cliff_duration(
    admin, recipient, chain, vesting_factory, token, balance
):
    start_time = chain.time() + 100
    duration = 86400 * 700
    cliff_time = start_time + duration
    with brownie.reverts("incorrect vesting cliff"):
        vesting_factory.deploy_vesting_contract(
            token,
            recipient,
            balance,
            duration,
            start_time,
            cliff_time,
            {"from": admin},
        )


def test_token_xfer(vesting, token, balance):
    # exactly 10**18 tokens should be transferred
    assert token.balanceOf(vesting) == balance


def test_token_approval(vesting, vesting_factory, token):
    # remaining approval should be zero
    assert token.allowance(vesting, vesting_factory) == 0


def test_init_vars(vesting, admin, recipient, token, start_time, end_time, balance):
    assert vesting.token() == token
    assert vesting.admin() == admin
    assert vesting.recipient() == recipient
    assert vesting.start_time() == start_time
    assert vesting.end_time() == end_time
    assert vesting.total_locked() == balance


def test_cannot_call_init(
    vesting, admin, recipient, token, start_time, end_time, balance
):
    with brownie.reverts():
        vesting.initialize(
            admin,
            token,
            recipient,
            balance,
            start_time,
            end_time,
            0,
            {"from": admin},
        )


def test_cannot_init_factory_target_simple(
    vesting_target_simple, admin, recipient, token, start_time, end_time, balance
):
    with brownie.reverts("can only initialize once"):
        vesting_target_simple.initialize(
            admin,
            token,
            recipient,
            balance,
            start_time,
            end_time,
            0,
            {"from": admin},
        )


def test_cannot_init_factory_targe_fully_revokable(
    vesting_target_fully_revokable,
    admin,
    recipient,
    token,
    start_time,
    end_time,
    balance,
):
    with brownie.reverts("can only initialize once"):
        vesting_target_fully_revokable.initialize(
            admin,
            token,
            recipient,
            balance,
            start_time,
            end_time,
            0,
            {"from": admin},
        )
