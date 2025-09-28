import smtplib

class EmailAccount:
    def __init__(self, my_email, my_password):
        self.m_myemail = my_email
        self.m_password = my_password

    def send_email(self, to_address, subject, message):
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(self.m_myemail, self.m_password)
            connection.sendmail(from_addr=self.m_myemail, to_addrs=to_address, msg=f"Subject: {subject}\n\n{message}")
