"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
"""
import os
from app import app
from flask import render_template, request, flash
from werkzeug.utils import secure_filename
from random import choice, shuffle
from string import digits, ascii_lowercase

# Note: that when using Flask-WTF we need to import the Form Class that we created
# in forms.py
from .forms import MyForm, curieForm

def gen_word(N, min_N_dig, min_N_low):
    choose_from = [digits]*min_N_dig + [ascii_lowercase]*min_N_low
    choose_from.extend([digits + ascii_lowercase] * (N-min_N_low-min_N_dig))
    chars = [choice(bet) for bet in choose_from]
    shuffle(chars)
    return ''.join(chars)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/About')
def about():
    """Render about page."""
    return render_template('about.html')

@app.route('/Visualise')
def visualise():
    """Render visualisation page."""
    return render_template('visualise.html')    


@app.route('/basic-form', methods=['GET', 'POST'])
def basic_form():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

        return render_template('result.html',
                               firstname=firstname,
                               lastname=lastname,
                               email=email)

    return render_template('form.html')


@app.route('/wtform', methods=['GET', 'POST'])
def wtform():
    myform = MyForm()

    if request.method == 'POST':
        if myform.validate_on_submit():
            # Note the difference when retrieving form data using Flask-WTF
            # Here we use myform.firstname.data instead of request.form['firstname']
            firstname = myform.firstname.data
            lastname = myform.lastname.data
            email = myform.email.data

            flash('You have successfully filled out the form', 'success')
            return render_template('result.html', firstname=firstname, lastname=lastname, email=email)

        flash_errors(myform)
    return render_template('wtform.html', form=myform)


@app.route('/dock', methods=['GET', 'POST'])
def dock_upload():
    form = curieForm()

    if request.method == 'POST' and form.validate_on_submit():

        description = form.description.data
        target = form.target.data
        ligand = form.ligand.data
        cx,cy,cz = str(form.center_x.data), str(form.center_y.data), str(form.center_z.data)
        sx,sy,sz = str(form.size_x.data), str(form.size_y.data), str(form.size_z.data)
        email = form.email.data

        import mysql.connector as con
        mycon = con.connect(host=app.config['DB_HOST'],user=app.config['DB_USER'],password=app.config['DB_PASSWORD'],port=app.config['DB_PORT'],database=app.config['DB_NAME'])
        mycursor = mycon.cursor()

        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            target.save(secure_filename(target.filename))
            ligand.save(secure_filename(ligand.filename))
            buffer = "center_x="+cx+"\ncenter_y="+cy+"\ncenter_z="+cz+"\nsize_x="+sx+"\nsize_y="+sy+"\nsize_z="+sz
            f = open("config.txt","w")
            f.write(buffer)
            f.close()
            ligandB = convertToBinaryData(secure_filename(ligand.filename))
            receptor = convertToBinaryData(secure_filename(target.filename))
            config = convertToBinaryData("config.txt")
            ligandName = secure_filename(ligand.filename)
            receptorName = secure_filename(target.filename)
            sqlQuery = "insert into curieweb (id, email, protein, protein_name, ligand_pdbqt, ligand_name,date, description, config) values (%s,%s,%s,%s,%s,%s,CURDATE(),%s,%s) "
            jobID = gen_word(16, 1, 1)
            print("Submitted JobID: ",jobID)
            insert_tuple = (jobID,email,receptor,receptorName,ligandB,ligandName,description,config)
            mycursor.execute(sqlQuery,insert_tuple)
            mycon.commit()

        print("Description",description)

        return render_template('display_result.html', filename="OwO", description=description,job=jobID)

    flash_errors(form)
    return render_template('dock_upload.html', form=form)

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")