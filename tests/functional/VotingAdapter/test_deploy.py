import pytest
import brownie
from brownie import ZERO_ADDRESS

pytestmark = pytest.mark.no_deploy

def test_deploy_voting_adapter(VotingAdapter, owner, voting, snapshot_delegate):
    voting_adapter = VotingAdapter.deploy(voting, snapshot_delegate, ZERO_ADDRESS, owner, {"from": owner})
    assert voting_adapter.voting_contract_addr() == voting
    assert voting_adapter.snapshot_delegate_contract_addr() == snapshot_delegate
    assert voting_adapter.delegation_contract_addr() == ZERO_ADDRESS
    assert voting_adapter.owner() == owner


def test_deploy_zero_owner(VotingAdapter, owner, voting, snapshot_delegate):
    with brownie.reverts("zero owner"):
        VotingAdapter.deploy(voting, snapshot_delegate, ZERO_ADDRESS, ZERO_ADDRESS, {"from": owner})


def test_deploy_zero_voting(VotingAdapter, owner, snapshot_delegate):
    with brownie.reverts("zero voting_addr"):
        VotingAdapter.deploy(ZERO_ADDRESS, snapshot_delegate, ZERO_ADDRESS, owner, {"from": owner})


def test_deploy_zero_snapshot(VotingAdapter, owner, voting):
    with brownie.reverts("zero snapshot_delegate_addr"):
        VotingAdapter.deploy(voting, ZERO_ADDRESS, ZERO_ADDRESS, owner, {"from": owner})
