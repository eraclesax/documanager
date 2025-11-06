import cv2 , pytesseract, tempfile

class MrzReader(object):
    img = None
    x,y,cw,ch = None, None, None, None
    text = ""
    data = {}
    
    def __init__(self, image_file) -> None:

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            for chunk in image_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
            self.img = cv2.imread(tmp_path)

        self._detect_mrz()
        self._read_text()
        self._parse_text()
        
    def _detect_mrz(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)

        # evidenzia le linee di testo
        sobel = cv2.Sobel(blur, cv2.CV_8U, 1, 0, ksize=3)
        _, thresh = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        # raggruppa blocchi di testo
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=2)

        # trova contorni
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h, w = self.img.shape[:2]
        candidates = []

        for c in contours:
            x, y, cw, ch = cv2.boundingRect(c)
            if y > h * 0.4 and cw > w * 0.5 and ch < h * 0.25:
                candidates.append((x, y, cw, ch))
        if not candidates:
            raise ValueError("Impossibile trovare la zona di testo leggibile")
        
        # prendiamo il più largo (di solito è l'MRZ)
        self.x, self.y, self.cw, self.ch = max(candidates, key=lambda r: r[2])
    
    def _read_text(self):
        # crop area MRZ
        x,y,cw,ch = self.x, self.y, self.cw, self.ch
        mrz_region = self.img[y:y+ch, x:x+cw]
        mrz_text = pytesseract.image_to_string(
            mrz_region,
            config="--oem 1 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
        )
        self.text = mrz_text

    def _parse_text(self):
        ## Normalizza il testo ##
        lines = self.text.splitlines()
        lines = [l.strip() for l in lines if l.strip()]
        if len(lines) < 3:
            raise ValueError("Il testo identificato non è valido")
        l1, l2, l3 = lines

        name_block = l1[5:]
        surname, given_names = name_block.split("<<", 1)

        data = {
            "mrz" : self.text.replace(" ", "").replace("\n", ""),
            ## Riga 1 ##
            "doc_type" : l1[0],
            "issuing_state" : l1[2:5],
            "surname" : surname.replace("<", " "),
            "given_names" : given_names.replace("<", " ").strip(),
            ## Riga 2 ##
            "document_number" : l2[0:9].replace("<", ""),
            "birth_date" : self.convert_date(l2[13:19]),
            "sex" : l2[20],
            "expiry_date" : self.convert_date(l2[21:27]),
            ## Riga 3 ##
            "codice_fiscale" : l3.replace("<", ""),
        }

        self.data = data
    
    # Convertiamo date in formato ISO (facilita frontend)
    def convert_date(self, s):
        # s arriva in formato YYMMDD
        y = int(s[0:2])
        y = 1900+y if y > 30 else 2000+y
        return f"{y}-{s[2:4]}-{s[4:6]}"