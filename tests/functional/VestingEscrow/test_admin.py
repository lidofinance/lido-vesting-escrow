import brownie
from brownie import ZERO_ADDRESS


def test_commit_admin_only(vesting, recipient):
    with brownie.reverts("admin only"):
        vesting.commit_transfer_ownership(recipient, {"from": recipient})


def test_apply_admin_only(vesting, recipient):
    with brownie.reverts("future admin only"):
        vesting.apply_transfer_ownership({"from": recipient})


def test_renounce_ownership_only(vesting, recipient):
    with brownie.reverts("admin only"):
        vesting.renounce_ownership({"from": recipient})


def test_commit_transfer_ownership(vesting, admin, recipient):
    vesting.commit_transfer_ownership(recipient, {"from": admin})

    assert vesting.admin() == admin
    assert vesting.future_admin() == recipient


def test_apply_transfer_ownership(vesting, admin, recipient):
    vesting.commit_transfer_ownership(recipient, {"from": admin})
    vesting.apply_transfer_ownership({"from": recipient})

    assert vesting.admin() == recipient


def test_apply_without_commit(vesting, admin):
    with brownie.reverts("future admin only"):
        vesting.apply_transfer_ownership({"from": admin})


def test_renounce_ownership(vesting, admin):
    vesting.renounce_ownership({"from": admin})

    assert vesting.admin() == ZERO_ADDRESS
    assert vesting.future_admin() == ZERO_ADDRESS
