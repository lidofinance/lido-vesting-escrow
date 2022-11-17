import brownie


def test_set_delegate(activated_vesting, recipient):
    tx = activated_vesting.set_delegate({"from": recipient})
    assert len(tx.events) == 1
    assert tx.events[0]["delegator"] == activated_vesting.address
    assert tx.events[0]["delegate"] == recipient


def test_set_delegate_to_custom_delegate(activated_vesting, recipient, random_guy):
    tx = activated_vesting.set_delegate(random_guy, {"from": recipient})
    assert len(tx.events) == 1
    assert tx.events[0]["delegator"] == activated_vesting.address
    assert tx.events[0]["delegate"] == random_guy


def test_set_delegate_from_owner_fail(activated_vesting, owner):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.set_delegate({"from": owner})


def test_set_delegate_from_manager_fail(activated_vesting, manager):
    with brownie.reverts("msg.sender not recipient"):
        activated_vesting.set_delegate({"from": manager})
