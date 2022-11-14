import brownie


def test_vote(vesting, recipient):
    vesting.vote(154, True, {"from": recipient})


def test_vote_non_recipient(vesting, admin):
    with brownie.reverts("recipient only"):
        vesting.vote(154, True, {"from": admin})
