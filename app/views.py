"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
"""
import os
from app import app
from flask import render_template, request, flash
from werkzeug.utils import secure_filename

# Note: that when using Flask-WTF we need to import the Form Class that we created
# in forms.py
from .forms import MyForm, curieForm


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

        #photo = photoform.photo.data # we could also use request.files['photo']
        description = form.description.data
        target = form.target.data
        ligand = form.ligand.data
        cx,cy,cz = str(form.center_x.data), str(form.center_y.data), str(form.center_z.data)
        sx,sy,sz = str(form.size_x.data), str(form.size_y.data), str(form.size_z.data)
        email = form.email.data

        import mysql.connector as con
        mycon = con.connect(host="sql12.freesqldatabase.com",user="sql12352288",password="7X35JENbK3",port=3306,database="sql12352288")
        mycursor = mycon.cursor()
        mycursor.execute("SELECT COUNT(*) FROM curie")
        jobID = mycursor.fetchall()[0][0]

        i = int(jobID) + 1
        t = str(i) + "_" + str(secure_filename(target.filename))
        l = str(i) + "_" + str(secure_filename(ligand.filename))
        c = "./app/static/uploads/configs/" + str(i) + ".txt"


        buffer = "center_x="+cx+"\ncenter_y="+cy+"\ncenter_z="+cz+"\nsize_x="+sx+"\nsize_y="+sy+"\nsize_z="+sz
        f = open(c,"w")
        f.write(buffer)
        f.close

        print(description)

        target.save(os.path.join(
            #app.config['UPLOAD_FOLDER'], secure_filename(target.filename)
            "./app/static/uploads/receptor",t #secure_filename(target.filename)
        ))
        ligand.save(os.path.join("./app/static/uploads/ligands",l))
        mycursor.execute("insert into curie values ({},'{}','{}','{}','{}',CURDATE(),'{}',0)".format(i,email,t,l,(str(i)+".txt"),description))
        mycon.commit()
        #photo.save(os.path.join(
        #    app.config['UPLOAD_FOLDER'], filename
        #))

        return render_template('display_photo.html', filename="OwO", description=description)

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