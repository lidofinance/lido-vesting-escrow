import brownie
from brownie import ZERO_ADDRESS


def test_init_args(
    owner,
    VestingEscrowFactory,
    vesting_target_simple,
    vesting_target_fully_revokable,
    voting_adapter,
    token,
    manager,
):
    factory = VestingEscrowFactory.deploy(
        vesting_target_simple,
        vesting_target_fully_revokable,
        token,
        owner,
        manager,
        voting_adapter,
        {"from": owner},
    )
    assert factory.target_simple() == vesting_target_simple
    assert factory.target_fully_revokable() == vesting_target_fully_revokable
    assert factory.token() == token
    assert factory.voting_adapter() == voting_adapter
    assert factory.owner() == owner
    assert factory.manager() == manager


def test_init_fail_on_zero_revokable_target(
    owner,
    VestingEscrowFactory,
    vesting_target_fully_revokable,
    voting_adapter,
    token,
    manager,
):
    with brownie.reverts("zero target_simple"):
        VestingEscrowFactory.deploy(
            ZERO_ADDRESS,
            vesting_target_fully_revokable,
            token,
            owner,
            manager,
            voting_adapter,
            {"from": owner},
        )


def test_init_fail_on_zero_simple_target(
    owner,
    VestingEscrowFactory,
    vesting_target_simple,
    voting_adapter,
    token,
    manager,
):
    with brownie.reverts("zero target_fully_revokable"):
        VestingEscrowFactory.deploy(
            vesting_target_simple,
            ZERO_ADDRESS,
            token,
            owner,
            manager,
            voting_adapter,
            {"from": owner},
        )


def test_init_fail_on_zero_token(
    owner,
    VestingEscrowFactory,
    vesting_target_simple,
    vesting_target_fully_revokable,
    voting_adapter,
    manager,
):
    with brownie.reverts("zero token"):
        VestingEscrowFactory.deploy(
            vesting_target_simple,
            vesting_target_fully_revokable,
            ZERO_ADDRESS,
            owner,
            manager,
            voting_adapter,
            {"from": owner},
        )


def test_init_fail_on_zero_owner(
    owner,
    VestingEscrowFactory,
    vesting_target_simple,
    vesting_target_fully_revokable,
    voting_adapter,
    token,
    manager,
):
    with brownie.reverts("zero owner"):
        VestingEscrowFactory.deploy(
            vesting_target_simple,
            vesting_target_fully_revokable,
            token,
            ZERO_ADDRESS,
            manager,
            voting_adapter,
            {"from": owner},
        )
