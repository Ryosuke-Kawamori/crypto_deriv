# crypto_deriv

# Initial Setup
  ```angular2html
  cd {Directory for repository}
  git clone {repository URL}
  ```
  Edit docker-compose file for your Ubuntu server
  `/home/rkawamori/Asobi/crypto_deriv:/home/` -> `{Directory for repository}/crypto_deriv:/home/`
  
  Edit .env file to use private API.  
  https://www.bybit.com/future-activity/ja-JP/developer
  ```angular2html
  TOKEN = YOUR_DISCORD_BOT_TOKEN
  SSL_CERT_DIR=/etc/ssl/certs
  BYBIT_APIKEY=YOUR_BYBIT_APIKEY
  BYBIT_SECRET=YOUR_BYBIT_SECRET
  ```

# How to Run bot and notebook

### Bot
  ```angular2html
  cd {Directory for repository}
  docker-compose up -d
  docker-compose exec bot bash
  ```
  You are now inside container for bot
  ```angular2html
  cd /home/bot
  python3.9 ivbot.py # Now Bot is Working!
  ```

### Notebook
  ```
  docker-compose exec jupyter bash  
  jupyter-lab --ip=0.0.0.0 --allow-root --port=8890
  ```
  Paste the URL output to your browser.
  `http://{your server URL}:8890/lab?token=XXXXXXX`  
  Now you can enjoy your crypto anlysis on your browser.
  