python3 -m pip install virtualenv
python3 -m virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
./database/db.py