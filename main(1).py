from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
  current_dir, 'calibrationOfTools.sqlite3')
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Form(db.Model):
  __tablename__ = 'form_data'
  id = db.Column(db.Integer,
                 autoincrement=True,
                 primary_key=True,
                 nullable=False)
  plantName = db.Column(db.String)
  areaName = db.Column(db.String)
  partType = db.Column(db.String)
  partName = db.Column(db.String)
  partUniqueNumber = db.Column(db.String)
  calibarationDate = db.Column(db.String)
  nextCalibarationDate = db.Column(db.String)
  reminderInDays = db.Column(db.String)
  remarks = db.Column(db.String)
  dateOfEntry = db.Column(db.String)


# get post put delete C R U D
@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == "GET":
    return render_template('index.html')
  elif request.method == "POST":
    plantName = request.form["plantName"]
    areaName = request.form["areaName"]
    partType = request.form["partType"]
    partName = request.form["partName"]
    partUniqueNumber = request.form["partUniqueNumber"]
    calibarationDate = request.form["calibarationDate"]
    nextCalibarationDate = request.form['nextCalibarationDate']
    reminderInDays = request.form["reminderInDays"]
    remarks = request.form['remarks']
    ls = [
      plantName, areaName, partType, partName, partUniqueNumber,
      calibarationDate, nextCalibarationDate, reminderInDays, remarks
    ]
    #print(ls)
    add_data(ls)
    return redirect(url_for('home'))


def add_data(new_data):
  new_record = Form(plantName=new_data[0],
                    areaName=new_data[1],
                    partType=new_data[2],
                    partName=new_data[3],
                    partUniqueNumber=new_data[4],
                    calibarationDate=new_data[5],
                    nextCalibarationDate=new_data[6],
                    reminderInDays=int(new_data[7]),
                    remarks=new_data[8],
                    dateOfEntry=datetime.today())
  #print(new_record)
  db.session.add(new_record)
  db.session.commit()


def updateDateAgain():
  forms = Form.query.all()
  for form in forms:
    c_date = form.nextcalibrationDate
    rem_days = form.reminderIndDays
    date_today = datetime(2023, 9, 10)
    days_passed = (date_today - c_date.date()).days
    remaining_days = rem_days - days_passed
    form.reminderInDays = remaining_days
    db.session.commit()
    print(c_date)
    print(remaining_days)
  pass


def updateDateFinal():
  forms = Form.query.all()
  for form in forms:
    nextCalDate = form.nextCalibarationDate
    nextCalDate = datetime.strptime(nextCalDate, "%d-%m-%Y")
    reminderInDays = form.reminderInDays
    reminderInDays = timedelta(days=int(reminderInDays))
    dateToStartSubract = nextCalDate - reminderInDays
    todayDate = datetime.strptime(date.today().strftime("%d-%m-%Y"),
                                  "%d-%m-%Y")
    daysPassed = todayDate - dateToStartSubract
    daysLeft = reminderInDays - daysPassed
    daysLeft = int(str(daysLeft).replace("days, 0:00:00", ""))
    if (int(form.reminderInDays) >= daysLeft):
      form.reminderInDays = daysLeft
    if (int(form.reminderInDays) <= 0):
      form.reminderInDays = 0
    db.session.commit()
    print(int(daysLeft), "is it working")
    print(reminderInDays)
    print(nextCalDate)
    print(dateToStartSubract)
    print(todayDate)
    print(daysPassed)
    print(daysLeft)
  return None


@app.route('/parts', methods=['GET', 'POST'])
def parts_display():
  all_parts = Form.query.all()
  updateDateFinal()
  print(all_parts)
  #count=0
  #for i in all_parts:
  #    count+=1
  return render_template('parts.html', forms=all_parts)


@app.route('/get_options/<selected_option>', methods=['GET'])
def get_options(selected_option):
  # Fetch options based on the selected_option from the dictionary
  plantAnd_Area = {
    'Pune': [
      'Select Area', 'Paint Shop', 'Rear Axle', 'Front Axle', 'Trim 1',
      'Trim 2', 'Trim 3', 'TCF 1', 'TCF 2', 'TCF 3', 'TIW', 'IBF'
    ],
    'Jamshedpur': [
      'Select Area', 'Paint Shop', 'Rear Axle', 'Front Axle', 'Trim 1',
      'Trim 2', 'Trim 3', 'TCF 1', 'TCF 2', 'TCF 3', 'TIW', 'IBF'
    ],
    'Lucknow': [
      'Select Area', 'Paint Shop', 'Rear Axle', 'Front Axle', 'Trim 1',
      'Trim 2', 'TCF', 'TIW', 'IBF'
    ],
    'Dharwad':
    ['Select Area', 'Rear Axle', 'Front Axle', 'Trim ', 'TCF ', 'IBF'],
  }
  options = plantAnd_Area.get(selected_option)
  #print(selected_option)
  print(options)
  return jsonify(options)


@app.route('/parts/delete/<id>', methods=['GET'])
def deleteFormData(id):
  part = Form.query.filter_by(id=id).first()
  #print(part)
  db.session.delete(part)
  db.session.commit()
  return redirect(url_for('parts_display'))


@app.route('/search', methods=['GET', 'POST'])
def search():
  if request.method == 'POST':
    #print('test')
    query2 = request.form['query']
    print(query2)
    test_form_0 = Form.query.filter_by(partName=query2).all()
    test_form_1 = Form.query.filter_by(partUniqueNumber=query2).all()
    test_form_2 = Form.query.filter_by(partType=query2).all()
    test_form = test_form_0 + test_form_1 + test_form_2
    print(test_form)
    return render_template('parts.html', forms=test_form)
  if request.method == 'GET':
    return redirect(url_for('home'))


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port='8083')
  updateDateFinal()
