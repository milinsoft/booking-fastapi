from email.message import EmailMessage

from pydantic import EmailStr

from app.config import settings


def create_booking_confirmation_template(booking: dict, email_to: EmailStr):
    email = EmailMessage()
    email["From"] = settings.SMTP_USER
    email["To"] = email_to
    email["Subject"] = "Booking Confirmation"
    email.set_content(
        f"""
        <H1>Here are all the details about your booking</H1>
        
        Hi there! below are your booking details:\n
        <ul>
        <li>
            Check in: {booking["date_from"]}
        </li>
        <li>
            Check out: {booking["date_to"]}
        </li>
        <li>
            Stay length {booking["total_days"]} days
        </li>
        <li> 
            Total cost: ${booking["price"]}
        </li> 
        </ul>
        """,
        subtype="html",
    )
    return email
