# Lido Vesting Escrow

A deeply modified version of [Yearn Vesting Escrow](https://github.com/banteg/yearn-vesting-escrow) contracts with added functionality:
- `rug_pull` method is renamed to `revoke_unvested`
- `admin` role is renamed to `manager`
- Added new role `owner`
- Added new escrow method `revoke_all` method that allows `owner` to revoke ALL tokens form escrow. This is required for legal optimization (in terms of legal token ownership) 
- Added methods:
    - `aragon_vote` method for Aragon voting participation
    - `snapshot_set_delegate` method for Snapshot voting delegation,
    - `delegate` method for further voting power delegation 
    
- Voting methods operate over upgradable middleware to encounter possible changes in voting interfaces
- Added `recover_erc20` and `recover_ether` methods
- Existing methods and events refined

## Contracts

- [`VestingEscrowFactory`](contracts/VestingEscrowFactory.vy): Factory to deploy many simplified vesting contracts
- [`VestingEscrow`](contracts/VestingEscrow.vy): Simplified vesting contract that holds tokens for a single beneficiary
- [`VotingAdapter`](contracts/VotingAdapter.vy): Middleware for voting with tokens under vesting

## Setup

```shell
poetry shell
poetry install

export WEB3_INFURA_PROJECT_ID=<your infura project id>
export ETHERSCAN_TOKEN=<your etherscan api key>
```

## Configuration

The default deployment parameters are set in [`vesting_initial_params.py`]. The following parameters are can be set:

- `TOKEN` address of the token to be vested with the deployed vesting contracts

- `OWNER` address that will be assigned as an owner of the factory and all deployed vestings

- `MANAGER` address that will be assigned as a manager of all deployed vestings

- `ARAGON_VOTING` address of the Lido Aragon voting contract

- `SNAPSHOT_DELEGATION` address of the snapshot voting contract

- `DELEGATION` address of the voting delegation contract. Not implemented ATM we recommend using `0x0000000000000000000000000000000000000000` now

Example content of `vesting_initial_params.py`:

```py
# LDO
TOKEN = "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32"

# Lido Agent
OWNER = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c"

# TRP committee multisig
MANAGER = "0x0000000000000000000000000000000000000000"

# Lido Aragon voting
ARAGON_VOTING = "0x2e59A20f205bB85a89C53f1936454680651E618e"

# Snapshot delegating contract
SNAPSHOT_DELEGATION = "0x469788fE6E9E9681C6ebF3bF78e7Fd26Fc015446"

# Voting delegation contract address. ZERO for now
DELEGATION = "0x0000000000000000000000000000000000000000"
```

## Run tests

It' better to run local mainnet fork node in separate terminal window.

```shell
brownie console --network mainnet-fork
```

Then run all tests

```shell
brownie test -s --disable-warnings
```

### Run tests against mainnet deployed setup

Add `owner` and `manager` accounts to the `brownie-config.yaml`

```yaml
networks:
    mainnet-fork:
        cmd_settings:
            unlock: # accounts order is crucial!
                - 0xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX # manager
                - 0xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX # owner
```
 
Run tests on the `mainnet-fork` forked after deploy

```shell
brownie test --network mainnet-fork --deploy-json deployed-mainnet.json -m "not no_deploy"
```

> Note: Not all tests will be executed (ex. Vote tests will be excluded)

## Deployment

Make sure your account is imported to Brownie: `brownie accounts list`.

Make sure you have exported or set id directly:

```yaml
DEPLOYER=deployer # deployer account alias
```

To deploy `VestingEscrowFactory` and all supplementary contracts run deploy script and follow the wizard:

```shell
DEPLOYER=deployer brownie run --network mainnet main deploy_factory
```

Deploy of the `VestingEscrow` and VestingEscrowFullyRevokable is permissionless, any account can deploy fund vesting escrow.

After script finishes, all deployed metadata will be saved to file `./deployed-{NETWORK}.json`, i.e. `deployed-mainnet.json`.

Deploy script is stateful, so it safe to start several times. To deploy from scratch, simply delete the `./deployed-{NETWORK}.json` before running it.

