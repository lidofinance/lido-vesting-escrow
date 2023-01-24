from brownie import VestingEscrow, VestingEscrowFactory, VotingAdapter

import utils.log as log
from utils.deployed_state import read_or_update_state


def do_deploy_escrow(tx_params):
    deployedState = read_or_update_state()

    if deployedState.vestingEscrowAddress:
        escrow_simple = VestingEscrow.at(deployedState.vestingEscrowAddress)
        log.warn("VestingEscrow already deployed at", deployedState.vestingEscrowAddress)
    else:
        log.info("Deploying VestingEscrow...")
        escrow_simple = VestingEscrow.deploy(tx_params)
        log.info("> txHash:", escrow_simple.tx.txid)

        deployedState = read_or_update_state(
            {
                "vestingEscrowDeployer": tx_params["from"].address,
                "vestingEscrowDeployTx": escrow_simple.tx.txid,
                "vestingEscrowAddress": escrow_simple.address,
            }
        )
        log.okay("VestingEscrow deployed at", escrow_simple.address)

        log.info("Checking deployed VestingEscrow...")
        check_deployed_vesting_simple(escrow_simple)
        log.okay("VestingEscrow check pass")

    return escrow_simple


def check_deployed_vesting_simple(escrow_simple):
    assert escrow_simple.initialized(), "VestingEscrow implementation state initialized is not True"


def do_deploy_voting_adapter(tx_params, deploy_args):
    deployedState = read_or_update_state()

    if deployedState.votingAdapterAddress:
        voting_adapter = VotingAdapter.at(deployedState.votingAdapterAddress)
        log.warn("VotingAdapter already deployed at", deployedState.votingAdapterAddress)
    else:
        log.info("Deploying VotingAdapter...")
        voting_adapter = VotingAdapter.deploy(
            deploy_args.voting_addr,
            deploy_args.snapshot_delegate_addr,
            deploy_args.delegation_addr,
            deploy_args.owner,
            tx_params,
        )
        log.info("> txHash:", voting_adapter.tx.txid)

        deployedState = read_or_update_state(
            {
                "votingAdapterDeployer": tx_params["from"].address,
                "votingAdapterDeployTx": voting_adapter.tx.txid,
                "votingAdapterAddress": voting_adapter.address,
                "votingAdapterDeployConstructorArgs": deploy_args.toDict(),
            }
        )
        log.okay("VotingAdapter deployed at", voting_adapter.address)

        log.info("Checking deployed VotingAdapter...")
        check_deployed_voting_adapter(voting_adapter, deploy_args)
        log.okay("VotingAdapter check pass")

    return voting_adapter


def check_deployed_voting_adapter(voting_adapter, deploy_args):
    assert voting_adapter.voting_contract_addr() == deploy_args.voting_addr, "Invalid aragon voting address"
    assert (
        voting_adapter.snapshot_delegate_contract_addr() == deploy_args.snapshot_delegate_addr
    ), "Invalid snapshot delegation address"
    assert voting_adapter.delegation_contract_addr() == deploy_args.delegation_addr, "Invalid aragon delegation address"


def do_deploy_factory(tx_params, deploy_args):
    deployedState = read_or_update_state()

    if deployedState.factoryAddress:
        factory = VestingEscrowFactory.at(deployedState.factoryAddress)
        log.warn("VestingEscrowFactory already deployed at", deployedState.factoryAddress)
    else:
        log.info("Deploying VestingEscrowFactory...")
        factory = VestingEscrowFactory.deploy(
            deploy_args.target,
            deploy_args.token,
            deploy_args.owner,
            deploy_args.manager,
            deploy_args.voting_adapter,
            tx_params,
        )
        log.info("> txHash:", factory.tx.txid)
        deployedState = read_or_update_state(
            {
                "factoryDeployer": tx_params["from"].address,
                "factoryDeployTx": factory.tx.txid,
                "factoryAddress": factory.address,
                "factoryDeployConstructorArgs": deploy_args.toDict(),
            }
        )
        log.okay("VestingEscrowFactory deployed at", factory.address)

        log.info("Checking deployed VestingEscrowFactory...")
        check_deployed_factory(factory, deploy_args)
        log.okay("VestingEscrowFactory check pass")

    return factory


def check_deployed_factory(factory, deploy_args):
    assert factory.target() == deploy_args.target, "Invalid target"
    assert factory.token() == deploy_args.token, "Invalid vesting token"
    assert factory.voting_adapter() == deploy_args.voting_adapter, "Invalid voting_adapter"
    assert factory.owner() == deploy_args.owner, "Invalid owner"
    assert factory.manager() == deploy_args.manager, "Invalid manager"
