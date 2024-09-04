import urllib.parse

host = "localhost"
port = "3306"
username = "root"
password = ""
database = "akshare"

_dialect = "mysql"
_driver = "pymysql"
mysql_url = f"{_dialect}+{_driver}://{username}:{urllib.parse.quote_plus(password)}@{host}:{port}/{database}"
tushare_token = "09bc9aa347e21a71a3c94fbcf0b6244276ff5dcc27e9e54328950d2c"
