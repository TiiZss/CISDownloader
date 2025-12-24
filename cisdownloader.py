import os
import time
import requests
import re
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN ---
# Enlace de acceso a la página de descargas de CIS
URL_ACCESO = "https://learn.cisecurity.org/e/799323/l-799323-2020-07-20-28mnm/2mnqr/2612638360/h/vT9Eq0qyyuhceegtopg1OtS3XKkPOra3-DACmrif5pU"
CARPETA_BASE = "CIS_Benchmarks"

# SELECTORES ACTUALIZADOS (VERIFICADO EN URL DIRECTA)
SELECTOR_TARJETA = "div.well.section" # Contenedor principal de cada grupo (ej. Alibaba Cloud)
SELECTOR_HEADER = ".header"         # La cabecera clickeable para expandir
SELECTOR_TITULO_CAT = "p.h4"        # Nombre de la categoría
SELECTOR_ITEM_ROW = "li.list-group-item" # Cada fila de benchmark dentro de la categoría
SELECTOR_TITULO_FILE = "p.h5"       # Nombre específico del benchmark
SELECTOR_BOTON = "a.cta_button"     # El botón de descarga

def sanear_nombre(nombre):
    """Limpia caracteres inválidos para nombres de carpeta/archivo."""
    return "".join([c for c in nombre if c.isalnum() or c in (' ', '-', '_', '.')]).strip()

def obtener_nombre_archivo_desde_cd(cd_header):
    """Extrae el nombre de archivo del header Content-Disposition si existe."""
    if not cd_header:
        return None
    fname = re.findall('filename="?([^"]+)"?', cd_header) 
    if not fname:
        fname = re.findall(r"filename\*=UTF-8''(.+)", cd_header)
    if fname:
        return fname[0]
    return None

def parse_benchmark_version(title):
    """
    Parsea el título (ej: 'CIS Benchmark v1.2.0') para separar nombre base y versión.
    Devuelve (nombre_base, tupla_version).
    """
    # Busca patrones tipo ' v1.2', ' v1.2.3', ' V2.0' al final o en medio
    match = re.search(r'(.+?)\s+[vV](\d+(?:\.\d+)+)', title)
    if match:
        name = match.group(1).strip()
        version_str = match.group(2)
        try:
            # Convertir '1.2.0' a (1, 2, 0)
            version_tuple = tuple(map(int, version_str.split('.')))
            return name, version_tuple
        except:
            pass
    return title.strip(), (0,)

# Función para esperar que termine la descarga
def esperar_descarga(carpeta, timeout=60):
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < timeout:
        # Buscar archivos recientes no temporales (.crdownload, .tmp)
        archivos = [f for f in os.listdir(carpeta) if not f.endswith('.crdownload') and not f.endswith('.tmp')]
        # Si encontramos al menos uno nuevo (asumimos carpeta vacía o controlada, 
        # pero para ser precisos deberíamos ver cambios. Aquí simplificamos esperando que haya crecido la lista)
        # Una mejor estrategia: esperar a que NO haya .crdownload
        if any(f.endswith('.crdownload') for f in os.listdir(carpeta)):
            time.sleep(1)
            continue
        return True
    return False

def formatear_nombre_archivo(carpeta, titulo_benchmark):
    """
    Busca el archivo más reciente en la carpeta y lo renombra con el título del benchmark
    para que quede limpio y legible.
    """
    try:
        # Dar un momento al FS
        time.sleep(2)
        archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta)]
        if not archivos:
            return

        # Archivo más reciente
        archivo_mas_reciente = max(archivos, key=os.path.getctime)
        if not os.path.isfile(archivo_mas_reciente):
            return

        _, ext = os.path.splitext(archivo_mas_reciente)
        if ext.lower() not in ['.pdf', '.zip']:
            return # No tocar cosas raras

        nuevo_nombre = sanear_nombre(titulo_benchmark) + ext
        nueva_ruta = os.path.join(carpeta, nuevo_nombre)

        # Evitar sobrescribir o errores si ya se llama así
        if archivo_mas_reciente != nueva_ruta:
            # Si ya existe el destino, borrarlo o añadir sufijo (aquí reemplazamos)
            if os.path.exists(nueva_ruta):
                os.remove(nueva_ruta)
            os.rename(archivo_mas_reciente, nueva_ruta)
            print(f"[RENOMBRADO] -> {nuevo_nombre}")
    except Exception as e:
        print(f"[WARN] No se pudo renombrar el archivo: {e}")

def main():
    # Carpeta absoluta para descargas (Chrome requiere rutas absolutas)
    base_abs = os.path.abspath(CARPETA_BASE)
    if not os.path.exists(base_abs):
        os.makedirs(base_abs)

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") 
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Preferencias para activar descarga automática y sin visor PDF
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True, # Importante: no abrir PDF en Chrome
        "profile.default_content_settings.popups": 0,
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"Navegando a: {URL_ACCESO}")
        driver.get(URL_ACCESO)
        time.sleep(5) 
        
        # Cookies
        try:
            print("Verificando cookies...")
            btn_cookie = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            if btn_cookie.is_displayed():
                btn_cookie.click()
                time.sleep(1)
        except:
            pass 

        print("Esperando lista de categorías...")
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_TARJETA)))
        
        tarjetas = driver.find_elements(By.CSS_SELECTOR, SELECTOR_TARJETA)
        print(f"Se encontraron {len(tarjetas)} categorías.")

        for tarjeta in tarjetas:
            try:
                # 1. Preparar carpeta
                header = tarjeta.find_element(By.CSS_SELECTOR, SELECTOR_HEADER)
                titulo_cat = header.find_element(By.CSS_SELECTOR, SELECTOR_TITULO_CAT).text
                nombre_carpeta = sanear_nombre(titulo_cat)
                ruta_carpeta = os.path.join(base_abs, nombre_carpeta)
                
                if not os.path.exists(ruta_carpeta):
                    os.makedirs(ruta_carpeta)

                print(f"\n--- Procesando: {nombre_carpeta} ---")

                # 2. Configurar Chrome para descargar en ESTA carpeta
                # Usamos CDP (Chrome DevTools Protocol) para cambiar la ruta al vuelo
                driver.execute_cdp_cmd("Page.setDownloadBehavior", {
                    "behavior": "allow",
                    "downloadPath": ruta_carpeta
                })

                # 3. Expandir
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", header)
                time.sleep(0.5)
                try:
                    header.click()
                    time.sleep(1) 
                except:
                    driver.execute_script("arguments[0].click();", header)
                    time.sleep(1)

                # 4. Analizar ítems
                filas = tarjeta.find_elements(By.CSS_SELECTOR, SELECTOR_ITEM_ROW)
                if not filas:
                    print("  No se encontraron archivos.")
                    continue

                print(f"  Analizando {len(filas)} items...")
                dict_versiones = {}

                for fila in filas:
                    try:
                        # Necesitamos el elemento 'a' para el binding de Selenium luego
                        btn = fila.find_element(By.CSS_SELECTOR, SELECTOR_BOTON)
                        url_descarga = btn.get_attribute('href')
                        titulo_bench = fila.find_element(By.CSS_SELECTOR, SELECTOR_TITULO_FILE).text.strip()
                        
                        if not url_descarga: continue
                        
                        nombre_base, ver_tuple = parse_benchmark_version(titulo_bench)
                        tiene_pk_vid = "pk_vid=" in url_descarga

                        if nombre_base in dict_versiones:
                            campeon = dict_versiones[nombre_base]
                            es_mayor = ver_tuple > campeon['ver']
                            es_igual_pk = (ver_tuple == campeon['ver']) and tiene_pk_vid and not campeon['con_pk']
                            
                            if es_mayor or es_igual_pk:
                                dict_versiones[nombre_base] = {
                                    'ver': ver_tuple,
                                    'element': btn, # Guardamos el elemento Web para hacer click
                                    'titulo': titulo_bench,
                                    'con_pk': tiene_pk_vid
                                }
                        else:
                            dict_versiones[nombre_base] = {
                                'ver': ver_tuple,
                                'element': btn,
                                'titulo': titulo_bench,
                                'con_pk': tiene_pk_vid
                            }
                    except:
                        continue
                
                # 5. Descargar los ganadores
                print(f"  Descargando {len(dict_versiones)} archivos...")
                for key, data in dict_versiones.items():
                    titulo = data['titulo']
                    
                    # Verificar si ya tenemos un PDF con ese nombre "saneado"
                    nombre_final_aprox = sanear_nombre(titulo) + ".pdf"
                    if os.path.exists(os.path.join(ruta_carpeta, nombre_final_aprox)):
                        print(f"  [EXISTE] {nombre_final_aprox}")
                        continue
                    
                    try:
                        print(f"  [CLICK] Descargando: {titulo}")
                        # Click nativo
                        # A veces el elemento pierde referencia si el DOM cambia, volver a buscarlo si falla
                        # pero usualmente en este bucle corto aguanta.
                        # Scroll para asegurar visibilidad
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", data['element'])
                        time.sleep(random.uniform(1.0, 2.0))
                        
                        # Click JS es más seguro contra overlays
                        driver.execute_script("arguments[0].click();", data['element'])
                        
                        # Esperar un poco a que arranque
                        time.sleep(2)
                        # Esperar a que termine de descargar (sin .crdownload)
                        esperar_descarga(ruta_carpeta, timeout=120)
                        
                        # Renombrar lo que haya bajado
                        formatear_nombre_archivo(ruta_carpeta, titulo)
                        
                        # Pausa anti-bot
                        time.sleep(random.uniform(2, 4))
                        
                    except Exception as e_dl:
                        print(f"  [ERROR] Falló descarga Selenium: {e_dl}")

            except Exception as e_cat:
                print(f"Error procesando tarjeta: {e_cat}")

    except Exception as e_main:
        print(f"Error fatal en el script ({type(e_main).__name__}): {e_main}")
        try:
            driver.save_screenshot("error_screenshot.png")
            print("Captura guardada.")
        except:
            pass
    finally:
        driver.quit()
        print("\nEjecución finalizada.")

if __name__ == "__main__":
    main()