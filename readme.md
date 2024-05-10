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

## Audits

Source code of the smart contracts was audited by:
- [statemind.io](./audits/lido-trp-vesting-escrow.pdf)

## Setup

```shell
pip install poetry==1.3.1
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
MANAGER = "0x834560F580764Bc2e0B16925F8bF229bb00cB759"

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

## Multisig TX preparation for vestings deploy

Compile the CSV list of vestings params with the [structure](input.csv.example)
```
amount,recipient,vesting_duration,vesting_start,cliff_length,is_fully_revokable
42_000_000_000_000_000_000,0x0000000000000000000000000000000000000001,144,1672480800,24,1
1_000_000_000_000_000_000,0x0000000000000000000000000000000000000002,144,1672308000,24,0
```

Add `FACTORY_ADDRESS` environment variable by running
```
export FACTORY_ADDRESS=%VestingEscrowFactory address%
```

Add `SAFE_ADDRESS` environment variable by running

```bash
export SAFE_ADDRESS=%TRP Safe Multisig address%
```

Make sure you have installed [frame.sh](http://frame.sh) wallet with configured Ledger hardware signer.

Run command to build and send proposed transaction to Gnosis backend, replacing %input.csv% with the path to the given round CSV:

```bash
brownie run multisig_tx build %input.csv% prod!
```

If you want to use a different nonce, e.g. for replacing a transaction, provide it as the last argument:

```bash
brownie run multisig_tx build %input.csv% prod! 42
```

Follow the script questions

Get SafeTX hash from Gnosis UI or the previous step.


Run the following command replacing `%safe-tx-hash%` and `%round-input.csv%` with actual values:

```bash
brownie run multisig_tx check %safe-tx-hash% %round-input.csv%
```
