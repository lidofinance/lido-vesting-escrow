import brownie
from brownie import ZERO_ADDRESS


def test_activate_vesting_contract(
    deployed_vesting, vesting_factory, token, owner, balance
):
    token._mint_for_testing(balance, {"from": owner})
    token.approve(vesting_factory, balance, {"from": owner})
    vesting_factory.activate_vesting_contract(
        deployed_vesting.address,
        balance,
        ZERO_ADDRESS,
        {"from": owner},
    )
    assert deployed_vesting.total_locked() == balance
    assert token.balanceOf(deployed_vesting.address) == balance


def test_activate_vesting_contract_no_funds(
    deployed_vesting, vesting_factory, token, owner, balance
):
    token.approve(vesting_factory, balance, {"from": owner})
    with brownie.reverts():
        vesting_factory.activate_vesting_contract(
            deployed_vesting.address,
            balance,
            ZERO_ADDRESS,
            {"from": owner},
        )


def test_activate_vesting_contract_no_approve(
    deployed_vesting, vesting_factory, token, owner, balance
):
    token._mint_for_testing(balance, {"from": owner})
    with brownie.reverts():
        vesting_factory.activate_vesting_contract(
            deployed_vesting.address,
            balance,
            ZERO_ADDRESS,
            {"from": owner},
        )


def test_token_approval(activated_vesting, vesting_factory, token):
    # remaining approval should be zero
    assert token.allowance(activated_vesting, vesting_factory) == 0


def test_activate_vars(activated_vesting, owner, manager, balance):
    assert activated_vesting.owner() == owner
    assert activated_vesting.manager() == manager
    assert activated_vesting.total_locked() == balance
