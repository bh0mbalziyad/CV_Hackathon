from flask import Flask, render_template, request, session
import pickle
from jdExtraction import jdExtraction
from resumeExtraction import ResumeExtraction
import requests
import os
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import sys, fitz

def allowedExtension(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ['docx','pdf']

jdextractorObj = pickle.load(open("jdExtraction.pkl","rb"))
resumeExtractionObj = pickle.load(open("resumeExtraction.pkl","rb"))
app = Flask(__name__)
UPLOAD_FOLDER = 'static/JD'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

app.secret_key = "Resume_screening"
app.config['MONGO_URI'] = "mongodb+srv://userpratik:RyuMongo$99@resumeanalytics.cf3os.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
mongo = PyMongo(app)
dbJD = mongo.db.JD
dbResume = mongo.db.dbResume


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploadJD", methods=['POST'])
def uploadJD():
    try:
        file = request.files['jd']
        filename = secure_filename(file.filename)
        print("Extension:",file.filename.rsplit('.',1)[1].lower())
        if file and allowedExtension(file.filename):
             file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
             fetchedData=jdextractorObj.extractorData("static/JD/"+filename,file.filename.rsplit('.',1)[1].lower())
             print(fetchedData[0])
             result = None
             result1 = dbJD.insert_one({"Skills":list(fetchedData[0]),"Education":fetchedData[1],"JD_Data":fetchedData[2]}).inserted_id
             if result1 == None:
                return render_template("StartFind.html",successMsg="Problem in Data Storage")
             else:
                session['jd_id'] = str(result1)
                return render_template("StartFind.html",successMsg="Job Description Uploaded!!")
    except:
        print("Exception Occured")

@app.route("/scanResume")
def scanResume():
    
    data = resumeExtractionObj.extractorData('Resumes/Resume1.pdf',"pdf")
    se=dbJD.find_one({"_id":ObjectId(session['jd_id'])},{"Skills":1,"Education":1,"JD_Data":1})
    
    return "<h1>Hello</h1>"

if __name__=="__main__":
    app.run(debug=True)