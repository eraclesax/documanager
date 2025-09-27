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
        created_by = user,
        organization = user.profile.organization,
        relative_id=1,

        # Dati anagrafici
        cognome="Rossi",
        nome="Mario",
        sesso="M",
        cittadinanza="Italiana",
        comune_nascita="Napoli",
        provincia_nascita="NA",
        data_nascita=date(1950, 5, 20),
        comune_residenza="Roma",
        provincia_residenza="RM",
        via_residenza="Via Garibaldi 10",
        codice_fiscale="RSSMRA50E20H501X",
        doc_ric_def="C.I.",
        n_doc_ric_def="AA1234567",
        ente_doc_def="Comune di Roma",
        data_doc_def=date(2010, 6, 15),

        # Decesso
        comune_decesso="Roma",
        provincia_decesso="RM",
        via_decesso="Via Appia 123",
        data_decesso=date(2025, 1, 1),
        ora_decesso=time(14, 30),

        # Osservazione salma
        comune_salma="Roma",
        provincia_salma="RM",
        tipo_luogo_salma="Ospedale",
        ospedale="Policlinico Umberto I",
        reparto_ospedaliero="Cardiologia",
        via_salma="Via del Policlinico 1",

        # Stato civile
        professione="Impiegato",
        stato_civile="Coniugato / unito civilmente",
        cognome_coniuge="Bianchi",
        nome_coniuge="Anna",

        # Parente
        tipo_parente="Figlio",
        cognome_parente="Rossi",
        nome_parente="Luca",
        sesso_par="M",
        comune_nascita_par="Roma",
        provincia_nascita_par="RM",
        data_nascita_parente=date(1980, 7, 15),
        comune_residenza_par="Roma",
        provincia_residenza_par="RM",
        via_residenza_par="Via Milano 45",
        codice_fiscale_par="RSSLCU80L15H501X",
        doc_ric_par="C.I.",
        n_doc_ric_par="BB7654321",
        ente_doc_par="Comune di Roma",
        data_doc_par=date(2015, 3, 10),

        # Contatti
        tel_famiglia="061234567",
        email="famiglia.rossi@example.com",
        altro="Note varie per i test.",

        # Funerale
        data_ora_partenza=datetime(2025, 1, 3, 9, 0),
        chiesa="Chiesa San Pietro",
        comune_chiesa="Roma",
        provincia_chiesa="RM",
        data_ora_funerale=datetime(2025, 1, 3, 10, 30),
        comune_sepoltura="Rionero in Vulture",
        provincia_sepoltura="PZ",
        processo_sepoltura="Tradizionale",
        ubicazione_feretro="Tumulazione",
        affissione_manifesti="Roma, Napoli",
        medico_curante="Dr. Verdi",
        fioraio="Fiori Rossi",

        # Servizi funebri
        lutto_casa=True,
        corteo_da_casa=True,
        dirett_in_chiesa=False,
        sala_commiato=False,
        tutto_in_auto=False,
        auto_chiesa_cimitero=True,

        # Servizi economici e logistici
        data_incarico=date(2024, 12, 30),
        necrofori=4,
        fattura_n="FATT-2025-001",
        articolo_cofano_funebre="Cofano in legno pregiato",
        targa_autofunebre="AB123CD",
        altro_servizi="Servizio musicale durante la cerimonia.",

        # Data e firma
        firmato=True,
        data_firma=date(2025, 1, 2)
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
