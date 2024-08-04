## hephestos dev setup MacOS
In shell, run each command and proceed once the previous one is runs successfully

1. Install Postgres@15

```shell
brew install postgresql@15
```

2. Update path once postgres is installed

```shell
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

Check if you are able to access psql by running the command `psql -U postgres`

3. Setup DB

```shell
sudo -u postgres psql -c "CREATE DATABASE cross_sell;"
```

4. Install python

```shell
brew install python@3.12
```

5. Install requirements 

```shell
pip install -r requirements.txt
```
6. Run db migration
```shell
flask db upgrade
```