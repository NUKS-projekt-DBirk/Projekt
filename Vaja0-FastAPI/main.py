from fastapi import FastAPI, HTTPException, status
from fastapi_versioning import version, VersionedFastAPI
##

##
import shemas
from sqlalchemy.orm import Session

from database import Base, engine, ToDO

Base.metadata.create_all(engine)

app = FastAPI()  #app instance



@app.get("/")
def read_root():
    """
    Default API call
    """
    return "TODO app"
#_______________________________________________________
@app.post("/add", status_code=status.HTTP_201_CREATED)
@version(2)
def create_todo(todo: shemas.ToDoTask):
    session = Session(bind = engine, expire_on_commit=False)
    tododb = ToDO(task= todo.task)
    
    session.add(tododb)
    session.commit()
    id = tododb.id
    session.close()

    return f"Created new todo with id: {id}"
#_______________________________________________________
@app.get("/get/{id}")
@version(1)
def read_todo(id: int):
    return "read TODO"

############################## v2 Get APIja##
@app.get("/get/{id}")
@version(2)
def read_todo(id: int):
    session = Session(bind=engine, expire_on_commit=False)
    tododb = session.query(ToDO).filter_by(id=id).first()
    session.close()
    
    if not tododb:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")
    
    return tododb.task
#_______________________________________________________
@app.put("/change/{id}")
@version(2)
def change_todo(id: int, new_task: str):
    session = Session(bind=engine, expire_on_commit=False)
    tododb = session.query(ToDO).filter_by(id=id).first()
    
    if not tododb:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")
    
    tododb.task = new_task
    session.commit()
    session.close()
    
    return f"Changed task of todo item with id {id} to '{new_task}'"
#_______________________________________________________
@app.delete("/delete/{id}")
@version(2)
def delete_todo(id: int):
    session = Session(bind=engine, expire_on_commit=False)
    tododb = session.query(ToDO).filter_by(id=id).first()
    
    if not tododb:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")
    
    session.delete(tododb)
    session.commit()
    session.close()
    
    return f"Deleted todo item with id {id}"
#_______________________________________________________
@app.get("/list")
@version(2)
def read_todo_list():
    session = Session(bind=engine, expire_on_commit=False)
    tododb_list = session.query(ToDO).all()
    session.close()
    
    return [{"id": todo.id, "task": todo.task} for todo in tododb_list]
#_______________________________________________________
###########################################################
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()  

@app.post("/send-email")
@version(2)
def send_email(to_email: str):
    session = Session(bind=engine, expire_on_commit=False)
    tododb_list = session.query(ToDO).all()
    session.close()
    todos = [{"id": todo.id, "task": todo.task} for todo in tododb_list]
    todos_text = "\n".join([f"{todo['id']}: {todo['task']}" for todo in todos])
    
    msg = EmailMessage()
    msg.set_content(todos_text)
    msg['Subject'] = 'TODO List'
    msg['From'] = os.getenv("EMAIL_USERNAME") # replace with the email address you want to send from
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP('smtp.office365.com', 587) as smtp:  # replace with your email provider's SMTP settings
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(os.getenv("EMAIL_USERNAME"), os.getenv("EMAIL_PASSWORD"))  # replace with your email address and password
            smtp.send_message(msg)
            return f"TODO list sent to {to_email}"
    except Exception as e:
        print(e.message)
        return "Failed to send email"
    
############################################################
app = VersionedFastAPI(app, version_format="{major}", prefix_format="/v{major}")
