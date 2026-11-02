#!/bin/bash
# Runs once, as root, on the VM's first boot. Its output goes to /var/log/cloud-init-output.log
export HOME=/root                     # npm needs a home folder; cloud-init may not set one
export PATH=$PATH:/snap/bin           # where snap puts node and npm

# 1. Swap space: a t2.micro has 1 GB of RAM, too little for the React build
fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile

# 2. System packages: Python's venv tool, and the nginx web server (it starts on port 80 by itself)
apt-get update -y
apt-get install -y python3.14-venv nginx

# 3. Node.js 22, to build the front-end
snap install node --classic --channel=22

# 4. Get the code
cd /opt
git clone https://github.com/JC2244/crud-app.git app

# 5. Backend: its own venv, its packages, then uvicorn on port ${backend_port} in the background
python3.14 -m venv /opt/venv
/opt/venv/bin/pip install -r /opt/app/crud-app/backend/requirements.txt
cd /opt/app/crud-app/backend
/opt/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${backend_port} > /opt/uvicorn.log 2>&1 &

# 6. Front-end: build it, then let nginx serve the built files on port 80
cd /opt/app/frontend
npm install
GENERATE_SOURCEMAP=false npm run build && rm -rf /var/www/html/* && cp -r build/* /var/www/html/
