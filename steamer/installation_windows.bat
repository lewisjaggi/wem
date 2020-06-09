python -m pip install virtualenv
python -m virtualenv .env
call .env\Scripts\activate.bat
pip install -r requirements.txt
python database\db.py