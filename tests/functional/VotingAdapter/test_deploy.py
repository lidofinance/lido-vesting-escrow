from brownie import ZERO_ADDRESS


def test_deploy_voting_adapter(VotingAdapter, owner, voting, snapshot_delegate):
    voting_adapter = VotingAdapter.deploy(voting, snapshot_delegate, ZERO_ADDRESS, {"from": owner})
    assert voting_adapter.voting_contract_addr() == voting
    assert voting_adapter.snapshot_delegate_contract_addr() == snapshot_delegate
    assert voting_adapter.delegation_contract_addr() == ZERO_ADDRESS
