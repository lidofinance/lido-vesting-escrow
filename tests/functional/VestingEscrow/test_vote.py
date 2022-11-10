import brownie


def test_vote(vesting, accounts):
    vesting.vote(154, True, {"from": accounts[1]})


def test_vote_non_recipient(vesting, accounts):
    with brownie.reverts("recipient only"):
        vesting.vote(154, True, {"from": accounts[0]})
