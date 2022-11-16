import pytest
from brownie import ZERO_ADDRESS


def test_activate_vesting_contracts(
    deployed_vesting, ya_deployed_vesting, vesting_factory, token, owner, balance
):
    token._mint_for_testing(balance * 2, {"from": owner})
    token.approve(vesting_factory, balance * 2, {"from": owner})
    vesting_factory.activate_vesting_contracts(
        [(deployed_vesting.address, balance), (ya_deployed_vesting.address, balance)],
        ZERO_ADDRESS,
        {"from": owner},
    )
    assert deployed_vesting.total_locked() == balance
    assert token.balanceOf(deployed_vesting.address) == balance

    assert ya_deployed_vesting.total_locked() == balance
    assert token.balanceOf(ya_deployed_vesting.address) == balance


@pytest.mark.fat
def test_activate_hundred_vestings(
    hundred_deployed_vestings, vesting_factory, token, owner, balance
):
    token._mint_for_testing(balance * 100, {"from": owner})
    token.approve(vesting_factory, balance * 100, {"from": owner})
    data = [(vesting.address, balance) for vesting in hundred_deployed_vestings]
    vesting_factory.activate_vesting_contracts(
        data,
        ZERO_ADDRESS,
        {"from": owner},
    )
    for vesting in hundred_deployed_vestings:
        assert vesting.total_locked() == balance
        assert token.balanceOf(vesting.address) == balance
