from django.db import models

class AnagraficaDefunto(models.Model):
    # Dati anagrafici
    cognome = models.CharField(verbose_name="Cognome Defunto", blank=True, null=True, max_length=255, default="")
    nome = models.CharField(verbose_name="Nome Defunto", blank=True, null=True, max_length=255, default="")
    luogo_nascita = models.CharField(verbose_name="Luogo di Nascita", blank=True, null=True, max_length=255, default="")
    data_nascita = models.DateField(verbose_name="Data di Nascita", blank=True, null=True)
    comune_residenza = models.CharField(verbose_name="Comune di Residenza", blank=True, null=True, max_length=255, default="")
    via_residenza = models.CharField(verbose_name="Via di Residenza", blank=True, null=True, max_length=255, default="")

    # Decesso
    comune_decesso = models.CharField(verbose_name="Comune del Decesso", blank=True, null=True, max_length=255, default="")
    via_decesso = models.CharField(verbose_name="Via del Decesso", blank=True, null=True, max_length=255, default="")
    ospedale = models.CharField(verbose_name="Ospedale", blank=True, null=True, max_length=255, default="")
    reparto_ospedaliero = models.CharField(verbose_name="Reparto Ospedaliero", blank=True, null=True, max_length=255, default="")
    data_ora_morte = models.CharField(verbose_name="Data e Ora di Morte", blank=True, null=True, max_length=63, default="")

    # Stato civile e famiglia
    professione = models.CharField(verbose_name="Professione", blank=True, null=True, max_length=255, default="")
    stato_civile = models.CharField(verbose_name="Stato Civile", blank=True, null=True, max_length=127, default="")
    doc_ric_def = models.CharField(verbose_name="Documento di Riconoscimento Defunto", blank=True, null=True, max_length=63, default="")
    ente_doc_def = models.CharField(verbose_name="Ente di Rilascio Documento Defunto", blank=True, null=True, max_length=255, default="")
    data_doc_def = models.DateField(verbose_name="Data di Rilascio Documento Defunto", blank=True, null=True)
    cognome_parente = models.CharField(verbose_name="Cognome Parente", blank=True, null=True, max_length=255, default="")
    nome_parente = models.CharField(verbose_name="Nome Parente", blank=True, null=True, max_length=255, default="")
    data_nascita_parente = models.DateField(verbose_name="Data di Nascita Parente", blank=True, null=True)
    doc_ric_par = models.CharField(verbose_name="Documento di Riconoscimento Parente", blank=True, null=True, max_length=63, default="")
    ente_doc_par = models.CharField(verbose_name="Ente di Rilascio Documento Parente", blank=True, null=True, max_length=255, default="")
    data_doc_par = models.DateField(verbose_name="Data di Rilascio Documento Parente", blank=True, null=True)

    # Contatti
    tel_famiglia = models.CharField(verbose_name="Telefono Famiglia", blank=True, null=True, max_length=63, default="")
    email = models.EmailField(verbose_name="Email", blank=True, null=True, default="")
    altro = models.TextField(verbose_name="Altre Informazioni", blank=True, null=True, default="")

    # Funerale
    chiesa = models.CharField(verbose_name="Chiesa", blank=True, null=True, max_length=255, default="")
    data_ora_funerale = models.DateTimeField(verbose_name="Data e Ora del Funerale", blank=True, null=True)
    cimitero = models.CharField(verbose_name="Cimitero", blank=True, null=True, max_length=255, default="")
    ubicazione_feretro = models.TextField(verbose_name="Ubicazione Feretro", blank=True, null=True, default="")
    affissione_manifesti = models.BooleanField(verbose_name="Affissione Manifesti", default=False)
    medico_curante = models.CharField(verbose_name="Medico Curante", blank=True, null=True, max_length=255, default="")
    fioraio = models.CharField(verbose_name="Fioraio", blank=True, null=True, max_length=255, default="")

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
    necrofori = models.PositiveIntegerField(verbose_name="Numero Necrofori", blank=True, null=True)
    fattura_n = models.CharField(verbose_name="Fattura N.", blank=True, null=True, max_length=127, default="")
    articolo_cofano_funebre = models.CharField(verbose_name="Articolo Cofano Funebre", blank=True, null=True, max_length=255, default="")
    altro_servizi = models.TextField(verbose_name="Altro (servizi)", blank=True, null=True, default="")

    # Metadata
    created = models.DateTimeField(verbose_name="Data di creazione", auto_now_add=True)
    modified = models.DateTimeField(verbose_name="Ultima modifica", blank=True, null=True, auto_now=True)

    def __str__(self):
        return f"{self.cognome} {self.nome}"

    def fill_fields(self, empty_fields):
        """Fills fields of the type:
            empty_fields = {
                "nome": {"x": 100, "y": 700, "info":{...}},
                "data": {"x": 400, "y": 700, "info":{...}},
                "luogo": {"x": 100, "y": 650, "info":{...}},
            }
            in fields of the type:
            empty_fields = {
                "nome": {"text": "Mario Rossi", "x": 100, "y": 700, "info":{...}},
                "data": {"text": "21/08/2025", "x": 400, "y": 700, "info":{...}},
                "luogo": {"text": "Trieste", "x": 100, "y": 650, "info":{...}},
            }        
        """
        for field_name, _ in empty_fields.items():
            empty_fields[field_name]["text"] = str(getattr(self, field_name))
        return empty_fields
    
class Documento(models.Model):
    file = models.FileField(verbose_name="File", upload_to="documenti/")
    nome = models.CharField(verbose_name="Nome File", blank=True, null=True, max_length=255, default="")
    fields = models.JSONField(verbose_name="Campi", null=True, blank=True)
    # fields structure:
    # {
    #     "AnagraficaDefunto.nomeCampo1": {"x": 100, "y": 700, "info":{...}},
    #     "AnagraficaDefunto.nomeCampo2": {"x": 400, "y": 700, "info":{...}},
    #     ...
    # }

    def __str__(self):
        return self.file.name.split("/")[-1]  # mostra solo il nome del file
    
    def save(self, *args, **kwargs):
        if not self.fields:  # solo alla creazione
            self.fields = self._genera_config()
        super().save(*args, **kwargs)
    
    def _genera_config(self):
        """
        Genera un dizionario con i campi del modello come chiavi principali,
        ognuno con la stessa struttura interna.
        """
        from .models import AnagraficaDefunto

        struttura_base = {
            "x": 0,
            "y": 0,
            "info": {
                "active": False,
                "invert_y": True,
                "font": "Helvetica",
                "size": 14,}
        }

        config = {}
        for field in AnagraficaDefunto._meta.get_fields():
            if field.concrete and not field.many_to_many and not field.is_relation:
                config[field.name] = struttura_base.copy()

        return config
