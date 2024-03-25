# from Coman.encoder import Encode_password
# from Coman.decoder import decode_password

# pass_ = input("Please Enter Your Password:- ")
# encoded_pass = Encode_password(pass_)
# print("Encoded Password:- " + encoded_pass)
# print("Decoded Password:- " + decode_password(encoded_pass))



#SQL Connection
import pyodbc
from sqlalchemy import create_engine
import urllib
from sqlalchemy.orm import sessionmaker
from sqlalchemy import  text

params = urllib.parse.quote_plus(r'Driver={ODBC Driver 18 for SQL Server};Server=tcp:helloalfredpudb.database.windows.net,1433;Database=HelloAlfredUser;Uid=adminalfred;Pwd={Admin@hello};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine_azure = create_engine(conn_str,echo=True)
Session = sessionmaker(bind=engine_azure)
session = Session()
with engine_azure.connect() as conn:
    try:
        results = conn.execute(text("SHOW DATABASES;"))
        conn.commit()
    except Exception as e:
        print(e)