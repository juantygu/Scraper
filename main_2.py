from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import pandas as pd
import numpy as np
import time
import re
import openpyxl
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from timeout_function_decorator import timeout
from pathlib import Path
import requests
import tkinter as tk
from tkinter import ttk, filedialog
import sys
from subprocess import CREATE_NO_WINDOW
class Scraperexeption(Exception):
    pass
class VurScraper():

    def __init__(self,archivo=None,matricula_individual=None,matricula_array=None,circulo_registral=None,usuario=None,contrasena=None):
        self.detener = False
        self.pausado = False
        self.finalizado = False
        self.matricula_actual = None
        self.matricula_no_encontrada = "No se econtro la matricula"
        self.ruta_archivo_salida = None
        self.indice_actual = 0
        self.df = None
        self.municipio_seleccionado = circulo_registral
        self.usuario = usuario
        self.contrasena = contrasena


        if archivo:
            self.cargar_matriculas_desde_archivo(archivo)
        elif matricula_individual:
            self.matriculas= [matricula_individual]
            self.total_matriculas = 1
        elif matricula_array:
            self.matriculas = matricula_array
            self.total_matriculas =len(self.matriculas)


        # === DEFINIR LAS COLUMNAS DEL ARCHIVO CONSOLIDADO Y EL TAMAÑO DEL ARRAY DONDE VAN LO DATOS  ===
        self.columnas = ["MATRICULA", "ANOTACION", "Doc", "FECHA", "PRECIO", "ESPECIFICACION", "DE", "A"]
        self.df = pd.DataFrame(columns=self.columnas)
        self.datos = [""] * 8
        print("3")
    def cargar_matriculas_desde_archivo(self,archivo):
        self.df = pd.read_excel(f"{archivo}")  # LEER EL ARCHIVO EN EL CUAL SE VAN A BUSCAR LAS MATRICULAS
        self.matriculas = self.df["MATRICULAS"]  # IDENTIFICAR LA COLUMNA QUE CONTIENES LOS DATOS A BUSCAR
        self.matriculas = self.matriculas.replace([np.inf, -np.inf], np.nan).dropna().astype(int)  # elimina lo valores  NO FINITOS ( CELDAS VACIAS )
        self.total_matriculas = len(self.matriculas)
        print(self.total_matriculas)

    def init_progress_bar(self, progress_bar):
        self.progress_bar = progress_bar
        self.progress_bar['maximum'] = len(self.matriculas)

    def main(self):
        index = 0 # VARIABLE QUE ME INDICA EN QUE MATRICULA
        i = 0
        while index < len(self.matriculas) and not self.detener:  # LOOP CONDICIONAL QUE ME INDICA EL FINAL DEL PROCESO
            self.verificar_pausa()# verificar estado de pausa
            try:
                self.m = self.matriculas[index]
                print(self.m)
                self.verificar_pausa()  # verificar estado de pausa
                self.inicio()
                self.verificar_pausa()  # verificar estado de pausa
                self.login()
                self.verificar_pausa()  # verificar estado de pausa
                self.getEJDI()
                self.verificar_pausa()  # verificar estado de pausa
                for i in range(index, len(self.matriculas)):
                    self.verificar_pausa()  # verificar estado de pausa
                    self.m = str(self.matriculas[i])
                    self.matricula_actual = self.m
                    self.print_matricula_actual()  # Llama al método para imprimir
                    try:
                        self.verificar_pausa()  # verificar estado de pausa
                        self.set_busqueda()
                        self.verificar_pausa()  # verificar estado de pausa
                        self.click_consultar()
                        self.verificar_pausa()  # verificar estado de pausa
                        self.extract_data()
                        self.verificar_pausa()  # verificar estado de pausa
                        self.indice_actual += 1 # para visualizar en la barra de carga en que matricula va
                    except Scraperexeption as e:
                        print(f"Dato no encontrado en la matrícula {self.m}")
                        print("Continuando con la siguiente matrícula...")
                        self.matricula_actual = self.matricula_no_encontrada
                        self.indice_actual += 1 # para visualizar en la barra de carga en que matricula va
                        index = i + 1  # Avanzar al siguiente índice
                        self.reanudar()
                        self.driver.quit()
                        break
                    except Exception as e:
                        print(f"Error en la matrícula {self.m}: {str(e)}")
                        print("Reiniciando la secuencia desde el método inicio teniendo en cuenta la matrícula actual...")
                        index = i  # Establecer el nuevo índice para continuar desde la matrícula actual
                        self.reanudar()
                        self.driver.quit()
                        break  # Salir del bucle for
                    except TimeoutError as te:
                        print(f"Error de tiempo límite en la matrícula {self.m}: {str(te)}")
                        print("Reiniciando la secuencia desde el método inicio teniendo en cuenta la matrícula actual...")
                        index = i  # Establecer el nuevo índice para continuar desde la matrícula actual
                        self.reanudar()
                        self.driver.quit()
                        break
                else:
                    index = len(self.matriculas)  # Finalizar el bucle while si se completaron todas las matrículas
            except Exception as e:
                print(f"Error en la matrícula {self.m}: {str(e)}")
                print("Reiniciando la secuencia desde el método inicio teniendo en cuenta la matrícula actual...")
                index = i  # Establecer el nuevo índice para continuar desde la matrícula actual
                self.reanudar()
                self.driver.quit()
            except TimeoutError as te:
                print(f"Error en la matrícula {self.m}: {str(te)}")
                print("Reiniciando la secuencia desde el método inicio teniendo en cuenta la matrícula actual...")
                index = i  # Establecer el nuevo índice para continuar desde la matrícula actual
                self.reanudar()
                self.driver.quit()
        self.filter()
        self.driver.quit()
        self.print_finalizado()
    def test_connection(self):
        try:
            self.response = requests.get("https://www.vur.gov.co/")
            if self.response.status_code == 200:
                return True
        except:
            return False

    def verificar_conexion(self):
        while not self.test_connection():
            print(" no hay conexion")
            time.sleep(1)
    def print_finalizado(self):
        self.finalizado = True
        print("finalizado")
    def print_matricula_actual(self):
        if self.detener:
            return
        if self.matricula_actual:
            print(f"Matrícula actual: {self.matricula_actual}")
    def detener_proceso(self):
        self.detener = True
        self.driver.quit()
    def pausar(self):
        self.pausado = True
        print("pausado")

    def verificar_pausa(self):
        while self.pausado:
            print("en pausa")
            time.sleep(1)
    def reanudar(self):
        self.pausado = False
        print("renaudado")
    def inicio (self):
        if self.detener:
            return
        #self.driver = webdriver.Chrome()
        #path = 'D:\pythonProject\librerias\chromedriver.exe'
        path = "chromedriver.exe"
        service = Service(path)
        service.creation_flags = CREATE_NO_WINDOW # VERIFICARRRRRR
        self.driver = webdriver.Chrome(service=service)

        url = ''
        self.driver.get(url)
        self.driver.maximize_window()

        print("inicio")
        # ===CHECK USER AGENT===
        check_useragent = self.driver.execute_script("return navigator.userAgent;")
        print("test user agent", check_useragent)
    def login (self):
        if self.detener:
            #sys.exit()  # Salir del programa inmediatamente
            return
        
        user = self.usuario
        password = self.contrasena
        print("login")
        # ===SECUENCIA CUANDO LA PAGINA SE LE CADUCA LA LICENCIA===
        #boton1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@id="details-button"]')))
        #boton1.click()
        #link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@id="proceed-link"]')))
        #link.click()
         # ===BUSCAR TEXT BOX===
        #caja_user = driver.find_element(by="xpath", value='//input[@name="username"]')
        # caja_password = driver.find_element(by="xpath", value='//input[@name="password"]')

        caja_user = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@name="username"]')))
        caja_password = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))

        # ===INGRESAR DATOS A LOS TEXT BOXS Y HACER CLICK===
        caja_user.send_keys(user)
        caja_password.send_keys(password)
        time.sleep(1)
        boton_iniciar_sesion = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@type="button"]')))
        boton_iniciar_sesion.click()

        time.sleep(4)

        # ===INGRESAR AL ESTADO JURIDICO DEL INMUEBLE===
    @timeout(20)
    def getEJDI(self):
        #html_code = self.driver.page_source
        #print(html_code)
        # ===drop down CONSULTA===
        if self.detener:
            #sys.exit()  # Salir del programa inmediatamente
            return

        print("getEJDI")
        time.sleep(2)
        boton_ejdi = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//li/a[@class="dropdown-toggle"]')))
        boton_ejdi.click()
        time.sleep(1)
        # ===OBJETO para hacer el movimiento del cursor===
        movimiento = ActionChains(self.driver)

        # ===etiquta consultas_juridicas ==> PRIMER MOVIMIENTO===
        consultas_juridicas = self.driver.find_element(by="xpath", value='//li[@class="dropdown-submenu"]')

        # ===etiquEta estado juridico del inmueble ==> SEGUNDO MOVIMIENTO===
        estado_juridico_del_inmueble = self.driver.find_element(by="xpath", value='//ul[@class="dropdown-menu"]//li[2]/a')

        # EJECUTAR LOS MOVIMINETOS Y HACER CLICK
        movimiento.move_to_element(consultas_juridicas).move_to_element(estado_juridico_del_inmueble).click().perform()
        time.sleep(4)

    # === set MEDELLIN SUR , DIGITAR NUMERO DE MATRICULA Y CLICK
    @timeout(40)
    def set_busqueda(self):
        if self.detener:
            #sys.exit()  # Salir del programa inmediatamente
            return

        print("set_busqueda")
        time.sleep(2)
        # === UBIRCAR EL IFRAME PARA BUSCAR LOS ELEMENTOS DESEADOS ===
        iframe = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//iframe[@id="page"]')))

        # === CAMBIAR EL SCOPE DEL DRIVER AL iframe ===
        self.driver.switch_to.frame(iframe)

        # ===  SELECCIONAR Y UBICAR LA LISTA DESPEGABLE ===
        dropdown = Select(self.driver.find_element(by="xpath", value="//select[@id='circulo']"))

        # === SELECCIONAR MEDELLIN SUR ===
        #dropdown.select_by_visible_text("ORIP - MEDELLIN SUR - ( 001 )")
        dropdown.select_by_visible_text(self.municipio_seleccionado)
        time.sleep(1)

        # === UBICAR CAJA DE TEXTO DONDE VA LA MATRICULA ===
        box_matricula = self.driver.find_element(by="xpath", value="//input[@id='matricula']")
        time.sleep(1)
        # === DIGITAR LA MATRICULA EN LA CAJA DE TEXTO ===
        max_retries = 2
        for _ in range(max_retries):
            try:
                box_matricula.clear() # limpiar caja de texto
                box_matricula.send_keys(self.m)
                time.sleep(1)
                matricula_ingresada = box_matricula.get_attribute("value")

                if matricula_ingresada == self.m:
                    # numero de matricula inresado correctamente
                    break
                else:
                    # el numero de matricula no coincide , vovler a intentarlo
                    raise ValueError ("el numero de matricula no coincide con el valor ingresado")
            except Exception as e:
                print(f"Error en la matricula:{self.m}")
                time.sleep(1)

        # === PRESIONAR CLICK
        #box_matricula.send_keys(Keys.ENTER)
        buscar_inm = self.driver.find_element(by="xpath",value="//button[@ng-click='buscarInmueble()']")
        buscar_inm.click()
        time.sleep(3)
        intentos_alerta = 0
        while True:
            try:
                # Esperar hasta que aparezca una alerta
                alerta = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                print("marca0000")
                if alerta:
                    alerta.accept()
                    intentos_alerta +=1
                    time.sleep(2)
                    buscar_inm = self.driver.find_element(by="xpath", value="//button[@ng-click='buscarInmueble()']")
                    buscar_inm.click()

                    if intentos_alerta >=2:
                        print("dato no encontrado")
                        raise Scraperexeption("Dato no encontrado") # RAISE Propagar la excepción hacia arriba en la pila de llamadas
            except TimeoutException:
                print("sigue con el codigo")
                break
        # === REGRESAR AL SCOPE PRINCIPAL ===
        self.driver.switch_to.default_content()
        time.sleep(5)
        # === METODO TECLADO ===
        # movimiento = ActionChains(driver)
        # for i in range(9):
        # movimiento.send_keys(Keys.TAB)
        # Pulsar la tecla Enter
        # movimiento.send_keys(Keys.ENTER)
    @timeout(120)
    def click_consultar (self):
        if self.detener:
            #sys.exit()  # Salir del programa inmediatamente
            return

        print("click_consultar")
        time.sleep(5)
        # === UBIRCAR EL IFRAME PARA BUSCAR LOS ELEMENTOS DESEADOS ===
        iframe = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//iframe[@id="page"]')))

        # === CAMBIAR EL SCOPE DEL DRIVER AL iframe ===
        self.driver.switch_to.frame(iframe)

        # === UBICAR BOTON CONSULTA Y HACER CLICK
        botton_consultar = WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH, "//a[@ng-click='consultarMatricula(registro)']")))
        botton_consultar.click()
        time.sleep(5)
        intentos_alerta1= 0
        while True:
            try:
                # Esperar hasta que aparezca una alerta
                alerta = WebDriverWait(self.driver, 5).until(EC.alert_is_present())

                # Verificar si la alerta está presente antes de aceptarla
                if alerta:
                    time.sleep(2)
                    alerta.accept()
                    time.sleep(3)
                    botton_consultar = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@ng-click='consultarMatricula(registro)']")))
                    botton_consultar.click()
                    time.sleep(5)
                    if intentos_alerta1 >=3:
                        print("error repetitivo al dar click en consultar")
                        raise Exception # RAISE Propagar la excepción hacia arriba en la pila de llamadas

            except TimeoutException:
                break


        self.driver.switch_to.default_content()
        time.sleep(10)
    @timeout(100)
    def extract_data (self):
        if self.detener:
            #sys.exit()  # Salir del programa inmediatamente
            return

        print("extract_data")
        time.sleep(2)
        # === UBIRCAR EL IFRAME PARA BUSCAR LOS ELEMENTOS DESEADOS ===
        iframe = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//iframe[@id="page"]')))

        # === CAMBIAR EL SCOPE DEL DRIVER AL iframe ===
        self.driver.switch_to.frame(iframe)

        # ===UBICAR ETIQUETA LISTA QUE DESPLIEGA LAS ANOTACIONES===
        lista_label = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Lista')]")))
        lista_label.click()
        time.sleep(2)

        # ===EXTRAER DATOS ===
        container = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//div[@title='Lista']")))
        # === ARRAY QUE CONTIENE TODAS LAS ANOTACIONES EN CRUDO ===
        anotaciones = WebDriverWait(container,10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='row anotacion ng-scope']")))

        # LOOP QUE RECORRE CADA ANOTACION
        for anotacion in anotaciones:
            # === ANOTACION INDIVIDUAL RAW
            anotacion_text = anotacion.find_element(by="xpath", value='.//span').text

            # === USO DE LAS EXPRESIONES REGULARES PARA EXTRAER LOS DATOS POR MEDIO DE PATRONES ===
            patron1 = r"Nro (\d+)"  # Nro 1
            patron2 = r"ESCRITURA (\d+)"  # numero de la escritura 1240
            patron3 = r"(\d{4}-\d{2}-\d{2})"  # extrae la fecha 2012-09-06
            patron4 = r"VALOR ACTO: \$([0-9,.]*)"  # extraer el PRECIO
            patron5 = r"ESPECIFICACION: \d+ ((?:\w+\s+){3})"  # extrae la pimera 3 palabras despues del numero de especificacion
            patron6 = "DE:(.*?)(?=\s*(?:DE:|A:|$))"  # extrae los DE:
            patron7 = "A:(.*?)(?=\s*(?:A:|$))"  # extraer los A:

            resultado1 = re.search(patron1, anotacion_text, re.DOTALL)
            resultado2 = re.search(patron2, anotacion_text, re.DOTALL)
            resultado3 = re.search(patron3, anotacion_text, re.DOTALL)
            resultado4 = re.search(patron4, anotacion_text, re.DOTALL)
            resultado5 = re.findall(patron5, anotacion_text, re.DOTALL)
            resultado6 = re.findall(patron6, anotacion_text, re.DOTALL)
            resultado7 = re.findall(patron7, anotacion_text, re.DOTALL)

            # === VARIABLES DONDE SE GUARDAN LOS PATRONES ENCONTRADOS ===
            anotacion = resultado1.group().strip() if resultado1 else "0"
            doc = resultado2.group(1).strip() if resultado2 else "0"
            fecha = resultado3.group().strip() if resultado3 else "0"
            precio = resultado4.group(1).strip() if resultado4 else "0"
            especificacion = resultado5[0].strip() if resultado5 else "0"
            DE = ','.join(resultado6).strip() if resultado6 else "0"
            A = ','.join(resultado7).strip() if resultado7 else "0"

            # === INGRESAR LOS DATOS AL ARRRAY ===
            self.datos[0] = self.m
            self.datos[1] = anotacion
            self.datos[2] = doc
            self.datos[3] = fecha
            self.datos[4] = precio
            self.datos[5] = especificacion
            self.datos[6] = DE
            self.datos[7] = A

            # GUARDA LOS DATOS DEL ARRAY datos EN LA SIGUIENTE COLUMNA DEL DATA FRAME
            self.df.loc[len(self.df)] = self.datos

        escritorio = Path.home() / "Desktop"

        # Guardar archivo CSV en el escritorio
        ruta_csv = escritorio / "Anotaciones.csv"
        self.df.to_csv(ruta_csv, index=True)

        # Guardar archivo Excel en el escritorio
        ruta_excel = escritorio / "datos.xlsx"
        self.df.to_excel(ruta_excel, sheet_name="data_raw", index=False)

        #self.df.to_csv('Anotaciones.csv', index=True)
        #self.df.to_excel("datos.xlsx", sheet_name="data_raw", index=False)

        # === REGRESAR SET_BUSQUEDA ===
        time.sleep(3)
        boton_buscar_inmueble = self.driver.find_element(by="xpath",value='//button[@ng-click="reiniciar()"]')
        boton_buscar_inmueble.click()
        self.driver.switch_to.default_content()
        time.sleep(3)
    def filter(self):
        if self.detener:
            return
        print("filtrando")
        escritorio = Path.home() / "Desktop"  # Ruta al escritorio del usuario
        ruta_archivo_excel = escritorio / "datos.xlsx"
        self.dff = pd.read_excel(ruta_archivo_excel)
        # self.dff = pd.read_excel(r'D:\pythonProject\VUR\datos.xlsx')

        self.df_filtrado = self.dff[self.dff['ESPECIFICACION'].str.contains('transferencia|compraventa', case=False)]
        ruta_archivo_salida = escritorio / "datos.xlsx"
        writer = pd.ExcelWriter(ruta_archivo_salida, mode='a', engine='openpyxl', if_sheet_exists='replace')
        self.df_filtrado.to_excel(writer, sheet_name='filtro', index=False)

        writer.close()

        # Después de crear el archivo filtrado, actualiza la ruta_archivo_salida
        self.ruta_archivo_salida = str(ruta_archivo_salida)





#hunter = VurScraper()
#hunter.main()

#if __name__ == "__main__":
    #gui = Menu()
    #gui.ventana.mainloop()

