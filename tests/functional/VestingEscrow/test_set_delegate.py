import brownie


def test_set_delegate(vesting, recipient):
    vesting.set_delegate({"from": recipient})


def test_vote_non_recipient(vesting, admin):
    with brownie.reverts("recipient only"):
        vesting.set_delegate({"from": admin})
