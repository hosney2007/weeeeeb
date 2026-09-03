from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

csrf = CSRFProtect()
mail=Mail()
db = SQLAlchemy()
login_manager = LoginManager()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)
