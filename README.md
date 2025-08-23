# Anonymous-Access-Dissertation
A project that utilises ZKPs and selective disclosure to create proofs that can be used to login into a (Therapy) service.

This project has two stages:

1. Where you use ZKP to produce a multi-show credential that can be used to login into a service.
2. An emulation of a therapy service that can be logged in using a ZKP credential hosted over Tor

Each part will operate in the respective order and will require some setup.
Each part also has its own set of requirements and the scripts within will help you setup, this readme simply contains an overview of the project, the prerequisites of the project and simple instructions on how to setup the project on windows/linux/macos machines.


ZKP_Software **

Prerequisites:
1. Circom -> Run ZK circuits
2. Snarkjs -> Proof creation and verification

macOs & Linux:
```bash
# Install Node.js (Recommended: via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install node

# Install Circom (Current mainstream version: 2.x)
git clone https://github.com/iden3/circom.git
cd circom
cargo build --release
sudo ln -s $(pwd)/target/release/circom /usr/local/bin/circom

#  Install SnarkJS
npm install -g snarkjs
```

You will also need to setup a separate virtual environment for this part of the project, which can be done by simply running the setup script.

Instructions**

1. First ensure you have the prerequisites installed.
2. Next run the setup script which will create and activate your virtual environment, build the the submodule within (ffi-bbs-signatures: https://github.com/mattrglobal/ffi-bbs-signatures.git) and add the dynamic library needed for the project to run. Also it will pip install many dependencies that the project requires (please look at the requirements file within the ZKP_Software folder.)
3. Lastly, use the run script to run this part of the project and follow the prompts on the command line.

Therapy Platform**

Prerequisites:

1. Tor and Tor browser

macOs:
 ```bash
 brew install tor
 ```
    (assuming your have homebrew, otherwise you can look up to see how to install Tor on your mac).

Windows:


Linux:


To download Tor browser simply search it on your current browser and install it.


To run this project you will need to install "Hyperledger Ursa BBS Signatures Wrapper for Python".

Then the following steps using yarn (package manager):

yarn install --frozen-lockfile

yarn build

Setup a virtual environment:

python3 -m venv .venv

source .venv/bin/activate           

Pip install the dependency:

python3 -m pip install ffi-bbs-signatures/wrappers/python


This essentially sets up the virtual environment and installs the dependencies for bbs+ to be able to run in python,
provided by https://github.com/mattrglobal/ffi-bbs-signatures.git

# Clone the repo
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate   # On Linux/Mac
# OR
.venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt
