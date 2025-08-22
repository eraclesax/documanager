def generate_filled_pdf(template_pdf_file, fields):
    """
    Genera un PDF in memoria con i campi riempiti.
    Ritorna un BytesIO con il PDF.
    """
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from io import BytesIO
    from reportlab.lib.pagesizes import A4

    template_pdf = PdfReader(template_pdf_file.path)
    output = PdfWriter()

    # Creo il PDF con il testo
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)

    width, height = A4

    for field_name, data in fields.items():
        info = data["info"]
        if info["active"]:
            text = data['text']
            x = data['x']
            # Sposta l'origine in alto a sinistra
            if info["invert_y"]:  
                y = height - data['y']
            else:
                y = data['y']
            can.setFont(info["font"], info["size"])    
            can.drawString(x, y, text)

    can.save()
    packet.seek(0)

    # Fonde l’overlay con la prima pagina del template
    overlay_pdf = PdfReader(packet)
    page = template_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    output.add_page(page)

    # Scrivo su buffer in memoria
    pdf_bytes = BytesIO()
    output.write(pdf_bytes)
    pdf_bytes.seek(0)

    return pdf_bytes

