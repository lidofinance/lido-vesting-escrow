import brownie


def test_set_delegate(vesting, accounts):
    vesting.set_delegate({"from": accounts[1]})


def test_vote_non_recipient(vesting, accounts):
    with brownie.reverts("recipient only"):
        vesting.set_delegate({"from": accounts[0]})
