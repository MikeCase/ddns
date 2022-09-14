## What is this.
Yet another dynamic dns app for cloudflare.

## How to use.
git clone https://github.com/MikeCase/ddns
cd ddns/
python3 -m venv ~/.config/venv/ddns
source ~/.config/venv/ddns/bin/activate
pip install -r requirements.txt

edit .env-example with your specific needs and save as .env

python ddns.py

