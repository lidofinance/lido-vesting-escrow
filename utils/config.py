from dotmap import DotMap

from vesting_initial_params import ARAGON_VOTING, DELEGATION, MANAGER, OWNER, SNAPSHOT_DELEGATION, TOKEN


def get_common_deploy_args():
    return DotMap(
        {
            "token": TOKEN,
            "owner": OWNER,
            "manager": MANAGER,
            "aragon_voting": ARAGON_VOTING,
            "snapshot_delegation": SNAPSHOT_DELEGATION,
            "delegation": DELEGATION,
        }
    )


def prepare_voting_adapter_deploy_args(
    voting_addr,
    snapshot_delegate_addr,
    delegation_addr,
    owner,
):
    return DotMap(
        {
            "voting_addr": voting_addr,
            "snapshot_delegate_addr": snapshot_delegate_addr,
            "delegation_addr": delegation_addr,
            "owner": owner,
        }
    )


def prepare_factory_deploy_args(
    target,
    token,
    owner,
    manager,
    voting_adapter,
):
    return DotMap(
        {
            "target": target,
            "token": token,
            "owner": owner,
            "manager": manager,
            "voting_adapter": voting_adapter,
        }
    )
