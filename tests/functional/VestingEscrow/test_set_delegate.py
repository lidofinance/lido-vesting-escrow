import brownie


def test_set_delegate(vesting, recipient):
    tx = vesting.set_delegate({"from": recipient})
    assert len(tx.events) == 1


def test_vote_non_recipient(vesting, admin):
    with brownie.reverts("recipient only"):
        vesting.set_delegate({"from": admin})
