from datetime import date, time, datetime
from docdefunto.models import AnagraficaDefunto
from django.contrib.auth import get_user_model
from app.models import Organization, User, Profile

def setup_superuser(username="admin", password="admin", email="admin@admin.com"):
    """
    Crea un superuser e un'organizzazione 'Superusers', e li collega tra loro.
    Se già esistono, li recupera senza duplicarli.
    """

    # Crea o recupera l'organizzazione
    org, org_created = Organization.objects.get_or_create(
        tag="superusers",
        # defaults={
        #     "name": "Superusers", 
        #     "email": "superusers@admin.com", 
        #     "domain": "superuser.ade.it",}
    )
    if org_created:
        print("✅ Organizzazione 'Superusers' creata.")
    else:
        print("ℹ️ Organizzazione 'Superusers' già esistente.")

    # Crea o recupera il superuser
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email, 
            "is_superuser": True, 
            "is_staff": True,}
    )
    if created:
        user.set_password(password)
        user.save()
        user.profile, create = Profile.objects.get_or_create(user=user,
                                             defaults={
                                                 "organization":org,
                                             })
        print(f"✅ Superuser '{username}' creato.")
    else:
        print(f"ℹ️ Superuser '{username}' già esistente.")
        user.profile.organization = org
        user.profile.save()
    print(f"✅ Assegnata organizzazione '{org}' a '{username}'.")

    return user, org

def crea_defunto_di_test(username="admin"):
    """
    Crea e salva un'istanza di AnagraficaDefunto con dati fittizi
    per scopi di test. Ritorna l'istanza salvata.
    """
    user = User.objects.get(username=username)
    defunto = AnagraficaDefunto.objects.create(
        # Metadata
        created_by = user,
        organization = user.profile.organization,
        # Dati anagrafici
        cognome="Rossi",
        nome="Mario",
        sesso="M",
        cittadinanza="Italiana",
        comune_nascita="Trieste",
        provincia_nascita="TS",
        data_nascita=date(1950, 5, 12),
        comune_residenza="Trieste",
        provincia_residenza="TS",
        via_residenza="Via Roma 1",
        codice_fiscale="RSSMRA50E12L424Z",
        doc_ric_def="C.I.",
        n_doc_ric_def="AR55593SS",
        ente_doc_def="Comune di Trieste",
        data_doc_def=date(2010, 4, 20),

        # Decesso
        comune_decesso="Trieste",
        provincia_decesso="TS",
        via_decesso="Via Milano 10",
        data_decesso=date(2023, 3, 15),
        ora_decesso=time(14, 30),

        # Osservazione salma
        comune_salma="Trieste",
        provincia_salma="TS",
        tipo_luogo_salma="Abitazione privata",
        ospedale="Ospedale Maggiore",
        reparto_ospedaliero="Cardiologia",
        via_salma="Via San Marco 7",

        # Stato civile
        professione="Pensionato",
        stato_civile="Celibe / nubile",
        cognome_coniuge="Donati",
        nome_coniuge="Francesca",

        # Parente
        tipo_parente="Cugina",
        comune_residenza_par="Milano",
        provincia_residenza_par="MI",
        via_residenza_par="Via degli Uccellini, 23",
        cognome_parente="Bianchi",
        nome_parente="Lucia",
        data_nascita_parente=date(1955, 8, 21),
        codice_fiscale_par="PPPMRA50E12L424Z",
        doc_ric_par="Patente",
        n_doc_ric_par="CD66336DF",
        ente_doc_par="Comune di Trieste",
        data_doc_par=date(2015, 9, 10),

        # Contatti
        tel_famiglia="040123456",
        email="famiglia.rossi@example.com",
        altro="Note aggiuntive di test.",

        # Funerale
        data_ora_partenza=datetime(2023, 3, 20, 9, 30),
        chiesa="Chiesa di San Giusto",
        comune_chiesa="Cordenons",
        provincia_chiesa="PS",
        data_ora_funerale=datetime(2023, 3, 20, 10, 30),
        # data_inumazione=date(2023, 3, 20),
        # ora_inumazione=time(11, 30),
        comune_sepoltura="Pordenone",
        provincia_sepoltura="PN",
        ubicazione_feretro="Cappella",
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

        # Data e firma
        firmato=True,
        data_firma=date(2025, 9, 15),
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
