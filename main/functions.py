from PIL import Image
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

# Load the certificate image
certificate_image_path = (
    "/home/rakhmatullo/Documents/Github/Lyceum/quiz_app/media/certificate.png"
)
certificate_image = Image.open(certificate_image_path)

# Create a new image with the same dimensions as the certificate image
certificate_with_content = Image.new("RGB", certificate_image.size)

# Paste the certificate image onto the new image
certificate_with_content.paste(certificate_image, (0, 0))

# Create a canvas for drawing PDF content with landscape orientation


# Add dynamic content to the PDF canvas
def create_certificate(student):
    pdf_canvas = canvas.Canvas(
        f"/home/rakhmatullo/Documents/Github/Lyceum/quiz_app/media/certificate/{student['uuid']}.pdf", pagesize=landscape(letter)
    )

    # Draw the certificate image with content onto the PDF canvas
    pdf_canvas.drawImage(
        ImageReader(certificate_with_content),
        0,
        0,
        width=landscape(letter)[0],
        height=landscape(letter)[1],
    )

    pdf_canvas.setFont("Helvetica-BoldOblique", 16)
    pdf_canvas.setFillColorRGB(0, 0, 0)
    pdf_canvas.drawString(305, 348, student["city"])
    pdf_canvas.setFont("Helvetica-BoldOblique", 16)
    pdf_canvas.drawString(200, 318, student["school"])
    pdf_canvas.drawString(200, 287, student["name"])
    pdf_canvas.setFont("Helvetica", 16)
    pdf_canvas.drawString(85, 40, student["id"])
    pdf_canvas.save()


# Save the PDF

print("Certificate generated successfully.")
