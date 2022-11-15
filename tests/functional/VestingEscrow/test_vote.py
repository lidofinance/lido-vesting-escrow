import brownie


def test_vote(vesting, recipient):
    tx = vesting.vote(154, True, {"from": recipient})
    assert len(tx.events) == 1


def test_vote_non_recipient(vesting, admin):
    with brownie.reverts("recipient only"):
        vesting.vote(154, True, {"from": admin})
