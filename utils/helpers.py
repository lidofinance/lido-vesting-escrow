import os

from brownie import accounts, network

import utils.log as log
from utils.env import get_env


def get_is_live():
    return network.show_active() != "development"


def get_deployer_account():
    is_live = get_is_live()
    if is_live and "DEPLOYER" not in os.environ:
        raise EnvironmentError("Please set DEPLOYER env variable to the deployer account name")

    return loadAccount("DEPLOYER") if is_live else accounts[0]


def loadAccount(accountEnvName):
    accountId = get_env(accountEnvName)
    if not accountId:
        log.error(f"`{accountEnvName}` env not found!")
        return

    try:
        account = accounts.load(accountId)
    except FileNotFoundError:
        log.error(f"Local account with id `{accountId}` not found!")
        exit()

    log.okay(f"`{accountId}` account loaded")
    return account


def proceedPrompt():
    proceed = log.prompt_yes_no("Proceed?")
    if not proceed:
        log.error("Script stopped!")
        exit()


def pprint_map(data):
    for k, v in data.items():
        log.note(k, v)
