from reportlab.pdfgen import canvas
from django.http import HttpResponse
from io import BytesIO


''' this is for the pdf export '''
"""
def view(request):

    file = tempfile.NamedTemporaryFile()

    e = PdfA4Letter(file.name)

    ref = '/absolute/path/to/image.png'
    e.image(ref, width=frame_width, height=10*cm)
    e.h1((u'Über Mich'))
    e.h3('Next header')

    t = """"""
    ascasc<br />
    ascascasc<br />
    <ul>
        <li>sdv1</li>
        <li>sdv2</li>
        <li>sdv3</li>
    </ul>
    ascasc<br />
    ascasc<br />
    """"""

    e.text(t)
    e.blankline(2)
    e.end_keep_together()
    e.build()

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=gugus.pdf'
    response.write(file.read())
    file.close()
    return response
"""
# another example

def some_view(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
