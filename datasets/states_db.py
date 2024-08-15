#libs
from typing import Optional
from sqlalchemy.orm import sessionmaker
#database
from datasets.tables import SQLStateStorage
from datasets.database import Session
#utils
from baselogs.custom_decorators import log_exceptions
from baselogs.custom_logger import create_logger


logger = create_logger('StatesDb')






