from django.db import models
from django.utils.translation import gettext_lazy as _
from app.models import Organization, User

class AnagraficaDefunto(models.Model):
    # Metadata
    created_by = models.ForeignKey(User, verbose_name=_("Creato da"), on_delete=models.PROTECT, blank=False, null=False)
    organization = models.ForeignKey(Organization, verbose_name=_("Organizzazione"), on_delete=models.PROTECT, blank=False, null=False)
    
    # Autofields (non compilare)
    relative_id = models.PositiveIntegerField(blank=False, null=False) 
    created = models.DateTimeField(verbose_name="Data di creazione", auto_now_add=True) # Campo automatico, non compilare
    modified = models.DateTimeField(verbose_name="Ultima modifica", blank=True, null=True, auto_now=True) # Campo automatico, non compilare

    # Dati anagrafici
    cognome = models.CharField(verbose_name="Cognome Defunto", blank=True, null=True, max_length=255)
    nome = models.CharField(verbose_name="Nome Defunto", blank=True, null=True, max_length=255)
    sesso = models.CharField(verbose_name="Sesso", max_length=1, blank=True, null=True, 
                             choices=[
                                 ("F", "Femmina"),
                                 ("M", "Maschio")]
                                 )
    cittadinanza = models.CharField(verbose_name="Cittadinanza", blank=True, null=True, max_length=127)
    comune_nascita = models.CharField(verbose_name="Comune di Nascita", blank=True, null=True, max_length=255)
    provincia_nascita = models.CharField(verbose_name="Provincia di Nascita (sigla)", blank=True, null=True, max_length=2)
    data_nascita = models.DateField(verbose_name="Data di Nascita", blank=True, null=True)
    comune_residenza = models.CharField(verbose_name="Comune di Residenza", blank=True, null=True, max_length=255)
    provincia_residenza = models.CharField(verbose_name="Provincia di Residenza (sigla)", blank=True, null=True, max_length=2)
    via_residenza = models.CharField(verbose_name="Via di Residenza", blank=True, null=True, max_length=255)
    codice_fiscale = models.CharField(verbose_name="Codice Fiscale", blank=True, null=True, max_length=16)
    doc_ric_def = models.CharField(verbose_name="Tipo Documento di Riconoscimento Defunto", blank=True, null=True, max_length=10, 
                                   choices=[
                                       ("C.I.", "Carta di Identità"),
                                       ("Patente", "Patente"),
                                       ("Passaporto", "Passaporto")]
                                   )
    n_doc_ric_def = models.CharField(verbose_name="Numero Documento di Riconoscimento Defunto", blank=True, null=True, max_length=63)
    ente_doc_def = models.CharField(verbose_name="Ente di Rilascio Documento Defunto", blank=True, null=True, max_length=255)
    data_doc_def = models.DateField(verbose_name="Data di Rilascio Documento Defunto", blank=True, null=True)

    # Decesso
    comune_decesso = models.CharField(verbose_name="Comune del Decesso", blank=True, null=True, max_length=255)
    provincia_decesso = models.CharField(verbose_name="Provincia del Decesso (sigla)", blank=True, null=True, max_length=2)
    via_decesso = models.CharField(verbose_name="Via del Decesso", blank=True, null=True, max_length=255)
    data_decesso = models.DateField(verbose_name="Data del decesso", blank=True, null=True)
    ora_decesso = models.TimeField(verbose_name="Orario del decesso (formato hh:mm)", blank=True, null=True)
    
    # Osservazione salma
    comune_salma = models.CharField(verbose_name="Comune dell'osservazione salma", blank=True, null=True, max_length=255)
    provincia_salma = models.CharField(verbose_name="Provincia dell'osservazione salma (sigla)", blank=True, null=True, max_length=2)
    tipo_luogo_salma = models.CharField(verbose_name="Luogo di osservazione della salma", blank=True, null=True,
                                    choices=[
                                        ("Abitazione privata", "Abitazione privata"),
                                        ("Istituto / Casa di riposo / Struttura obitoriale / Ospedale", 
                                         "Istituto / Casa di riposo / Struttura obitoriale / Ospedale"),], 
                                    )
    ospedale = models.CharField(verbose_name="Ospedale", blank=True, null=True, max_length=255)
    reparto_ospedaliero = models.CharField(verbose_name="Reparto Ospedaliero", blank=True, null=True, max_length=255)
    via_salma = models.CharField(verbose_name="Via dell'osservazione salma", blank=True, null=True, max_length=255)

    # Stato civile
    professione = models.CharField(verbose_name="Professione", blank=True, null=True, max_length=255)
    stato_civile = models.CharField(verbose_name="Stato Civile", blank=True, null=True, max_length=63,
                                    choices=[
                                        ("Celibe / nubile", "Celibe / nubile"),
                                        ("Coniugato / unito civilmente", "Coniugato / unito civilmente con"),
                                        ("Vedovo", "Vedovo di"),
                                        ("Già coniugato / unito civolmente", "Già coniugato / unito civolmente con")],
                                    )
    cognome_coniuge = models.CharField(verbose_name="Cognome Coniuge", blank=True, null=True, max_length=255)
    nome_coniuge = models.CharField(verbose_name="Nome Coniuge", blank=True, null=True, max_length=255)

    # Parente
    tipo_parente = models.CharField(verbose_name="Grado di parentela", blank=True, null=True, max_length=255)
    comune_residenza_par = models.CharField(verbose_name="Comune di residenza parente", blank=True, null=True, max_length=255)
    provincia_residenza_par = models.CharField(verbose_name="Provincia di residenza parente (sigla)", blank=True, null=True, max_length=2)
    indirizzo_residenza_par = models.CharField(verbose_name="Via di residenza parente", blank=True, null=True, max_length=255)

    cognome_parente = models.CharField(verbose_name="Cognome Parente", blank=True, null=True, max_length=255)
    nome_parente = models.CharField(verbose_name="Nome Parente", blank=True, null=True, max_length=255)
    data_nascita_parente = models.DateField(verbose_name="Data di Nascita Parente", blank=True, null=True)
    doc_ric_par = models.CharField(verbose_name="Documento di Riconoscimento Parente", blank=True, null=True, max_length=10,
                                   choices=[
                                       ("C.I.", "Carta di Identità"),
                                       ("Patente", "Patente"),
                                       ("Passaporto", "Passaporto")], 
                                   )
    n_doc_ric_par = models.CharField(verbose_name="Numero Documento di Riconoscimento Parente", blank=True, null=True, max_length=63)
    ente_doc_par = models.CharField(verbose_name="Ente di Rilascio Documento Parente", blank=True, null=True, max_length=255)
    data_doc_par = models.DateField(verbose_name="Data di Rilascio Documento Parente", blank=True, null=True)

    # Contatti
    tel_famiglia = models.CharField(verbose_name="Telefono Famiglia", blank=True, null=True, max_length=63)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    altro = models.TextField(verbose_name="Altre Informazioni", blank=True, null=True)

    # Funerale
    data_ora_partenza = models.DateTimeField(verbose_name="Data e Ora della partenza del corteo", blank=True, null=True) #TODO: non è la stessa cosa di data_ora_funerale?
    chiesa = models.CharField(verbose_name="Chiesa", blank=True, null=True, max_length=255)
    comune_chiesa = models.CharField(verbose_name="Comune Chiesa", blank=True, null=True, max_length=255)
    provincia_chiesa = models.CharField(verbose_name="Provincia della Chiesa (sigla)", blank=True, null=True, max_length=2)
    data_ora_funerale = models.DateTimeField(verbose_name="Data e Ora del Funerale", blank=True, null=True)
    # data_inumazione = models.DateField(verbose_name="Data di sepoltura", blank=True, null=True) #TODO: sicuro che vadano eliminati?
    # ora_inumazione = models.TimeField(verbose_name="Orario di sepoltura (formato hh:mm)", blank=True, null=True)
    comune_sepoltura = models.CharField(verbose_name="Comune di sepoltura", blank=False, null=True, max_length=255)
    # altro_comune = models.BooleanField(verbose_name="Comune diverso da Rionero in Vulture", default=False)
    provincia_sepoltura = models.CharField(verbose_name="Provincia di sepoltura (sigla)", blank=True, null=True, max_length=2)
    ubicazione_feretro = models.CharField(verbose_name="Ubicazione Feretro", blank=True, null=True, max_length=11,
                                      choices=[
                                       ("Cappella", "Cappella"),
                                       ("Inumazione", "Inumazione"),
                                       ("Tumulazione", "Tumulazione")], 
                                   ) 
    affissione_manifesti = models.TextField(verbose_name="Comuni affissione manifesti", blank=True, null=True)
    medico_curante = models.CharField(verbose_name="Medico Curante", blank=True, null=True, max_length=255)
    fioraio = models.CharField(verbose_name="Fioraio", blank=True, null=True, max_length=255)

    # Servizi funebri
    lutto_casa = models.BooleanField(verbose_name="Lutto a Casa", default=False)
    corteo_da_casa = models.BooleanField(verbose_name="Corteo da Casa", default=False)
    corteo_da_ospedale = models.BooleanField(verbose_name="Corteo da Ospedale", default=False)
    pass_solo_auto = models.BooleanField(verbose_name="Passaggio da Casa Solo Auto", default=False)
    pass_casa_per_corteo = models.BooleanField(verbose_name="Passaggio da Casa per Iniziare il Corteo", default=False)
    dirett_in_chiesa = models.BooleanField(verbose_name="Direttamente in Chiesa", default=False)
    sala_commiato = models.BooleanField(verbose_name="Sala del Commiato", default=False)
    tutto_in_auto = models.BooleanField(verbose_name="Tutto in Auto", default=False)
    auto_chiesa_cimitero = models.BooleanField(verbose_name="Auto Chiesa / Cimitero", default=False)

    # Servizi economici e logistici
    data_incarico = models.DateField(verbose_name="Data di Incarico", blank=True, null=True)
    necrofori = models.PositiveIntegerField(verbose_name="Numero Necrofori", blank=True, null=True)
    fattura_n = models.CharField(verbose_name="Fattura N.", blank=True, null=True, max_length=127)
    articolo_cofano_funebre = models.CharField(verbose_name="Articolo Cofano Funebre", blank=True, null=True, max_length=255)
    targa_autofunebre = models.CharField(verbose_name="Targa autofunebre", blank=True, null=True, max_length=255)
    altro_servizi = models.TextField(verbose_name="Altro (servizi)", blank=True, null=True)

    # Data e firma
    firmato = models.BooleanField(verbose_name="Firma documenti", default=False)
    data_firma = models.DateField(verbose_name="Firma documenti in data", blank=True, null=True)

    @property
    def get_eta(self):
        if self.data_nascita and self.data_decesso:
            years_delta = self.data_decesso.year - self.data_nascita.year
            months_delta = self.data_decesso.month - self.data_nascita.month
            days_delta = self.data_decesso.day - self.data_nascita.day
            happy_birthday = int(months_delta >= 0 and days_delta >= 0)
            age = years_delta + happy_birthday
            return age
        else:
            return None

    class Meta(): # type: ignore
        verbose_name = _("Anagrafica Defunto")
        verbose_name_plural = _("Anagrafiche Defunti")

    def __str__(self):
        return f"{self.cognome} {self.nome}"
    
    def save(self, *args, **kwargs):
        if self.relative_id is None:  # solo alla creazione
            last = AnagraficaDefunto.objects.filter(organization=self.organization)\
                                    .aggregate(models.Max("relative_id"))["relative_id__max"]
            self.relative_id = 1 if last is None else last + 1
        super().save(*args, **kwargs)

    # FIELD_CATEGORIES determina la visualizzazione dei dati in defunto.html e in defunto_edit, quindi deve sempre essere aggiornata
    NON_USER_FIELDS = ('created_by', 'organization', 'relative_id', 'created', 'modified', )
    FIELD_CATEGORIES = {
        "Anagrafica":('cognome', 'nome', 'sesso', 'cittadinanza', 'comune_nascita', 'provincia_nascita', 
                      'data_nascita', 'comune_residenza', 'provincia_residenza', 'via_residenza', 
                      'codice_fiscale', 'doc_ric_def', 'n_doc_ric_def', 'ente_doc_def', 'data_doc_def', ),
        "Decesso":('comune_decesso', 'provincia_decesso', 'via_decesso', 'data_decesso', 'ora_decesso', ),
        "Salma":('comune_salma','provincia_salma','tipo_luogo_salma','ospedale', 'reparto_ospedaliero','via_salma',),
        "Stato civile":('professione', 'stato_civile','cognome_coniuge','nome_coniuge',), 
        "Parente": ('tipo_parente', 'comune_residenza_par', 'provincia_residenza_par', 'indirizzo_residenza_par',
                    'cognome_parente', 'nome_parente', 'data_nascita_parente', 'doc_ric_par', 'n_doc_ric_par', 
                    'ente_doc_par', 'data_doc_par', ),
        "Contatti":('tel_famiglia', 'email', 'altro', ),
        "Funerale":('data_ora_partenza', 'chiesa', 'comune_chiesa', 'provincia_chiesa', 'data_ora_funerale',  
                    'comune_sepoltura','provincia_sepoltura', 'ubicazione_feretro', 
                    'affissione_manifesti', 'medico_curante', 'fioraio', ),
        "Servizi funebri":('lutto_casa', 'corteo_da_casa', 'corteo_da_ospedale', 'pass_solo_auto', 
                           'pass_casa_per_corteo', 'dirett_in_chiesa', 'sala_commiato', 'tutto_in_auto', 
                           'auto_chiesa_cimitero', ),
        "Servizi economico-logistici":('data_incarico', 'necrofori', 'fattura_n', 'articolo_cofano_funebre', 
                                       'targa_autofunebre', 'altro_servizi', ),
        "Data e firma":('data_firma', 'firmato',)
    }


def user_documents_path(instance, filename):
    # esempio: "media/azienda_5/documenti/contratto.pdf"
    return f"{instance.organization.tag}/documents/{filename}"
def user_documentsbkgds_path(instance, filename):
    # esempio: "media/azienda_5/documenti/contratto.pdf"
    return f"{instance.organization.tag}/backgrounds/{filename}"
class Documento(models.Model):
    nome = models.CharField(verbose_name="Nome Documento", blank=True, null=True, max_length=255, default="")
    file = models.FileField(verbose_name="File", upload_to=user_documents_path)
    background = models.FileField(verbose_name="Sfondo", upload_to=user_documentsbkgds_path, blank=True, null=True)
    organization = models.ForeignKey(Organization, verbose_name=_("Organizzazione"), on_delete=models.PROTECT, blank=False, null=False)

    class Meta(): # type: ignore
        verbose_name = _("Documento")
        verbose_name_plural = _("Documenti")

    def __str__(self):
        return self.file.name.split("/")[-1]  # mostra solo il nome del file

