from datetime import date, time, datetime
from docdefunto.models import AnagraficaDefunto

def crea_defunto_di_test():
    """
    Crea e salva un'istanza di AnagraficaDefunto con dati fittizi
    per scopi di test. Ritorna l'istanza salvata.
    """
    defunto = AnagraficaDefunto.objects.create(
        # Dati anagrafici
        cognome="Rossi",
        nome="Mario",
        sesso="M",
        cittadinanza="Italiana",
        luogo_nascita="Trieste",
        data_nascita=date(1950, 5, 12),
        comune_residenza="Trieste",
        via_residenza="Via Roma 1",
        codice_fiscale="RSSMRA50E12L424Z",
        doc_ric_def="Carta d'Identità",
        ente_doc_def="Comune di Trieste",
        data_doc_def=date(2010, 4, 20),

        # Decesso
        comune_decesso="Trieste",
        via_decesso="Via Milano 10",
        ospedale="Ospedale Maggiore",
        reparto_ospedaliero="Cardiologia",
        data_morte=date(2023, 3, 15),
        ora_morte=time(14, 30),
        tipo_luogo_salma=1,
        comune_salma="Trieste",
        via_salma="Via San Marco 7",

        # Stato civile e famiglia
        professione="Pensionato",
        stato_civile="Coniugato",
        cognome_parente="Bianchi",
        nome_parente="Lucia",
        data_nascita_parente=date(1955, 8, 21),
        doc_ric_par="Carta d'Identità",
        ente_doc_par="Comune di Trieste",
        data_doc_par=date(2015, 9, 10),

        # Contatti
        tel_famiglia="040123456",
        email="famiglia.rossi@example.com",
        altro="Note aggiuntive di test.",

        # Funerale
        chiesa="Chiesa di San Giusto",
        comune_chiesa="Trieste",
        data_ora_funerale=datetime(2023, 3, 20, 10, 30),
        data_inumazione=date(2023, 3, 20),
        ora_inumazione=time(11, 30),
        comune_inumazione="Trieste (TS)",
        ubicazione_feretro="Cimitero di Sant'Anna, loculo 23",
        affissione_manifesti=True,
        medico_curante="Dott. Verdi",
        fioraio="Fioraio Bella Rosa",

        # Servizi funebri
        lutto_casa=True,
        corteo_da_casa=True,
        corteo_da_ospedale=False,
        pass_solo_auto=False,
        pass_casa_per_corteo=True,
        dirett_in_chiesa=False,
        sala_commiato=False,
        tutto_in_auto=False,
        auto_chiesa_cimitero=True,

        # Servizi economici e logistici
        data_incarico=date(2023, 3, 16),
        necrofori=4,
        fattura_n="123/2023",
        articolo_cofano_funebre="Cofano in legno rovere",
        targa_autofunebre="AB123CD",
        altro_servizi="Servizio aggiuntivo: trasporto floreale",
    )
    return defunto

# def generate_filled_pdf(template_pdf_file, fields):
#     """
#     Genera un PDF in memoria con i campi riempiti.
#     Ritorna un BytesIO con il PDF.
#     """
#     from PyPDF2 import PdfReader, PdfWriter
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     from reportlab.lib.units import mm
#     from io import BytesIO
#     from reportlab.lib.pagesizes import A4

#     template_pdf = PdfReader(template_pdf_file.path)
#     output = PdfWriter()

#     # Creo il PDF con il testo
#     packet = BytesIO()
#     can = canvas.Canvas(packet, pagesize=A4)

#     width, height = A4

#     for field_name, data in fields.items():
#         info = data["info"]
#         if info["active"]:
#             text = data['text']
#             x = data['x']*mm
#             # Sposta l'origine in alto a sinistra
#             if info["invert_y"]:  
#                 y = height - data['y']*mm
#             else:
#                 y = data['y']*mm
#             can.setFont(info["font"], info["size"])    
#             can.drawString(x, y, text)

#     can.save()
#     packet.seek(0)

#     # Fonde l’overlay con la prima pagina del template
#     overlay_pdf = PdfReader(packet)
#     page = template_pdf.pages[0]
#     page.merge_page(overlay_pdf.pages[0])
#     output.add_page(page)

#     # Scrivo su buffer in memoria
#     pdf_bytes = BytesIO()
#     output.write(pdf_bytes)
#     pdf_bytes.seek(0)

#     return pdf_bytes
