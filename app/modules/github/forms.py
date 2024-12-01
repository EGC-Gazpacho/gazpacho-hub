from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class DataSetFormGithub(FlaskForm):
    title = StringField('Dataset Title', validators=[DataRequired()])
    commit_message = StringField('Commit Message', validators=[DataRequired()])
    owner = StringField('Repository Owner', validators=[DataRequired()])
    repo_name = StringField('Repository Name', validators=[DataRequired()])
    branch = StringField('Branch', default='main')

    repo_type = SelectField('Repository Type', choices=[
        ('new', 'New Repository'),
        ('existing', 'Existing Repository')
    ], default='existing')

    access_token = PasswordField('Personal Access Token', validators=[DataRequired()])
    license = SelectField('Dataset License', choices=[
        ('MIT', 'MIT'),
        ('GPL', 'GPL'),
        ('Apache', 'Apache'),
        ('CC BY', 'CC BY'),
        ('None', 'None')
    ])
    submit = SubmitField('Upload Dataset to GitHub')
