import json
import os
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache
from fastapi import APIRouter, FastAPI, HTTPException, Request, Depends
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Set
import json

from db_engine import engine, get_db

router = APIRouter()
