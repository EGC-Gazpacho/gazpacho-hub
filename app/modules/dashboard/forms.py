from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class DashboardForm(FlaskForm):
    ndatasets = StringField('Number', validators=[DataRequired()])
