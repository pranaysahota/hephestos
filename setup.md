## hephestos dev setup MacOS
In shell, run each command and proceed once the previous one is success

#### Install Postgres@15
```shell
brew install postgresql@15
```

#### Update path once postgres is installed
Check your default bash file
for e.g. if .zshrc
Open .zshrc using vim or nano and add the below line in the file.
```shell
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```
Once file is saved and closed.
```sh
source ~/.zshrc
```
* Start postgres server on local using command
  ```shell
  brew services start postgresql@15
  ```
Check if you are able to access psql by running the command `psql -U postgres`
if you get an error: psql: error: connection to server on socket "/tmp/.s.PGSQL.5432" failed: FATAL:  role "postgres" does not exist
It means the postgres server was setup with your mac username as default, in that case run:
```shell
psql -U <your-mac-username>
```
This will log you into default postgres db
* Create a generic superuser:
  ```sh
  CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD '';
  ```

#### Create DB and Schema
  ```shell
  sudo psql -U postgres -c "CREATE DATABASE hephestos;"
  ```
  ```sh
  psql -U postgres -d hephestos -c "CREATE SCHEMA cross_sell;"
  ```

#### Installing python3 (skip if already installed)
```shell
brew install python@3.12
```

#### Install python requirements 
```shell
pip install -r requirements.txt
```
#### Running db migration
```shell
flask db upgrade
```
