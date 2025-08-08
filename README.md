# Anonymous-Access-Dissertation
A project that utilises ZKPs and selective disclosure to create proofs that can be used to login into a service.

Instructions**

To run this project you will need to install "Hyperledger Ursa BBS Signatures Wrapper for Python".

To do this first clone the repository

git clone https://github.com/mattrglobal/ffi-bbs-signatures.git

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
