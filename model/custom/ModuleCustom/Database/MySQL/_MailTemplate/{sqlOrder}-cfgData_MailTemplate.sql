# ==============================================================================
# IMPORTANT : Before use those templates, remember to upload the files with the 
# templates
# ==============================================================================
DELETE FROM _MailTemplate;

# Mail sent by _User when a user has registered in the platform. It contains the
# activation code
INSERT INTO _MailTemplate (MID, Subject, Comments, Content) VALUES 
('_User:Register','Welcome to {APP_NAME}!','email template on registration', '
<html>
<body>

<p>
Welcome $name to {APP_NAME}!
</p>

This your activation e-mail : $url

</body>
</html>
');

# Mail sent by _User when a user has forgotten his password and a it contains the
# new password set automatically by the system
INSERT INTO _MailTemplate (MID,Subject,Comments, Content) VALUES ('_User:ForgotPassword','New password to access to {APP_NAME}','email template on forgot password', '
<html>
<body>

TBD

</body>
</html>
');