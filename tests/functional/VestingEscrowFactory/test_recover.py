import pytest

from tests.utils import mint_or_transfer_for_testing


@pytest.fixture
def token2(ERC20, owner):
    return ERC20.deploy("XYZ", "XYZ", 18, {"from": owner})


def test_recover_non_vested_token(vesting_factory, token2, anyone, owner, balance, random_guy):
    token2._mint_for_testing(balance, {"from": random_guy})
    token2.transfer(vesting_factory, balance, {"from": random_guy})

    vesting_factory.recover_erc20(token2, balance, {"from": anyone})
    assert token2.balanceOf(owner) == balance
    assert token2.balanceOf(vesting_factory) == 0


def test_recover_vested_token(vesting_factory, token, anyone, balance, owner, random_guy, deployed):
    mint_or_transfer_for_testing(owner, random_guy, token, balance, deployed)
    token.transfer(vesting_factory, balance, {"from": random_guy})

    owner_balance = token.balanceOf(owner)
    vesting_factory.recover_erc20(token, balance, {"from": anyone})
    assert token.balanceOf(owner) == balance + owner_balance
    assert token.balanceOf(vesting_factory) == 0


def test_recover_ether(vesting_factory, anyone, owner, random_guy, one_eth, destructible):
    random_guy.transfer(destructible, one_eth)
    destructible.destruct(vesting_factory)
    assert vesting_factory.balance() == one_eth
    balance_before = owner.balance()
    vesting_factory.recover_ether({"from": anyone})
    assert owner.balance() == balance_before + one_eth
    assert vesting_factory.balance() == 0
