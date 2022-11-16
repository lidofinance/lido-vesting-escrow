import brownie


def test_set_delegate(activated_vesting, recipient):
    tx = activated_vesting.set_delegate({"from": recipient})
    assert len(tx.events) == 1


def test_set_delegate_from_owner_fail(activated_vesting, owner):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.set_delegate({"from": owner})


def test_set_delegate_from_manager_fail(activated_vesting, manager):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.set_delegate({"from": manager})
