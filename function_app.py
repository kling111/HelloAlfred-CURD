import azure.functions as func
from sqlalchemy import  text
import logging
from datetime import datetime
from Coman.Datamodel import UserData, PatientDetails
from Coman.encoder import Encode_password, verify_password
from Coman.Utils import parse_header, createconnection, patient_id_generator

app = func.FunctionApp()

# Create Operation - C of CURD
@app.route(route="create_account", auth_level=func.AuthLevel.FUNCTION)
def Account_Creation(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Received New Request For Account Creation')
    req_body = parse_header(req)
    required_fields = ["username","email","dob","gender","mobile","rtype","education","ssn","insuranceurl","password"]
    if not all(key_ in req_body for key_ in required_fields):
        missing_fields = set(required_fields) - set(req_body.keys())
        return func.HttpResponse(f"Missing Fields :- [ {', '.join(map(str, missing_fields))} ] in the body.", status_code=400)
    req_body["dob"] = datetime.strptime(req_body["dob"], "%Y-%m-%d")
    tp,main_ = Encode_password(req_body["password"])
    print(main_[0],main_[1])
    req_body["salt"],req_body["password"] = main_[0],main_[1]
    try:
        session,engine = createconnection()
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT patient_id,activestat FROM patient_details WHERE email='{req_body['email']}'"))
            for row in result:
                if row[1] == 1:
                    return func.HttpResponse("Account with this email already exist. Please try another email",202)
        patient_id = patient_id_generator(req_body)
        user_data = UserData(
            patient_id=patient_id,
            salt = str(req_body["salt"]),
            password = req_body["password"]
        )
        patient_details = PatientDetails(
            patient_id = patient_id,
            username = req_body["username"],
            email = req_body["email"],
            dob = req_body["dob"],
            gender = req_body["gender"],
            mobile = req_body["mobile"],
            rtype = req_body["rtype"],
            education = req_body["education"],
            ssn = req_body["ssn"],
            insuranceurl = req_body["insuranceurl"],
            activestat = 1
        )
        session.add(user_data)
        session.add(patient_details)
        session.commit()
        session.close()
    except Exception as e:
        return func.HttpResponse("Failed to add data to sql database :- " + str(e))
    return func.HttpResponse("Account Created Successfully! Thank You", status_code=200)

# Update Operation - U of CURD
@app.route(route="update_details", auth_level=func.AuthLevel.FUNCTION)
def Update_User_Details(req: func.HttpRequest):
    req_body = parse_header(req)
    if "email" not in req_body.keys():
        return func.HttpResponse("Email is compulsory for updating details.", status_code=400)
    if len(req_body) == 1:
        return func.HttpResponse("No Parameters found to update",status_code=200)
    main_query = "UPDATE patient_details SET"
    cn = 0
    for key_ in req_body.keys():
        if key_ == "email":
            continue
        if cn != 0:
            main_query += " ,"
        main_query += f" {key_} = '{req_body[key_]}'"
        cn += 1
    main_query += f" WHERE email = '{req_body['email']}';"
    session, engine = createconnection()
    with engine.connect() as conn:
        try:
            results = conn.execute(text(main_query))
            conn.commit()
        except Exception as e:
            return func.HttpResponse("Code failed with:- " + str(e),status_code=400)
    return func.HttpResponse("Details Updated Succefully.",status_code=200)

# Read Operation - R of CURD
@app.route(route="show_accounts", auth_level=func.AuthLevel.FUNCTION)
def Current_User_Details(req: func.HttpRequest):
    try:    
        req_body = parse_header(req)
    except:
        req_body = {}
    if "password" in req_body.keys():
        return func.HttpResponse("Can not view accounts on the basis of Password.")
    main_query = "SELECT * FROM patient_details"
    if len(req_body) > 0:
        for cn, key_ in enumerate(req_body.keys()):
            if cn == 0:
                if key_ == 'activestat':
                    main_query += f" WHERE {key_} = {req_body[key_]}"
                    continue
                main_query += f" WHERE {key_} = '{req_body[key_]}'"
                continue
            if key_ == 'activestat':
                main_query += f" AND {key_} = {req_body[key_]}"
                continue
            main_query += f" AND {key_} = '{req_body[key_]}'"
    main_query += ";"
    session, engine = createconnection()
    out = []
    with engine.connect() as conn:
        results = conn.execute(text(main_query))
        for row in results:
            out.append(row)
    return str(out)

# Delete Operation - D of CURD
@app.route(route="delete_account", auth_level=func.AuthLevel.FUNCTION)
def Delete_User(req: func.HttpRequest):
    req_body = parse_header(req)
    if "email" not in req_body.keys():
        return func.HttpResponse("Email is compulsory for updating details.", status_code=400)
    checker_query = f"SELECT username FROM patient_details WHERE email='{req_body['email']}';"
    main_query = f"UPDATE patient_details SET activestat = 0 WHERE email = '{req_body['email']}'";
    session, engine = createconnection()
    try:
        with engine.connect() as conn:
            results = conn.execute(text(checker_query))
            count = 0
            for val in results:
                count+=1
            if count != 0:
                result = conn.execute(text(main_query))
                conn.commit()
            else:
                return func.HttpResponse("User Account with email :- " + req_body["email"] + " Does not exsist",status_code=200)
    except Exception as e:
         return func.HttpResponse("Code failed with:- " + str(e),status_code=400)
    return func.HttpResponse("User Account Deleted Successfully. Thank You")

# Login Operation for User
@app.route(route="login_account", auth_level=func.AuthLevel.FUNCTION)
def User_Login(req: func.HttpRequest):
    req_body = parse_header(req)
    if "@" in req_body["Username"]:
        query = f"SELECT patient_id from patient_details WHERE email = '{req_body['Username']}' AND activestat = 1"
        
        session, engine = createconnection()
        try:
            with engine.connect() as conn:
                results = conn.execute(text(query))
                for row in results:
                    user_query = f"SELECT salt,password from user_data WHERE patient_id = '{row[0]}'"
                    result = conn.execute(text(user_query))
                    for main in result:
                        print(main)
                        if verify_password(req_body["Password"],main[0],main[1]):
                            return func.HttpResponse("User authenticated succesfully!")
                        else:
                            return func.HttpResponse("Incorrect password or Incorrect Username",status_code=203)
                return func.HttpResponse("Incorrect email-Id or user not registered.")
        except Exception as e:
            return func.HttpResponse("The Process of logging in failed with:- " + str(e),status_code=400)
    else:
        query = f"SELECT password from user_data WHERE mobile = '{req_body['Username']}'"
        session, engine = createconnection()
        try:
            with engine.connect() as conn:
                results = conn.execute(text(query))
                for row in results:
                    if verify_password(req_body["Password"]):
                        return func.HttpResponse("User authenticated succesfully!")
                    else:
                        return func.HttpResponse("Incorrect password or Incorrect Username",status_code=203)
            return func.HttpResponse("Incorrect email-Id or user not registered.")
        except Exception as e:
            return func.HttpResponse("The Process of logging in failed with:- " + str(e),status_code=400)
        
        
    
# Symptoms adder for user
@app.route(route="add_symptoms", auth_level=func.AuthLevel.FUNCTION)
def sym_adder(req: func.HttpRequest):
    req_body = parse_header(req)
    if ("email" in req_body.keys()) or ("mobile" in req_body.keys()):
        #INSERT INTO patient_symp (tdate, patient_id, weight, height, bloodP, pulse, timestamp, vitals)
        # SELECT '2024-03-20', pd.patient_id, 70, 170, 120, 80, NOW(), 'Normal'
        # FROM patient_details pd
        # WHERE pd.email = 'john@example.com';
        query = f"INSERT INTO patient_symp (tdate, patient_id, weight, height, bloodP, pulse, timestamp, vitals) " \
                f"SELECT '{req_body['today_date']}', pd.patient_id, {req_body['weight']}, {req_body['height']}, " \
                f"{req_body['bloodP']}, {req_body['pulse']}, '{req_body['timestamp']}', '{req_body['vitals']}' " \
                f"FROM patient_details pd WHERE pd.email = '{req_body['email']}'"
        session,engine = createconnection()
        with engine.connect() as conn:
            result = conn.execute(text(query))
            conn.commit()
            print(result)
        return func.HttpResponse("The Symptoms for :- " + str(req_body['timestamp']) + " Were noted successfully", status_code=200)
    else:
        return func.HttpResponse("Email or Phone-Number is required")