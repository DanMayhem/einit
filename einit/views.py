import flask.ext.wtf as w
import wtforms as f
import wtforms.validators as v

class SignUpForm(w.Form):
  name = f.StringField('Name', validators=[
    v.InputRequired('Name is required field')
  ])
  email = f.StringField('Email',validators=[
    v.Email('Valid email address required')
  ])
  password = f.PasswordField('Password', validators=[
    v.InputRequired('Password required'),
    v.EqualTo('password_confirmation','Passwords must match')
  ])
  password_confirmation = f.PasswordField('Confirm Password')

