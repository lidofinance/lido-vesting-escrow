from dotmap import DotMap
from brownie import network
from brownie.utils import color

if network.show_active() == "holesky":
    print(f'Using {color("cyan")}vesting_initial_params_holesky.py{color} addresses')
    from vesting_initial_params_holesky import *
elif network.show_active() == "hoodi":
    print(f'Using {color("blue")}vesting_initial_params_hoodi.py{color} addresses')
    from vesting_initial_params_hoodi import *
else:
    print(f'Using {color("magenta")}vesting_initial_params.py{color} addresses')
    from vesting_initial_params import *


def get_common_deploy_args():
    return DotMap(
        {
            "token": TOKEN,
            "owner": OWNER,
            "manager": MANAGER,
            "aragon_voting": ARAGON_VOTING,
            "snapshot_delegation": SNAPSHOT_DELEGATION,
        }
    )


def prepare_voting_adapter_deploy_args(
    voting_addr,
    snapshot_delegate_addr,
    owner,
):
    return DotMap(
        {
            "voting_addr": voting_addr,
            "snapshot_delegate_addr": snapshot_delegate_addr,
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
