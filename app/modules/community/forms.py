from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

from app.modules.community.models import CommunityType


class CommunityForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField(
        "Type",
        choices=[(type.value, type.name.capitalize()) for type in CommunityType],
        validators=[DataRequired()],
    )
    submit = SubmitField('Save Community')


class CommunityEditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Save Changes')
