from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email


class MyForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])


class curieForm(FlaskForm):
    ligand = FileField('Ligand', validators=[
        FileRequired(),
        FileAllowed(['pdbqt', 'PDBQT only!'])
    ])
    target = FileField('Receptor / Target', validators=[
        FileRequired(),
        FileAllowed(['pdbqt', 'PDBQT only!'])
    ])
    description = StringField('Description',default="Curie Web Task")

    size_x = DecimalField('Size X',default=25.0)
    size_y = DecimalField('Size Y',default=25.0)
    size_z = DecimalField('Size Z',default=25.0)

    center_x = DecimalField('Center X',default=0)
    center_y = DecimalField('Center Y',default=0)
    center_z = DecimalField('Center Z',default=0)

    email = StringField('Email', validators=[DataRequired(), Email()])

class statusForm(FlaskForm):
    jobID = StringField('Job ID',validators=[DataRequired()])

class dockSingleForm(FlaskForm):
    description = StringField('Description',default="Curie Web Task")
    pdbID = StringField('PDB ID',validators=[DataRequired()])
    smiles = StringField('SMILES',validators=[DataRequired()])
    name = StringField('Ligand Name',validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

class generateSMILES(FlaskForm):
    n = IntegerField('Number of Molecules to Generate',default=1,validators=[DataRequired()])
    #modelSelection = SelectField('Model',choices=[("alpha","Alpha"),("beta","Beta")])

class generatePDBQTS(FlaskForm):
    jobType = SelectField(u'Generate for Protein or Ligand', choices=[("", "Protein or Ligand"),('protein', 'Protein (PDB)'), ('ligand', 'Ligand (SMILES)')], default='SelectOption')
    pdb = StringField('PDB ID')
    smiles = StringField('SMILES')
    name = StringField('Compound Name (Optional)')

class PyMedSearch(FlaskForm):
    query = StringField('Search Query',default="Query",validators=[DataRequired()])