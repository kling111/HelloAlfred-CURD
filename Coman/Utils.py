from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import azure.functions as func
import pandas as pd
import ast
import urllib
import uuid

def createconnection():
    # TODO : Convert this to use Azure sql
    params = urllib.parse.quote_plus(r'Driver={ODBC Driver 18 for SQL Server};Server=tcp:helloalfredpudb.database.windows.net,1433;Database=HelloAlfredUser;Uid=adminalfred;Pwd={Admin@hello};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
    engine = create_engine(conn_str,echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session,engine
    # conn_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:sqldemotrial.database.windows.net,1433;Database=hemang_trial;Uid=admin1hemang;Pwd=admin@3210;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

def parse_header(req: func.HttpRequest):
    req_body_bytes = req.get_body()
    req_body = req_body_bytes.decode("utf-8")
    req_body = ast.literal_eval(req_body)
    return req_body

def patient_id_generator(req_body):  
    return str(uuid.uuid4())[:18]   