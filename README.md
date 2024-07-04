# FRESCO: Fast and Reliable Edge Offloading using Reputation-based Hybrid Smart Contract
FRESCO is a reliable and fast edge offloading framework that offloads mobile application tasks on reliable edge servers to minimize 
Quality-of-Service (QoS) violations and ensure fast offloading decisions for latency-sensitive applications.

The main components of the FRESCO framework are:

- **Reputation state manager**: It is a FRESCO system component that manages the reputation scores of edge servers. Reputation score is a belief
about edge server reliability' based on its historical performance. Reputation is used as an input for mobile devices to identify reliable edge servers
for task offloading. The reputation scores are managed on a public blockchain because of its immutability property that prevents tampering.
Tamper-proof reputation management is necessary to prevent malicious actors (e.g. users, client devices, vehicles) that want to manipulate reputation
to their advantage. Deploying reputation management on a blockchain has its limitation of long latencies due to a slow consensus mechanism.
Therefore, to avoid blockchain consensus overhead, the reputation state manager is implemented as a Hybrid Smart Contract (HSC) on a public blockchain.
The HSC is a program deployed on blockchain and it self-executes when certain conditions are met. The HSC ensures a secured reputation on-chain against
tampering while allowing fast offloading decisions off-chain to satisfy strict QoS deadlines for latency-sensitive applications.
- **Offloading decision engine**: It is a FRESCO system component that is deployed on mobile devices and computes offloading decisions. The decision-making
is calculated based on retrieved reputation score from HSC, task resource requirements, and available edge resource capacities, to satisfy application
QoS deadlines. The decision engine is implemented as Satisfiability Modulo Theory (SMT) which is a formal method that can model resources and
applications as constraints that need to be satisfied. Constraints such as reputation scores, edge server resources, and application QoS deadlines are encoded
into SMT logical formulas, and solved by the SMT solver tool through automatic logical reasoning. The output of SMT solving is an offloading decision
that formally satisfies all aforementioned constraints.

<img width="627" alt="edge_offloading_model" src="https://github.com/jzilic1991/hybrid-edge-blockchain/assets/89394269/79d97c14-5b73-43ce-969a-d9320450338e">

The reputation state manager is deployed as an HSC on the public blockchain network (step 1). HSC calculates the reputation score of an edge node based on its past and 
current performance metrics. The reputation state manager interacts with the decision engine and provides the queried reputation score (step 2). The decision engine is 
deployed on the mobile device and considers (i) diverse tasks' resource requirements, (ii) mobile devices' limited resources, (iii) heterogeneous edge infrastructure, 
(iv) edge node availability, and (v) changing infrastructure due to device mobility. These factors significantly impact application performance and QoS level. 
The offloading decision is computed based on the aforementioned factors and reputation provided by the HSC (step 2) and offloads tasks to the off-chain cluster (step 3). 
The mobile device transmits monitored performance metrics to the HSC on the blockchain, which updates the reputation score of the corresponding server (step 4). 
Steps 2-4 are cyclically repeated until application termination.

<hr>

The repository consists of the following directory elements:

- *contracts*: smart contract source code in Solidity programming language,
- *migrations*: JavaScript code for deploying smart contracts on a target blockchain network,
- *src*: edge offloading simulator which contains source code implementation in Python, data for experimental evaluation and simulation logs,
- *test*: unit tests for smart contract verification written in JavaScript,

The root project directory contains files like mnemonic.txt, package.json, and truffle-config.json. The first one is used for generating 
private keys in the Ganache blockchain emulator, the second contains metadata for NodeJS dependencies and the third one is used for managing Truffle
project for Ethereum smart contract development.

## Project pre-requisites:
- Setup Truffle smart contract project: https://archive.trufflesuite.com/
- Install Ganache blockchain emulator: https://archive.trufflesuite.com/ganache/
- Install Python for running the edge offloading simulator

## Run Ganache blockchain emulator
First, we need to run a blockchain emulator on which our edge offloading simulator will connect for reputation updates and retrieval during simulation.
Printout content of mnemonic.txt file which is necessary for maintaining the same set of Ganache private keys over different experiment runs:
cat mnemonic.txt

Pass the mnemonic.txt content as a argument to the Ganache:
ganache-cli -m "mnemonic.txt content here" --gasLimit 8000000 --port 8545 --defaultBalanceEther 1000


