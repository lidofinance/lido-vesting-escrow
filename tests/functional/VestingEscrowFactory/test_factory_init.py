import brownie
import pytest
from brownie import ZERO_ADDRESS

pytestmark = pytest.mark.no_deploy


def test_init_args(
    owner,
    VestingEscrowFactory,
    vesting_target,
    voting_adapter,
    token,
    manager,
):
    factory = VestingEscrowFactory.deploy(
        vesting_target,
        token,
        owner,
        manager,
        voting_adapter,
        {"from": owner},
    )
    assert factory.target() == vesting_target
    assert factory.token() == token
    assert factory.voting_adapter() == voting_adapter
    assert factory.owner() == owner
    assert factory.manager() == manager


def test_init_fail_on_zero_target(
    owner,
    VestingEscrowFactory,
    voting_adapter,
    token,
    manager,
):
    with brownie.reverts("zero target"):
        VestingEscrowFactory.deploy(
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
    vesting_target,
    voting_adapter,
    manager,
):
    with brownie.reverts("zero token"):
        VestingEscrowFactory.deploy(
            vesting_target,
            ZERO_ADDRESS,
            owner,
            manager,
            voting_adapter,
            {"from": owner},
        )


def test_init_fail_on_zero_owner(
    owner,
    VestingEscrowFactory,
    vesting_target,
    voting_adapter,
    token,
    manager,
):
    with brownie.reverts("zero owner"):
        VestingEscrowFactory.deploy(
            vesting_target,
            token,
            ZERO_ADDRESS,
            manager,
            voting_adapter,
            {"from": owner},
        )
