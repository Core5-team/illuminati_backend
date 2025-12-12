import requests, json
from coverage.debug import info_header
from .models import EntryPassword
from rest_framework.response import Response
from django.db import connection
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def save_new_entry_password(password):
    logging.info("Detected new changes for entry password")
    logging.info("New entry password received: %s", password)
    old_password = EntryPassword.objects.filter().first()
    query = """
        UPDATE entry_password
        SET 
            entry_password = %s, 
            last_updated = %s
        WHERE id = %s;
    """
    params = [password,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),old_password.id]
    
    with connection.cursor() as cursor:
        cursor.execute(query,params)

    logging.info("entry password updated: %s", type(datetime.now().strftime("%Y-%m-%d %H:%M")))

