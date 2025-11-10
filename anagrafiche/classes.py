import tempfile
import numpy as np
import pytesseract
import cv2
import os
from django.conf import settings

import imutils
from imutils import perspective
from imutils.contours import sort_contours

DEBUG=False
## Set environment parameter to permit pytesseract to find the trained files
# os.environ["TESSDATA_PREFIX"] = os.path.join(settings.BASE_DIR, "tessdata")

# helper per ordinare punti quadrilatero
def order_points(pts):
    # pts: (4,2) o più punti
    rect = np.zeros((4,2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

# semplice 4 point transform (usata come fallback)
def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

class MrzReader(object):
    """
    The aim of this class is to translate a generic picture of a CIE ID in a dictionary of 
    informations. 
    This specific way of reach this goal is abbandoned because it would represent a too complex 
    and deep spin-off of the main project and surelly higer in value. 
    New path are going to be walked: 
    1) use passporteye
    2) use Amazon Textract https://aws.amazon.com/textract/pricing/
    3) use docTR
    """
    SINGLE_CHAR_SEGMENTATION = False
    # ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<
    l = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    n = "0123456789"
    z = "<"
    t = "ABCDEFGHIJKLMNOPQRSTUVWXYZ<"
    TESSEDIT_CHAR_WHITELIST=(
        (l,z,l,l,l,l,l,n,n,n,n,n,l,l,n,z,z,z,z,z,z,z,z,z,z,z,z,z,z,z),
        (n,n,n,n,n,n,n,l,n,n,n,n,n,n,n,l,l,l,z,z,z,z,z,z,z,z,z,z,z,n),
        (t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t)
    )
    TESSEDIT_CHAR_SKIP=(
        (0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
        (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0),
        (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    )
    CHAR_CUT_MAP = (
        0,23,52,77,104,134,160,188,216,243,
        271,298,326,354,381,408,436,462,491,519,
        546,574,602,629,656,683,711,739,766,794,818
    )
    data = {}
    
    def __init__(self, image_file) -> None:
        # Init configs
        ## Use trained model found here https://github.com/DoubangoTelecom/tesseractMRZ/tree/master
        # config = f"--oem 1 --psm 10 -c tessedit_char_whitelist={charset}"
        tessdata_path = os.path.join(settings.BASE_DIR, "anagrafiche", "tessdata")
        self.TESS_CHAR_CONFIG = lambda charset: f'\
            --tessdata-dir "{tessdata_path}" \
            -l mrz_best \
            --psm 10 \
            -c load_system_dawg=0 \
            -c load_freq_dawg=0 \
            -c tessedit_char_whitelist={charset}'
        self.TESS_CARD_CONFIG = f'\
            --tessdata-dir "{tessdata_path}" \
            -l mrz_best \
            --psm 6 \
            -c load_system_dawg=0 \
            -c load_freq_dawg=0 \
            -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            for chunk in image_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
            image = cv2.imread(tmp_path)
        # image = self._image_resize(image)
        # image = self._detect_card(image)
        image = self._rectify_card_by_peak_edges(image)
        if DEBUG:
            cv2.imshow("image", image)
            cv2.waitKey(0)
        image = self._detect_mrz(image)
        image = self._refine_mrz_region(image)
        if self.SINGLE_CHAR_SEGMENTATION:
            image = self._enhance_mrz_contrast(image)
            lines_chars = self._segment_mrz(image)
            text = self._read_segmented_text(lines_chars)
        else:
            text = self._read_text(image)
        print(text)
        self.data = self._parse_text(text)

    def _image_resize(self, image, max_dim=800):
        h, w = image.shape[:2]
        scale = max_dim / max(h, w)
        if scale < 1:
            image = cv2.resize(image, (int(w*scale), int(h*scale)))
        if DEBUG:
            cv2.imshow("resized", image)
            cv2.waitKey(0)
        return image

    def _detect_card(self, image):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)
        th = cv2.adaptiveThreshold(L, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            35, 10
        )
        if DEBUG:
            cv2.imshow("adaptiveThreshold", th)
            cv2.waitKey(0)

        cnts, _ = cv2.findContours(th, cv2.RETR_TREE , cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=lambda cnt:(cv2.contourArea(cnt),len(cnt)), reverse=True)
        card_vertex = None
        for cnt in cnts:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            # if DEBUG:
            #     test_image = image.copy()
            #     cv2.drawContours(test_image, cnt, -1, (0,255,0), 2)
            #     cv2.imshow("warped", test_image)
            #     cv2.waitKey(0)
            if len(approx) != 4:
                # print("Troppi punti")
                continue
            # bounding box del contorno
            x, y, w, h = cv2.boundingRect(approx)
            # calcolo rapporto d'aspetto (larghezza / altezza)
            ratio = w / float(h)
            # range accettabile per la CIE
            if 1.4 < ratio < 1.7:
                # trovato un contorno plausibile della carta
                card_vertex = approx
                break

        if card_vertex is None:
            raise ValueError("Impossibile individuare la carta nella foto")
        if DEBUG:
            test_image = image.copy()
            cv2.drawContours(test_image, cnt, -1, (0,0,255), 4)
            cv2.imshow("warped", test_image)
            cv2.waitKey(0)
        if DEBUG:
            test_image = image.copy()
            cv2.drawContours(test_image, approx, -1, (0,0,255), 4)
            cv2.imshow("warped", test_image)
            cv2.waitKey(0)
        pts = card_vertex.reshape(4, 2)
        # ordina i punti TL, TR, BR, BL
        rect = perspective.order_points(pts)
        warped = perspective.four_point_transform(image, rect)
        if DEBUG:
            cv2.imshow("warped", warped)
            cv2.waitKey(0)

        return warped
    
    def _rectify_card_by_peak_edges(self,image,
                               max_size=1200,
                               min_area_ratio=0.05,
                               contour_area_threshold=0.01,
                               expected_ar=1.42,      # rapporto width/height atteso per la carta (es. CIE ~?)
                               ar_tolerance=0.5,
                               hist_bins=200,
                               peak_window=5,
                               peak_prominence_ratio=0.2,
                               debug=False):
        """
        Raddrizza la carta trovando i 4 lati tramite istogrammi delle x e y dei punti del contorno.
        Ritorna (warped, dst_quad) oppure (None, None) se fallisce.
        Parametri di ingresso da adattare:
        - max_size: ridimensiona lato maggiore per velocità/stabilità
        - min_area_ratio: area contorno minima rispetto all'immagine per considerare contorno candidato
        - expected_ar / ar_tolerance: rapporto larghezza/altezza atteso e tolleranza per scartare contorni
        - hist_bins: numero di bin per gli istogrammi su x e y
        - peak_window: finestra per smoothing dell'istogramma
        - peak_prominence_ratio: soglia per ignorare picchi troppo piccoli
        """
        H0, W0 = image.shape[:2]
        # 1) ridimensionamento se troppo grande (mantieni aspect ratio)
        scale = 1.0
        if max(H0, W0) > max_size:
            scale = max_size / float(max(H0, W0))
            image = cv2.resize(image, (int(W0*scale), int(H0*scale)), interpolation=cv2.INTER_AREA)
        H, W = image.shape[:2]

        # preprocessing semplice (adatta se serve)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # dilata per unire eventuali gap
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        edges = cv2.dilate(edges, kernel, iterations=1)

        # trova contorni
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)
        th = cv2.adaptiveThreshold(L, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            35, 10
        )
        if DEBUG:
            cv2.imshow("adaptiveThreshold", th)
            cv2.waitKey(0)

        cnts, _ = cv2.findContours(th, cv2.RETR_TREE , cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=lambda cnt:(cv2.contourArea(cnt),len(cnt)), reverse=True)
        card_vertex = None
        candidate = None
        for cnt in cnts:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            # if DEBUG:
            #     test_image = image.copy()
            #     cv2.drawContours(test_image, cnt, -1, (0,255,0), 2)
            #     cv2.imshow("warped", test_image)
            #     cv2.waitKey(0)
            if len(approx) != 4:
                # print("Troppi punti")
                continue
            # bounding box del contorno
            x, y, w, h = cv2.boundingRect(approx)
            # calcolo rapporto d'aspetto (larghezza / altezza)
            ratio = w / float(h)
            # range accettabile per la CIE
            if 1.4 < ratio < 1.7:
                # trovato un contorno plausibile della carta
                card_vertex = approx
                candidate = cnt
                break

        if candidate is None:
            # fallback: prendi il contorno più grande
            candidate = cnts[0]

        # estrai i punti del contorno su coordinate scalate originali dell'immagine ridimensionata
        pts = candidate.reshape(-1,2)

        # 2) costruisci istogrammi su x e su y
        xs = pts[:,0]
        ys = pts[:,1]

        def smooth(v, k=peak_window):
            kernel = np.ones(k)/k
            return np.convolve(v, kernel, mode='same')

        hist_x, bin_edges_x = np.histogram(xs, bins=hist_bins, range=(0, W))
        hist_y, bin_edges_y = np.histogram(ys, bins=hist_bins, range=(0, H))

        hist_x_s = smooth(hist_x)
        hist_y_s = smooth(hist_y)

        # trova i due picchi principali in ciascun istogramma (top2 peaks)
        def top2_peaks(hist):
            idxs = np.argsort(hist)[::-1]
            if len(idxs) < 2:
                return idxs[:2]
            return idxs[:2]

        px = top2_peaks(hist_x_s)
        py = top2_peaks(hist_y_s)

        # prominenza minima per considerare un picco valido
        prom_thresh_x = hist_x_s.max() * peak_prominence_ratio
        prom_thresh_y = hist_y_s.max() * peak_prominence_ratio
        if hist_x_s[px[0]] < prom_thresh_x or hist_x_s[px[1]] < prom_thresh_x or \
        hist_y_s[py[0]] < prom_thresh_y or hist_y_s[py[1]] < prom_thresh_y:
            if debug: print("Peak too small, fallback a minAreaRect")
            # fallback: usa minAreaRect
            rect = cv2.minAreaRect(candidate)
            box = cv2.boxPoints(rect).astype("int")
            # ordina i punti e restituisci
            box = order_points(box)
            warped = four_point_transform(image, box)
            # scala verso dimensione originale
            if scale != 1.0:
                warped = cv2.resize(warped, (int(warped.shape[1]/scale), int(warped.shape[0]/scale)), interpolation=cv2.INTER_CUBIC)
            return warped, box

        # mappa bin index -> coordinate
        def bin_to_coord(bin_idx, bin_edges):
            c0 = bin_edges[bin_idx]
            c1 = bin_edges[bin_idx+1]
            return (c0 + c1) / 2.0

        # ottieni coordinate centro dei due picchi
        x_peak_coords = [bin_to_coord(i, bin_edges_x) for i in px]
        y_peak_coords = [bin_to_coord(i, bin_edges_y) for i in py]

        # ordina in modo che x_left < x_right e y_top < y_bottom
        x_left, x_right = sorted(x_peak_coords)
        y_top, y_bottom = sorted(y_peak_coords)

        if debug:
            print("x peaks:", x_left, x_right, "y peaks:", y_top, y_bottom)

        # 3) isola punti appartenenti ai picchi: prendi punti con x vicino ai due picchi e y vicino ai due picchi
        # definisci tolleranza in pixel come frazione della dimensione
        tol_x = max(3, int(W / hist_bins * 3))
        tol_y = max(3, int(H / hist_bins * 3))

        left_pts = pts[np.abs(pts[:,0] - x_left) <= tol_x]
        right_pts = pts[np.abs(pts[:,0] - x_right) <= tol_x]
        top_pts = pts[np.abs(pts[:,1] - y_top) <= tol_y]
        bottom_pts = pts[np.abs(pts[:,1] - y_bottom) <= tol_y]

        # fallback se non ci sono punti sufficienti
        min_pts = 10
        if len(left_pts) < min_pts or len(right_pts) < min_pts or len(top_pts) < min_pts or len(bottom_pts) < min_pts:
            if debug: print("Non abbastanza punti nei picchi, fallback minAreaRect")
            rect = cv2.minAreaRect(candidate)
            box = cv2.boxPoints(rect).astype("int")
            box = order_points(box)
            warped = four_point_transform(image, box)
            if scale != 1.0:
                warped = cv2.resize(warped, (int(warped.shape[1]/scale), int(warped.shape[0]/scale)), interpolation=cv2.INTER_CUBIC)
            return warped, box

        # 4) fitta una retta a ciascun insieme con np.polyfit (y = m*x + b) o x = m*y + b per rette verticali
        def fit_line_pts(pts_set):
            # fit x = a*y + b if varianza y maggiore, altrimenti y = a*x + b
            if pts_set.shape[0] < 2:
                return None
            vx = np.std(pts_set[:,0])
            vy = np.std(pts_set[:,1])
            if vy > vx:
                # x = a*y + b  -> polyfit(y, x)
                a, b = np.polyfit(pts_set[:,1], pts_set[:,0], 1)
                # ritorna funzione che prende y e restituisce x
                return lambda y: a*y + b
            else:
                # y = a*x + b
                a, b = np.polyfit(pts_set[:,0], pts_set[:,1], 1)
                return lambda x: a*x + b

        left_line = fit_line_pts(left_pts)
        right_line = fit_line_pts(right_pts)
        top_line = fit_line_pts(top_pts)
        bottom_line = fit_line_pts(bottom_pts)

        if None in (left_line, right_line, top_line, bottom_line):
            if debug: print("Fit line failed, fallback minAreaRect")
            rect = cv2.minAreaRect(candidate)
            box = cv2.boxPoints(rect).astype("int")
            box = order_points(box)
            warped = four_point_transform(image, box)
            if scale != 1.0:
                warped = cv2.resize(warped, (int(warped.shape[1]/scale), int(warped.shape[0]/scale)), interpolation=cv2.INTER_CUBIC)
            return warped, box

        # calcola 4 intersezioni: top-left, top-right, bottom-right, bottom-left
        def intersect(f1, f2, var='xy'):
            # se f1 è funzione x(y) e f2 è y(x) o viceversa, bisogna risolvere
            # proviamo due approcci: cerca y tale che x1(y) == x2(y) se entrambe x(y)
            # per semplicità, risolveremo numericamente cercando punto in range
            # alternative più precise: esprimere entrambe come y = a*x + b se possibile
            # implementazione semplice: risolvi per y su range 0..H
            ys = np.linspace(0, H-1, 1000)
            x1 = np.array([f1(y) if callable(f1) else f1(y) for y in ys])
            x2 = np.array([f2(y) if callable(f2) else f2(y) for y in ys])
            idx = np.argmin(np.abs(x1 - x2))
            y = ys[idx]
            x = 0.5*(x1[idx] + x2[idx])
            return np.array([x, y])

        # intersections:
        tl = intersect(left_line, top_line)
        tr = intersect(right_line, top_line)
        br = intersect(right_line, bottom_line)
        bl = intersect(left_line, bottom_line)

        src_quad = np.array([tl, tr, br, bl], dtype="float32")

        # sanity: assicurati che i punti siano dentro l'immagine
        src_quad[:,0] = np.clip(src_quad[:,0], 0, W-1)
        src_quad[:,1] = np.clip(src_quad[:,1], 0, H-1)

        # ordina i punti in ordine top-left, top-right, bottom-right, bottom-left
        src_quad = order_points(src_quad)

        # compute destination size based on distances
        (tl, tr, br, bl) = src_quad
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = int(max(widthA, widthB))
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = int(max(heightA, heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(src_quad, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        # ridimensiona al formato originale se necessario
        if scale != 1.0:
            warped = cv2.resize(warped, (int(warped.shape[1]/scale), int(warped.shape[0]/scale)), interpolation=cv2.INTER_CUBIC)

        return warped, src_quad

    def _detect_mrz(self, image):
        # load the input image, convert it to grayscale, and grab its
        # dimensions    
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        (H, W) = gray.shape
        # initialize a rectangular and square structuring kernel
        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
        sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
        # smooth the image using a 3x3 Gaussian blur and then apply a
        # blackhat morpholigical operator to find dark regions on a light
        # background
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
        if DEBUG:
            cv2.imshow("Blackhat", blackhat)
            cv2.waitKey(0)
        # compute the Scharr gradient of the blackhat image and scale the
        # result into the range [0, 255]
        grad = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        grad = np.absolute(grad)
        (minVal, maxVal) = (np.min(grad), np.max(grad))
        grad = (grad - minVal) / (maxVal - minVal)
        grad = (grad * 255).astype("uint8")
        if DEBUG:
            cv2.imshow("Gradient", grad)
            cv2.waitKey(0)
        # apply a closing operation using the rectangular kernel to close
        # gaps in between letters -- then apply Otsu's thresholding method
        grad = cv2.morphologyEx(grad, cv2.MORPH_CLOSE, rectKernel)
        thresh = cv2.threshold(grad, 0, 255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if DEBUG:
            cv2.imshow("Rect Close", thresh)
            cv2.waitKey(0)
        # perform another closing operation, this time using the square
        # kernel to close gaps between lines of the MRZ, then perform a
        # series of erosions to break apart connected components
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
        thresh = cv2.erode(thresh, None, iterations=2)
        if DEBUG:
            cv2.imshow("Square Close", thresh)
            cv2.waitKey(0)

        # find contours in the thresholded image and sort them from bottom
        # to top (since the MRZ will always be at the bottom of the passport)
        cnts = cv2.findContours(
            thresh.copy(), 
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sort_contours(cnts, method="bottom-to-top")[0]
        # initialize the bounding box associated with the MRZ
        mrzBox = None
        # loop over the contours
        for c in cnts:
            # compute the bounding box of the contour and then derive the
            # how much of the image the bounding box occupies in terms of
            # both width and height
            (x, y, w, h) = cv2.boundingRect(c)
            percentWidth = w / float(W)
            percentHeight = h / float(H)
            # if the bounding box occupies > 80% width and > 4% height of the
            # image, then assume we have found the MRZ
            if percentWidth > 0.8 and percentHeight > 0.04:
                mrzBox = (x, y, w, h)
                break
        # if the MRZ was not found, exit the script
        if mrzBox is None:
            raise ValueError("Impossibile trovare la zona di testo leggibile")
        # pad the bounding box since we applied erosions and now need to
        # re-grow it
        (x, y, w, h) = mrzBox
        pX = int((x + w) * 0.03)
        pY = int((y + h) * 0.03)
        (x, y) = (x - pX, y - pY)
        (w, h) = (w + (pX * 2), h + (pY * 2))
        # extract the padded MRZ from the image
        mrz_region = image[y:y + h, x:x + w]
        # show the MRZ image
        if DEBUG:
            cv2.imshow("MRZ", mrz_region)
            cv2.waitKey(0)
        
        ## Ulteriore elaborazione della zona ritagliata ##
        # gray = cv2.cvtColor(mrz_region, cv2.COLOR_BGR2GRAY)
        # rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
        # gray = cv2.GaussianBlur(gray, (3, 3), 3)
        # blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
        # if DEBUG:
        #     cv2.imshow("Blackhat", blackhat)
        #     cv2.waitKey(0)
        # mrz_region = blackhat

        return mrz_region

    def _refine_mrz_region(self, mrz_region):
        # assumiamo che self.mrz_region sia in BGR o gray
        gray = cv2.cvtColor(mrz_region, cv2.COLOR_BGR2GRAY) if len(mrz_region.shape) == 3 else mrz_region

        # threshold forte per isolare lettere
        _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # trova i contorni
        cnts = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cv2.convexHull(cnts[0]) if len(cnts) == 1 else cnts[0]

        # costruisci il bounding box totale delle lettere
        xs = []
        ys = []
        ws = []
        hs = []
        for c in cnts:
            x,y,w,h = cv2.boundingRect(c)
            xs.append(x)
            ys.append(y)
            ws.append(x+w)
            hs.append(y+h)

        # bounding box globale
        x1 = max(min(xs)-2, 0)
        y1 = max(min(ys)-2, 0)
        x2 = min(max(ws)+2, mrz_region.shape[1])
        y2 = min(max(hs)+2, mrz_region.shape[0])

        refined = mrz_region[y1:y2, x1:x2]

        if DEBUG:
            cv2.imshow("MRZ refined", refined)
            cv2.waitKey(0)

        return refined

    def _enhance_mrz_contrast(self,image):
        # Converti in spazio colore Lab
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)
        # Il testo è quasi neutro → bassi valori di saturazione colore.
        # Calcoliamo una "mappa colore" per isolare lo sfondo.
        color_distance = np.sqrt((A - 128)**2 + (B - 128)**2).astype('uint8')
        # Normalizzazione per ottenere una maschera
        color_distance = cv2.normalize(color_distance, None, 0, 255, cv2.NORM_MINMAX)
        # Invertiamo: testo = bianco, sfondo colorato = nero
        _, fg_mask = cv2.threshold(color_distance, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # Ora usiamo solo il canale L (luminosità) ma filtrato da fg_mask
        text_only = cv2.bitwise_and(L, L, mask=fg_mask)
        # Binarizzazione finale leggera
        _, binary = cv2.threshold(text_only, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        # Pulizia / riempimento piccole lacune
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

        if DEBUG:
            cv2.imshow("MRZ enhanced", binary)
            cv2.waitKey(0)

        return binary

    def _segment_mrz(self, refined):
        # Convert to grayscale & threshold (migliora OCR)
        # gray = cv2.cvtColor(refined, cv2.COLOR_BGR2GRAY)
        # rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
        # gray = cv2.GaussianBlur(gray, (3, 3), 0)
        # blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
        # _, thresh = cv2.threshold(blackhat, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # refined = thresh

        H, W = refined.shape
        line_height = H // 3

        # Taglia le due righe
        line1 = refined[0:line_height, :]
        line2 = refined[line_height:2*line_height, :]
        line3 = refined[2*line_height:H, :]

        # Ogni riga ha 30 caratteri
        char_cut_unit = W/self.CHAR_CUT_MAP[-1]
        cut_positions = [round(ccm*char_cut_unit) for ccm in self.CHAR_CUT_MAP]
        # Substitute the last element to avoid overflows due to rounding processes
        cut_positions[-1] = W

        lines_chars = [[],[],[]]
        for i in range(30):
            # slice su larghezza
            c1 = line1[:, cut_positions[i]:cut_positions[i+1]]
            c2 = line2[:, cut_positions[i]:cut_positions[i+1]]
            c3 = line3[:, cut_positions[i]:cut_positions[i+1]]
            lines_chars[0].append(c1)
            lines_chars[1].append(c2)
            lines_chars[2].append(c3)
            if DEBUG:
                cv2.imshow("MRZ", c3)
                cv2.waitKey(0)

        return lines_chars
    
    def _ocr_character(self,image,charset="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"):
        text = pytesseract.image_to_string(
            image, 
            config=self.TESS_CHAR_CONFIG(charset)
            )
        return text.strip()
    
    def _read_segmented_text(self, lines_chars):
        mrz_text = ""
        for j in range(3):
            for i in range(30):
                if self.TESSEDIT_CHAR_SKIP[j][i]:
                    mrz_text += "<"
                else:
                    char = self._ocr_character(lines_chars[j][i],charset=self.TESSEDIT_CHAR_WHITELIST[j][i])
                    if not char or len(char)>1:
                        mrz_text += "?"
                    else:
                        mrz_text += char

                    # if j==1:
                    #     print(char)
                    #     cv2.imshow("MRZ", lines_chars[j][i])
                    #     cv2.waitKey(0)
            mrz_text += "\n"
        return mrz_text
    
    def _read_text(self,image):
        mrz_text = pytesseract.image_to_string(
            image, 
            config=self.TESS_CARD_CONFIG
            )
        return mrz_text

    def _parse_text(self,mrz_text):
        ## Normalizza il testo ##

        lines = mrz_text.splitlines()
        lines = [l.strip() for l in lines if l.strip()]
        if len(lines) < 3:
            raise ValueError("Il testo identificato non è valido")
        l1, l2, l3 = lines

        name_block = l1[5:]
        surname, given_names = name_block.split("<<", 1)
        data = {
            "mrz" : mrz_text.replace(" ", "").replace("\n", ""),
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

        return data
    
    # Convertiamo date in formato ISO (facilita frontend)
    def convert_date(self, s):
        try:
            # s arriva in formato YYMMDD
            y = int(s[0:2])
            y = 1900+y if y > 30 else 2000+y
            return f"{y}-{s[2:4]}-{s[4:6]}"
        except Exception as exc:
            return None
    

    # def _detect_mrz(self):
    #     gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
    #     blur = cv2.GaussianBlur(gray, (5,5), 0)

    #     # evidenzia le linee di testo
    #     sobel = cv2.Sobel(blur, cv2.CV_8U, 1, 0, ksize=3)
    #     _, thresh = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    #     # raggruppa blocchi di testo
    #     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    #     dilated = cv2.dilate(thresh, kernel, iterations=2)

    #     # trova contorni
    #     contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #     h, w = self.img.shape[:2]
    #     candidates = []

    #     for c in contours:
    #         x, y, cw, ch = cv2.boundingRect(c)
    #         if y > h * 0.4 and cw > w * 0.5 and ch < h * 0.25:
    #             candidates.append((x, y, cw, ch))
    #     if not candidates:
    #         raise ValueError("Impossibile trovare la zona di testo leggibile")
    #     # prendiamo il più largo (di solito è l'MRZ)
    #     x,y,cw,ch = max(candidates, key=lambda r: r[2])
    #     # crop area MRZ
    #     self.mrz_region = self.img[y:y+ch, x:x+cw]