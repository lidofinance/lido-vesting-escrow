from brownie import network, VestingEscrow, VestingEscrowFactory, VotingAdapter

import utils.log as log
from scripts.deploy import (
    do_deploy_factory,
    do_deploy_voting_adapter,
    do_deploy_escrow,
)
from utils.config import get_common_deploy_args, prepare_voting_adapter_deploy_args, prepare_factory_deploy_args
from utils.env import get_env
from utils.helpers import get_deployer_account, proceedPrompt, pprint_map

# environment
WEB3_INFURA_PROJECT_ID = get_env("WEB3_INFURA_PROJECT_ID")
ETHERSCAN_TOKEN = get_env("ETHERSCAN_TOKEN")


def check_env():
    if not WEB3_INFURA_PROJECT_ID:
        log.error("`WEB3_INFURA_PROJECT_ID` env not found!")
        exit()

    if not ETHERSCAN_TOKEN:
        log.error("`ETHERSCAN_TOKEN` env not found!")
        exit()

    log.okay("Environment variables checked")


def deploy_factory():
    log.info("-= VestingEscrowFactory deploy =-")
    log.info("This script will deploy VestingEscrowFactory and all necessary contracts")

    check_env()
    deployer = get_deployer_account()

    log.note("NETWORK", network.show_active())
    log.note("DEPLOYER", deployer.address)

    deploy_args = get_common_deploy_args()

    log.info("> commonDeployArgs:")
    pprint_map(deploy_args)

    proceedPrompt()

    log.note(f"VestingEscrow deploy")
    escrow = do_deploy_escrow({"from": deployer})

    log.note(f"VotingAdapter deploy")
    voting_adapter_args = prepare_voting_adapter_deploy_args(
        voting_addr=deploy_args.aragon_voting,
        snapshot_delegate_addr=deploy_args.snapshot_delegation,
        delegation_addr=deploy_args.delegation,
        owner=deploy_args.owner,
    )

    proceedPrompt()

    log.info("> VotingAdapterDeployArgs:")
    pprint_map(voting_adapter_args)
    voting_adapter = do_deploy_voting_adapter({"from": deployer}, voting_adapter_args)

    log.note(f"VestingEscrowFactory deploy")
    factory_args = prepare_factory_deploy_args(
        target=escrow.address,
        token=deploy_args.token,
        owner=deploy_args.owner,
        manager=deploy_args.manager,
        voting_adapter=voting_adapter.address,
    )
    log.info("> VotingAdapterDeployArgs:")
    pprint_map(factory_args)

    proceedPrompt()

    factory = do_deploy_factory({"from": deployer}, factory_args)

    if network.show_active() == "mainnet":
        proceed = log.prompt_yes_no("(Re)Try to publish source codes?")
        if proceed:
            VestingEscrowFactory.publish_source(factory)
            VestingEscrow.publish_source(simple_escrow)
            VestingEscrowFullyRevokable.publish_source(revokable_escrow)
            VotingAdapter.publish_source(voting_adapter)
            log.okay("Contract source published!")
    else:
        log.info(f"The current network '{network.show_active()}' is not 'mainnet'. Source publication skipped")

    log.note("All deployed metadata saved to", f"./deployed-{network.show_active()}.json")


def deploy_vestings():
    log.error("use brownie run build_multisig_tx instead")
