import brownie
from brownie import ZERO_ADDRESS

def test_delegate(voting_adapter, recipient, delegate):
    with brownie.reverts("not implemented"):
        tx = voting_adapter.delegate(ZERO_ADDRESS, delegate, {"from": recipient})
