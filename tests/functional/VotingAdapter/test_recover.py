import brownie
from tests.utils import mint_or_transfer_for_testing


def test_recover_erc20(voting_adapter, token, anyone, balance, owner, random_guy, deployed):
    mint_or_transfer_for_testing(owner, random_guy, token, balance, deployed)
    token.transfer(voting_adapter, balance, {"from": random_guy})

    owner_balance = token.balanceOf(owner)
    voting_adapter.recover_erc20(token, balance, {"from": anyone})
    assert token.balanceOf(owner) == balance + owner_balance
    assert token.balanceOf(voting_adapter) == 0


def test_recover_ether(voting_adapter, anyone, owner, random_guy, one_eth, destructible):
    random_guy.transfer(destructible, one_eth)
    destructible.destruct(voting_adapter)
    assert voting_adapter.balance() == one_eth
    balance_before = owner.balance()
    voting_adapter.recover_ether({"from": anyone})
    assert owner.balance() == balance_before + one_eth
    assert voting_adapter.balance() == 0


def test_cant_send_ether(voting_adapter, random_guy, one_eth):
    with brownie.reverts(""):
        random_guy.transfer(voting_adapter, one_eth)
