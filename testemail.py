import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

#It makes the connection to server email
smtp = smtplib.SMTP('<SMTP-mailbox>', 25)

smtp.set_debuglevel(1)
fromaddr = 'sender-address'
toaddr = 'receiver-address'
text = 'hello Email'
smtp.sendmail(fromaddr, toaddr, text)
