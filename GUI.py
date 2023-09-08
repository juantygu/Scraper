import time
import tkinter as tk
import main_2
from tkinter import ttk, filedialog
from main_2 import VurScraper
import threading
import os
import shutil
from PIL import Image, ImageTk
import requests
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteCombobox


class Menu():
    def __init__(self):
        self.inicio = tk.Tk()
        self.inicio.title("Inicio de Sesión")
        self.inicio.geometry("300x150")

        # Centrar la ventana en la pantalla
        self.inicio_width = self.inicio.winfo_screenwidth()  # ancho de la ventana requerido gracias a la funcion .winfo_reqwidth()
        self.inicio_height = self.inicio.winfo_screenheight()  # alto de la ventana requerido gracias a la funcion .winfo_reqheight()
        self.winicio = 300
        self.hinicio = 150
        self.inicio_position_right = int(self.inicio_width / 2 - self.winicio / 2)  # posicion de la ventana la funcion winfo_screenwidth() determina el ancho de la pantalla
        self.inicio_position_down = int(self.inicio_height / 2 - self.hinicio / 2)  # posicion de la ventana la funcion winfo_screenheight() determina el alto de la pantalla
        self.inicio.geometry("+{}+{}".format(self.inicio_position_right,self.inicio_position_down))  # los valores position_right, position_down van en los corchet

        # Agrega widgets para el usuario y la contraseña
        self.label_user = tk.Label(self.inicio, text="Usuario:")
        self.label_user.pack()
        self.entry_user = tk.Entry(self.inicio)
        self.entry_user.pack()


        self.label_password = tk.Label(self.inicio, text="Contraseña:")
        self.label_password.pack()
        self.entry_password = tk.Entry(self.inicio, show="*")  # Muestra asteriscos para la contraseña
        self.entry_password.pack()


        # Crea un botón para iniciar sesión
        self.login_button = tk.Button(self.inicio, text="Iniciar Sesión", command=self.verificar_credenciales)
        self.login_button.pack()
    def verificar_credenciales(self):
        # Obtiene el usuario y la contraseña ingresados por el usuario
        self.usuario = self.entry_user.get()
        self.contrasena = self.entry_password.get()

        # Verifica las credenciales (puedes personalizar esto)
        if self.usuario == "GPINEDAC" and self.contrasena == "Martes16*":
            # Si las credenciales son correctas, cierra la ventana de inicio de sesión y muestra la ventana principal
            self.inicio.destroy()
            self.mostrar_ventana_principal()
        else:
            # Si las credenciales son incorrectas, muestra un mensaje de error
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    def mostrar_ventana_principal(self):
        # ==========================================VENTANA===========================================================
        self.ventana = tk.Tk()
        self.ventana.title("VUR SCRAPER")
        self.ventana.geometry('1080x600')
        self.ventana.minsize(600, 400)
        self.ventana.resizable(width=False, height=False)

        # Centrar la ventana en la pantalla
        self.window_width = self.ventana.winfo_screenwidth()  # ancho de la ventana requerido gracias a la funcion .winfo_reqwidth()
        self.window_height = self.ventana.winfo_screenheight()  # alto de la ventana requerido gracias a la funcion .winfo_reqheight()
        self.wventana = 1080
        self.hventana = 600
        self.position_right = int(self.window_width / 2 - self.wventana / 2)  # posicion de la ventana la funcion winfo_screenwidth() determina el ancho de la pantalla
        self.position_down = int(self.window_height / 2 - self.hventana / 2)  # posicion de la ventana la funcion winfo_screenheight() determina el alto de la pantalla
        self.ventana.geometry("+{}+{}".format(self.position_right,self.position_down))  # los valores position_right, position_down van en los corchetes gracias a la funcion .format

        self.create_widgets()
        # ==========================================VARIABLE BOOLEANAS=================================================
        self.hilo_scraper = None
        self.programa_parado = False
        self.programa_finalizado = False
        self.terminado = False
        self.matricula_no_encotrada = False
        # ==========================================EVENTOS============================================================
        self.ventana.protocol("WM_DELETE_WINDOW", self.on_cerrar_ventana)
        self.ventana.bind("<<IndividualTerminado>>", self.on_Individual_terminado)
        self.ventana.bind("<<ExcelTerminado>>", self.on_Excel_terminado)  # evento finalizado
        self.ventana.bind("<<ScraperParado>>", self.on_Excel_stop)  # evento parado
        self.lista_desplegable.bind("<<ComboboxSelected>>", self.guardar_municipio_seleccionado_excel)
        self.lista_desplegable.bind("<<ComboboxSelected>>", self.guardar_municipio_seleccionado_grupal)


        self.ventana.mainloop()# asigno el nuevo mainloo() que sera el hilo principal de la interfaz
    def create_widgets(self):
        # ========================================= ETIQUETAS =====================================================
        self.etiqueta_blanca = ttk.Label(background='#ADD8E6')
        self.etiqueta_blanca.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.etiqueta_azul = ttk.Label(background='midnight blue')
        self.etiqueta_azul.place(relx=0, rely=0, relwidth=0.3, relheight=1)

        self.etiqueta_1 = tk.Label( text=" VUR SCRAPER",font=("Arial",18,"bold"),bg="midnight blue", fg="white",width=20, borderwidth=0)
        self.etiqueta_1.place(x=20, y=30)

        self.etiqueta_2 = tk.Label( text=" Seleccione un opción ",font=("Arial",18,"bold"),bg="midnight blue",fg="white",width=20,wraplength=300, borderwidth=0)
        self.etiqueta_2.place(x=20,y=150)

        self.etiqueta_mensaje= tk.Label()

        self.etiqueta_cargar = tk.Label(text="", font=("Arial", 12), bg='#ADD8E6')

        self.etiqueta_matricula = tk.Label()

        self.barra_progreso = ttk.Progressbar()

        self.etiqueta_alerta = tk.Label()

        self.etiqueta_circulo = tk.Label()

        self.etiqueta_matriculas_saved = tk.Label()
        self.etiqueta_verificar_matriculas_saved = tk.Label()


# =================================FRAMES INFORMACION VENTANA PRINCIAPAL====================================================================
        self.frame_1 = tk.Frame(self.ventana, bg="midnight blue")
        self.frame_1.place(relx=0.4, rely=0, relwidth=0.5, relheight=0.3)
        self.etiqueta1_frame_1 = tk.Label(self.ventana,text="Buscador de matriculas inmobiliarias", font=("Arial", 18,"bold"), bg='midnight blue',fg="white")
        self.etiqueta1_frame_1.place(x=490, y=10)
        self.etiqueta2_frame_1 = tk.Label(self.ventana, text="Este scraper se enfoca unicamente en la pagina www.vur.gov.co",font=("Arial", 13,"bold"), bg='midnight blue', fg="white")
        self.etiqueta2_frame_1.place(x=450, y=80)
# ===================================TEST INTERNET CONECCTION =============================================================================
        self.etiqueta1_frame_2 = tk.Label(text="Verifique su conexión a internet", font=("Arial", 14,"bold"), bg='midnight blue',fg="white")
        self.etiqueta1_frame_2.place(x=17,y=450)
        self.boton_test = tk.Button(text="Test",font=("Arial",16,"bold"),bg="#ADD8E6", fg="black",width=10,command=self.test_connection)
        self.boton_test.place(x=90,y=500)
        self.etiqueta3_frame_2 = tk.Label(text="", font=("Arial", 14, "bold"), bg="midnight blue")

        # ========================================= BOTONES =====================================================
        self.botton_mi = tk.Button( text=" Individual",font=("Arial",16,"bold"),bg="#ADD8E6", fg="black",width=10, command=self.on_botton_mi_click)
        self.botton_mi.place(x=90, y=225)

        self.botton_mg = tk.Button( text="Grupal",font=("Arial",16,"bold"),bg="#ADD8E6", fg="black",width=10, command=self.on_botton_mg_click)
        self.botton_mg.place(x=90, y=295)

        self.botton_excel = tk.Button( text="Archivo excel", font=("Arial", 16,"bold"), bg="#ADD8E6", fg="black", width=10, command=self.on_botton_excel_click)
        self.botton_excel.place(x=90, y=370)

        self.boton_descargar = None
        self.boton_cargar = None
        self.boton_comenzar = None

        self.boton_pausa = None
        self.boton_reanudar = None
        self.boton_parar = None
        self.boton_atras = None
        self.boton_reset = None

        #================================================BOX MATRICULA INDIVIDUAL======================================================
        self.box_matricula = tk.Entry(self.ventana)
        self.matricula_caja = None
        #========================================ventana stop emergente ===========================================
        self.wait_window = None
        #======================================ARRAY MATRICULAS PARA GRUPAL ======================================
        self.num_matriculas = tk.StringVar(self.ventana)
        self.num_matriculas.set("1")  # Valor predeterminado
        self.entry_boxes = []  # Lista para mantener las cajas de texto
        self.labels = []
        self.dropdown_num_matriculas = ttk.Combobox()
        self.matricula_array = []
        self.boton_guardar = tk.Button()
        self.entry_box = tk.Entry()
        self.label = tk.Label()
        #============================================LISTA DESPEGABLE MUNICIPIOS Y CUIDADES ======================================
        self.circulos_registrales_ORIP = ["ORIP - APARTADO - ( 008 )", "ORIP - ABEJORRAL - ( 002 )", "ORIP - ACACIAS - ( 232 )",
                      "ORIP - AGUA DE DIOS - ( 150 )", "ORIP - AGUACHICA - ( 196 )", "ORIP - AGUADAS - ( 102 )",
                      "ORIP - AMALFI - ( 003 )", "ORIP - AMBALEMA - ( 351 )", "ORIP - ANDES - ( 004 )",
                      "ORIP - ANSERMA - ( 103 )", "ORIP - APIA - ( 292 )", "ORIP - ARAUCA - ( 410 )",
                      "ORIP - ARMENIA - ( 280 )", "ORIP - ARMERO - ( 352 )", "ORIP - AYAPEL - ( 141 )",
                      "ORIP - BARBACOAS - ( 242 )", "ORIP - BARICHARA - ( 302 )", "ORIP - BARRANCABERMEJA - ( 303 )",
                      "ORIP - BARRANQUILLA - ( 040 )", "ORIP - BELEN DE UMBRIA - ( 293 )",
                      "ORIP - BOGOTA CENTRO - ( 50C )","ORIP - BOGOTA NORTE - ( 50N )", "ORIP - BOGOTA SUR - ( 50S )",
                      "ORIP - BOLIVAR ANTIOQUIA - ( 005 )", "ORIP - BOLIVAR CAUCA - ( 122 )",
                      "ORIP - BUCARAMANGA - ( 300 )", "ORIP - BUENAVENTURA - ( 372 )", "ORIP - BUGA - ( 373 )",
                      "ORIP - CACHIRA - ( 261 )", "ORIP - CAJAMARCA - ( 354 )", "ORIP - CALARCA - ( 282 )",
                      "ORIP - CALI - ( 370 )", "ORIP - CALOTO - ( 124 )", "ORIP - CAQUEZA - ( 152 )",
                      "ORIP - CARTAGENA - ( 060 )", "ORIP - CARTAGO - ( 375 )", "ORIP - CAUCASIA - ( 015 )",
                      "ORIP - CAÑASGORDAS - ( 006 )", "ORIP - CERETE - ( 143 )", "ORIP - CHAPARRAL - ( 355 )",
                      "ORIP - CHARALA - ( 306 )", "ORIP - CHIMICHAGUA - ( 192 )", "ORIP - CHINACOTA - ( 264 )",
                      "ORIP - CHINU - ( 144 )", "ORIP - CHIQUINQUIRA - ( 072 )", "ORIP - CHOCONTA - ( 154 )",
                      "ORIP - CIENAGA - ( 222 )", "ORIP - CONCEPCION - ( 308 )", "ORIP - CONTRATACION - ( 161 )",
                      "ORIP - CONVENCION - ( 266 )", "ORIP - COROZAL - ( 342 )", "ORIP - CUCUTA - ( 260 )",
                      "ORIP - DABEIBA - ( 007 )", "ORIP - DOSQUEBRADAS - ( 294 )", "ORIP - DUITAMA - ( 074 )",
                      "ORIP - EL BANCO - ( 224 )", "ORIP - EL CARMEN DE BOLIVAR - ( 062 )", "ORIP - EL COCUY - ( 076 )",
                      "ORIP - ESPINAL - ( 357 )", "ORIP - FACATATIVA - ( 156 )", "ORIP - FILANDIA - ( 284 )",
                      "ORIP - FLORENCIA - ( 420 )", "ORIP - FREDONIA - ( 010 )", "ORIP - FRESNO - ( 359 )",
                      "ORIP - FRONTINO - ( 011 )","ORIP - FUNDACION - ( 225 )", "ORIP - FUSAGASUGA - ( 157 )", "ORIP - GACHETA - ( 160 )",
                      "ORIP - GARAGOA - ( 078 )", "ORIP - GARZON - ( 202 )", "ORIP - GIRARDOT - ( 307 )",
                      "ORIP - GIRARDOTA - ( 012 )", "ORIP - GUADUAS - ( 162 )", "ORIP - GUAMO - ( 360 )",
                      "ORIP - GUAPI - ( 126 )", "ORIP - GUATEQUE - ( 079 )", "ORIP - HONDA - ( 362 )",
                      "ORIP - IBAGUE - ( 350 )", "ORIP - INIRIDA - ( 500 )", "ORIP - IPIALES - ( 244 )",
                      "ORIP - ISTMINA - ( 184 )", "ORIP - ITUANGO - ( 013 )", "ORIP - JERICO - ( 014 )",
                      "ORIP - LA CEJA - ( 017 )", "ORIP - LA CRUZ - ( 246 )", "ORIP - LA DORADA - ( 106 )",
                      "ORIP - LA MESA - ( 166 )", "ORIP - LA PALMA - ( 167 )","ORIP - LA PLATA - ( 204 )",
                      "ORIP - LA UNION - ( 248 )", "ORIP - LETICIA - ( 400 )",
                      "ORIP - LIBANO - ( 364 )", "ORIP - LORICA - ( 146 )", "ORIP - MAGANGUE - ( 064 )",
                      "ORIP - MAICAO - ( 212 )", "ORIP - MALAGA - ( 312 )", "ORIP - MANIZALES - ( 100 )",
                      "ORIP - MANZANARES - ( 108 )", "ORIP - MARINILLA - ( 018 )", "ORIP - MEDELLIN NORTE - ( 01N )",
                      "ORIP - MEDELLIN SUR - ( 001 )", "ORIP - MELGAR - ( 366 )", "ORIP - MIRAFLORES - ( 082 )",
                      "ORIP - MITU - ( 520 )", "ORIP - MOCOA - ( 440 )", "ORIP - MOMPOS - ( 065 )",
                      "ORIP - MONIQUIRA - ( 083 )", "ORIP - MONTELIBANO - ( 142 )", "ORIP - MONTERIA - ( 140 )",
                      "ORIP - NEIRA - ( 110 )", "ORIP - NEIVA - ( 200 )",
                      "ORIP - NUQUI - ( 186 )", "ORIP - OCAÑA - ( 270 )", "ORIP - OROCUE - ( 086 )",
                      "ORIP - PACHO - ( 170 )", "ORIP - PACORA - ( 112 )", "ORIP - PALMIRA - ( 378 )",
                      "ORIP - PAMPLONA - ( 272 )", "ORIP - PASTO - ( 240 )", "ORIP - PATIA EL BORDO - ( 128 )",
                      "ORIP - PAZ DE ARIPORO - ( 475 )", "ORIP - PENSILVANIA - ( 114 )", "ORIP - PEREIRA - ( 290 )",
                      "ORIP - PIEDECUESTA - ( 314 )", "ORIP - PITALITO - ( 206 )", "ORIP - PLATO - ( 226 )",
                      "ORIP - POPAYAN - ( 120 )", "ORIP - PUENTE NACIONAL - ( 315 )", "ORIP - PUERTO ASIS - ( 442 )",
                      "ORIP - PUERTO BERRIO - ( 019 )", "ORIP - PUERTO BOYACA - ( 088 )",
                      "ORIP - PUERTO CARREÑO - ( 540 )", "ORIP - PUERTO LOPEZ - ( 234 )",
                      "ORIP - PUERTO TEJADA - ( 130 )", "ORIP - PURIFICACION - ( 368 )", "ORIP - QUIBDO - ( 180 )",
                      "ORIP - RAMIRIQUI - ( 090 )", "ORIP - RIOHACHA - ( 210 )", "ORIP - RIONEGRO - ( 020 )",
                      "ORIP - RIOSUCIO - ( 115 )", "ORIP - ROLDANILLO - ( 380 )", "ORIP - SABANALARGA - ( 045 )",
                      "ORIP - SAHAGUN - ( 148 )", "ORIP - SALAMINA - ( 118 )", "ORIP - SALAZAR - ( 276 )",
                      "ORIP - SAMANIEGO - ( 250 )", "ORIP - SAN ANDRES ISLA - ( 450 )",
                      "ORIP - SAN ANDRES SANTANDER - ( 318 )", "ORIP - SAN GIL - ( 319 )",
                      "ORIP - SAN JOSE DEL GUAVIARE - ( 480 )", "ORIP - SAN JUAN DEL CESAR - ( 214 )",
                      "ORIP - SAN MARCOS - ( 346 )", "ORIP - SAN MARTIN - ( 236 )",
                      "ORIP - SAN VICENTE DE CHUCURI - ( 320 )", "ORIP - SAN VICENTE DEL CAGUAN - ( 425 )",
                      "ORIP - SANTA BARBARA - ( 023 )", "ORIP - SANTA FE DE ANTIOQUIA - ( 024 )",
                      "ORIP - SANTA MARTA - ( 080 )", "ORIP - SANTA ROSA DE CABAL - ( 296 )",
                      "ORIP - SANTA ROSA DE OSOS - ( 025 )", "ORIP - SANTA ROSA DE VITERBO - ( 092 )",
                      "ORIP - SANTANDER DE QUILICHAO - ( 132 )", "ORIP - SANTO DOMINGO - ( 026 )",
                      "ORIP - SANTUARIO - ( 297 )", "ORIP - SEGOVIA - ( 027 )", "ORIP - SEVILLA - ( 382 )",
                      "ORIP - SIBUNDOY - ( 441 )", "ORIP - SILVIA - ( 134 )", "ORIP - SIMITI - ( 068 )",
                      "ORIP - SINCE - ( 347 )", "ORIP - SINCELEJO - ( 340 )", "ORIP - SITIO NUEVO - ( 228 )",
                      "ORIP - SOACHA - ( 051 )", "ORIP - SOATA - ( 093 )", "ORIP - SOCHA - ( 094 )",
                      "ORIP - SOCORRO - ( 321 )", "ORIP - SOGAMOSO - ( 095 )", "ORIP - SOLEDAD - ( 041 )",
                      "ORIP - SONSON - ( 028 )", "ORIP - SOPETRAN - ( 029 )", "ORIP - TAMESIS - ( 032 )",
                      "ORIP - TITIRIBI - ( 033 )", "ORIP - TULUA - ( 384 )", "ORIP - TUMACO - ( 252 )",
                      "ORIP - TUNJA - ( 070 )", "ORIP - TUQUERRES - ( 254 )", "ORIP - TURBO - ( 034 )",
                      "ORIP - UBATE - ( 172 )", "ORIP - URRAO - ( 035 )", "ORIP - VALLEDUPAR - ( 190 )",
                      "ORIP - VELEZ - ( 324 )", "ORIP - VILLAVICENCIO - ( 230 )", "ORIP - YARUMAL - ( 037 )",
                      "ORIP - YOLOMBO - ( 038 )", "ORIP - YOPAL - ( 470 )", "ORIP - ZAPATOCA - ( 326 )","ORIP - ZIPAQUIRA - ( 176 )"]
        self.circulos_registrales = ['APARTADO - ( 008 )', 'ABEJORRAL - ( 002 )', 'ACACIAS - ( 232 )', 'AGUA DE DIOS - ( 150 )', 'AGUACHICA - ( 196 )',
            'AGUADAS - ( 102 )', 'AMALFI - ( 003 )', 'AMBALEMA - ( 351 )', 'ANDES - ( 004 )', 'ANSERMA - ( 103 )', 'APIA - ( 292 )',
            'ARAUCA - ( 410 )', 'ARMENIA - ( 280 )', 'ARMERO - ( 352 )', 'AYAPEL - ( 141 )', 'BARBACOAS - ( 242 )', 'BARICHARA - ( 302 )',
            'BARRANCABERMEJA - ( 303 )', 'BARRANQUILLA - ( 040 )', 'BELEN DE UMBRIA - ( 293 )', 'BOGOTA CENTRO - ( 50C )',
            'BOGOTA NORTE - ( 50N )', 'BOGOTA SUR - ( 50S )', 'BOLIVAR ANTIOQUIA - ( 005 )', 'BOLIVAR CAUCA - ( 122 )',
            'BUCARAMANGA - ( 300 )', 'BUENAVENTURA - ( 372 )', 'BUGA - ( 373 )', 'CACHIRA - ( 261 )', 'CAJAMARCA - ( 354 )',
            'CALARCA - ( 282 )', 'CALI - ( 370 )', 'CALOTO - ( 124 )', 'CAQUEZA - ( 152 )', 'CARTAGENA - ( 060 )', 'CARTAGO - ( 375 )',
            'CAUCASIA - ( 015 )', 'CAÑASGORDAS - ( 006 )', 'CERETE - ( 143 )', 'CHAPARRAL - ( 355 )', 'CHARALA - ( 306 )',
            'CHIMICHAGUA - ( 192 )', 'CHINACOTA - ( 264 )', 'CHINU - ( 144 )', 'CHIQUINQUIRA - ( 072 )', 'CHOCONTA - ( 154 )',
            'CIENAGA - ( 222 )', 'CONCEPCION - ( 308 )', 'CONTRATACION - ( 161 )', 'CONVENCION - ( 266 )', 'COROZAL - ( 342 )',
            'CUCUTA - ( 260 )', 'DABEIBA - ( 007 )', 'DOSQUEBRADAS - ( 294 )', 'DUITAMA - ( 074 )', 'EL BANCO - ( 224 )',
            'EL CARMEN DE BOLIVAR - ( 062 )', 'EL COCUY - ( 076 )', 'ESPINAL - ( 357 )', 'FACATATIVA - ( 156 )', 'FILANDIA - ( 284 )',
            'FLORENCIA - ( 420 )', 'FREDONIA - ( 010 )', 'FRESNO - ( 359 )', 'FRONTINO - ( 011 )', 'FUNDACION - ( 225 )',
            'FUSAGASUGA - ( 157 )', 'GACHETA - ( 160 )', 'GARAGOA - ( 078 )', 'GARZON - ( 202 )', 'GIRARDOT - ( 307 )',
            'GIRARDOTA - ( 012 )', 'GUADUAS - ( 162 )', 'GUAMO - ( 360 )', 'GUAPI - ( 126 )', 'GUATEQUE - ( 079 )',
            'HONDA - ( 362 )', 'IBAGUE - ( 350 )', 'INIRIDA - ( 500 )', 'IPIALES - ( 244 )', 'ISTMINA - ( 184 )',
            'ITUANGO - ( 013 )', 'JERICO - ( 014 )', 'LA CEJA - ( 017 )', 'LA CRUZ - ( 246 )', 'LA DORADA - ( 106 )',
            'LA MESA - ( 166 )', 'LA PALMA - ( 167 )', 'LA PLATA - ( 204 )', 'LA UNION - ( 248 )', 'LETICIA - ( 400 )',
            'LIBANO - ( 364 )', 'LORICA - ( 146 )', 'MAGANGUE - ( 064 )', 'MAICAO - ( 212 )', 'MALAGA - ( 312 )', 'MANIZALES - ( 100 )',
            'MANZANARES - ( 108 )', 'MARINILLA - ( 018 )', 'MEDELLIN NORTE - ( 01N )', 'MEDELLIN SUR - ( 001 )', 'MELGAR - ( 366 )',
            'MIRAFLORES - ( 082 )', 'MITU - ( 520 )', 'MOCOA - ( 440 )', 'MOMPOS - ( 065 )', 'MONIQUIRA - ( 083 )', 'MONTELIBANO - ( 142 )',
            'MONTERIA - ( 140 )', 'NEIRA - ( 110 )', 'NEIVA - ( 200 )', 'NUQUI - ( 186 )', 'OCAÑA - ( 270 )', 'OROCUE - ( 086 )',
            'PACHO - ( 170 )', 'PACORA - ( 112 )', 'PALMIRA - ( 378 )', 'PAMPLONA - ( 272 )', 'PASTO - ( 240 )', 'PATIA EL BORDO - ( 128 )',
            'PAZ DE ARIPORO - ( 475 )', 'PENSILVANIA - ( 114 )', 'PEREIRA - ( 290 )', 'PIEDECUESTA - ( 314 )', 'PITALITO - ( 206 )',
            'PLATO - ( 226 )', 'POPAYAN - ( 120 )', 'PUENTE NACIONAL - ( 315 )', 'PUERTO ASIS - ( 442 )', 'PUERTO BERRIO - ( 019 )',
            'PUERTO BOYACA - ( 088 )', 'PUERTO CARREÑO - ( 540 )', 'PUERTO LOPEZ - ( 234 )', 'PUERTO TEJADA - ( 130 )', 'PURIFICACION - ( 368 )',
            'QUIBDO - ( 180 )', 'RAMIRIQUI - ( 090 )', 'RIOHACHA - ( 210 )', 'RIONEGRO - ( 020 )', 'RIOSUCIO - ( 115 )', 'ROLDANILLO - ( 380 )',
            'SABANALARGA - ( 045 )', 'SAHAGUN - ( 148 )', 'SALAMINA - ( 118 )', 'SALAZAR - ( 276 )', 'SAMANIEGO - ( 250 )',
            'SAN ANDRES ISLA - ( 450 )', 'SAN ANDRES SANTANDER - ( 318 )', 'SAN GIL - ( 319 )', 'SAN JOSE DEL GUAVIARE - ( 480 )',
            'SAN JUAN DEL CESAR - ( 214 )', 'SAN MARCOS - ( 346 )', 'SAN MARTIN - ( 236 )', 'SAN VICENTE DE CHUCURI - ( 320 )',
            'SAN VICENTE DEL CAGUAN - ( 425 )', 'SANTA BARBARA - ( 023 )', 'SANTA FE DE ANTIOQUIA - ( 024 )', 'SANTA MARTA - ( 080 )',
            'SANTA ROSA DE CABAL - ( 296 )', 'SANTA ROSA DE OSOS - ( 025 )', 'SANTA ROSA DE VITERBO - ( 092 )', 'SANTANDER DE QUILICHAO - ( 132 )',
            'SANTO DOMINGO - ( 026 )', 'SANTUARIO - ( 297 )', 'SEGOVIA - ( 027 )', 'SEVILLA - ( 382 )', 'SIBUNDOY - ( 441 )', 'SILVIA - ( 134 )',
            'SIMITI - ( 068 )', 'SINCE - ( 347 )', 'SINCELEJO - ( 340 )', 'SITIO NUEVO - ( 228 )', 'SOACHA - ( 051 )',
            'SOATA - ( 093 )', 'SOCHA - ( 094 )', 'SOCORRO - ( 321 )', 'SOGAMOSO - ( 095 )', 'SOLEDAD - ( 041 )', 'SONSON - ( 028 )',
            'SOPETRAN - ( 029 )', 'TAMESIS - ( 032 )', 'TITIRIBI - ( 033 )', 'TULUA - ( 384 )', 'TUMACO - ( 252 )', 'TUNJA - ( 070 )',
            'TUQUERRES - ( 254 )', 'TURBO - ( 034 )', 'UBATE - ( 172 )', 'URRAO - ( 035 )', 'VALLEDUPAR - ( 190 )', 'VELEZ - ( 324 )',
            'VILLAVICENCIO - ( 230 )', 'YARUMAL - ( 037 )', 'YOLOMBO - ( 038 )', 'YOPAL - ( 470 )', 'ZAPATOCA - ( 326 )', 'ZIPAQUIRA - ( 176 )']
        self.municipio_seleccionado = tk.StringVar(self.ventana)
        #self.circulo_registral_var.set(self.circulos_registrales[0])
        #self.lista_desplegable = ttk.Combobox()
        self.lista_desplegable = AutocompleteCombobox()
    def test_connection(self):
        self.etiqueta3_frame_2.destroy()
        self.etiqueta3_frame_2 = tk.Label( text="", font=("Arial", 14, "bold"), bg="midnight blue")
        self.etiqueta3_frame_2.place(x=50, y=560)
        try:
            self.response = requests.get("https://www.vur.gov.co/",timeout=10)
            if self.response.status_code == 200:
                self.etiqueta3_frame_2.config(text="Conexion a VUR exitosa",fg="green")
                print("Conexión a Internet exitosa")

            else:
                self.etiqueta3_frame_2.config(text=" no hay Conexion a VUR ", fg="red")
                self.etiqueta3_frame_2.place(x=40, y=560)
                print("Error: No se pudo conectar a la URL")
        except requests.ConnectionError:
            self.etiqueta3_frame_2.config(text="No hay conección a internet", fg="red")
            self.etiqueta3_frame_2.place(x=35, y=560)
            print("No se pudo conectar a Internet")


        # Programa la destrucción de la etiqueta después de 10 segundos
        self.ventana.after(3000,lambda: self.etiqueta3_frame_2.config(text=""))
# ========================================ON=======================================================================
    def on_botton_mi_click(self): # CLICK EN BOTON_MI
        self.show_state("Individual")
    def on_botton_mg_click(self): # CLICK EN BOTON_MG
        self.show_state("Grupal")
    def on_botton_excel_click(self): # CLICK EN BOTON_EXCEL
        self.show_state("Excel")
    def on_cerrar_ventana(self): # CERRAR VENTANA
        if self.hilo_scraper and self.hilo_scraper.is_alive(): # Si se esta ejecutando el hilo , detener el proceso cuand se cierre la ventana
            self.hunter.detener_proceso()
        self.ventana.destroy()
    def on_Individual_terminado(self,event):
        self.show_state("individual_finalizado")
    def on_Excel_terminado(self, event): # cuando el scraper ha terminado
        self.show_state("excel_finalizado")
    def on_Excel_stop(self,event): # cuando el scraper se ha detenido por el usuario
        self.show_state("excel_parado")

#=========================================CLEAN AND DISABLE ELEMENTS============================================================
    def clear_upload_widgets(self): # asegura que no haya ningun elemento cargado previamente para evitar la superposicion de elementos
        if self.etiqueta_cargar:
            self.etiqueta_cargar.destroy()
        if self.boton_cargar:
            self.boton_cargar.destroy()
        if self.box_matricula:
            self.box_matricula.destroy()
        if self.boton_comenzar:
            self.boton_comenzar.destroy()
        if self.dropdown_num_matriculas:
            self.dropdown_num_matriculas.destroy()
        if self.boton_guardar:
            self.boton_guardar.destroy()
        if self.label:
            for self.label in self.labels:
                self.label.destroy()
        if self.entry_box:
            for self.entry_box in self.entry_boxes:
                self.entry_box.destroy()
        if self.etiqueta_verificar_matriculas_saved:
            self.etiqueta_verificar_matriculas_saved.destroy()
        if self.boton_atras:
            self.boton_atras.destroy()
        if self.boton_reset:
            self.boton_reset.destroy()
        if self.etiqueta_mensaje:
            self.etiqueta_mensaje.destroy()
        if self.lista_desplegable:
            self.lista_desplegable.destroy()
        if self.etiqueta_circulo:
            self.etiqueta_circulo.destroy()
    def disable_main_bottons(self): # desabilita los tres botones principales de la interfaz
        self.botton_mi.config(state=tk.DISABLED)
        self.botton_mg.config(state=tk.DISABLED)
        self.botton_excel.config(state=tk.DISABLED)
    def enable_main_bottons(self): # habilita los tres botones principales de la interfaz
        self.botton_mi.config(state=tk.NORMAL)
        self.botton_mg.config(state=tk.NORMAL)
        self.botton_excel.config(state=tk.NORMAL)
    def enable_comenzar_scraper(self):
        self.matricula_caja = self.box_matricula.get()
        print(self.matricula_caja)
        if self.matricula_caja.isdigit():
            self.boton_comenzar.config(state="normal")
        else:
            self.boton_comenzar.config(state="disabled")
    def enable_box_matricula(self):
        if self.box_matricula:
            self.box_matricula.config(state="normal")

#===========================================ESTADOS ATRAS =============================================================
    def atras(self): # CONDICIONES SI SE OPRIME EL BOTON REGRESAR
        if self.estado_actual == "Individual":
            self.show_state("Individual")

        if self.estado_actual == "Grupal":
            self.show_state("Grupal")

        if self.estado_actual == "Archivo_cargado": #  SE ACTIVA CUANDO EL ARCHIVO HA SIDO CREADO
            self.show_state("Excel")
            self.enable_main_bottons()


        if self.estado_actual == "Scraper_finalizado": # SE ACTIVA CUANDO EL PROCESO SE HA FINALIZADO
            # CREACION
            self.etiqueta1_frame_1 = tk.Label(self.ventana, text="Buscador de matriculas inmobiliarias",font=("Arial", 18, "bold"), bg='midnight blue', fg="white")
            self.etiqueta1_frame_1.place(x=490, y=10)
            self.etiqueta2_frame_1 = tk.Label(self.ventana,text="Este scraper se enfoca unicamente en la pagina www.vur.gov.co",font=("Arial", 13, "bold"), bg='midnight blue', fg="white")
            self.etiqueta2_frame_1.place(x=450, y=80)
            # DESRUCCION
            if self.boton_descargar:
                self.boton_descargar.destroy()
            self.etiqueta_mensaje.destroy()
            self.etiqueta_alerta.destroy()
            self.boton_atras.destroy()
            self.enable_main_bottons()

        if self.estado_actual == "array_matriculas_cargado":
            self.enable_main_bottons()
            self.show_state("Grupal")
    # ========================================= ESTADOS =====================================================
    def show_state(self,estado): # INDICA EN QUE ESTADO ESTA LA INTERFAZ
        self.clear_upload_widgets() # elimino elementos de carga boton y etiqueta cargar
        self.etiqueta1_frame_1.destroy()
        self.etiqueta2_frame_1.destroy()

        if estado == "Individual":

            self.etiqueta_cargar = tk.Label(self.frame_1,text="Ingrese los datos a buscar", font=("Arial", 18,"bold"),bg='midnight blue',fg="white")
            self.etiqueta_cargar.place(x=110, y=10)
            self.box_matricula = ttk.Entry(self.frame_1,width=20,state="disable")
            self.box_matricula.place(x=100, y=60)
            self.box_matricula.bind("<KeyRelease>", lambda event: self.enable_comenzar_scraper())
            self.matricula_caja = self.box_matricula.get()
            #print(self.matricula_caja)

            # ======================================================CIRCULOS REGISTRALES======================================================
            self.lista_desplegable = AutocompleteCombobox(self.frame_1, textvariable=self.municipio_seleccionado)
            self.lista_desplegable.place(x=270, y=60)
            self.lista_desplegable.config(width=25, height=5)
            self.lista_desplegable.set(self.circulos_registrales[0])
            self.lista_desplegable.set_completion_list(self.circulos_registrales)
            self.lista_desplegable.bind("<<ComboboxSelected>>", self.guardar_municipio_seleccionado_individual )

            self.boton_comenzar = tk.Button(self.frame_1, text="Comenzar Scraper", font=("Arial", 12, "bold"), state="disabled",bg="#ADD8E6", fg="black", command=self.guardar_matricula_ejecutar)
            self.boton_comenzar.place(x=190, y=120)

        if estado == "Individual_ejecutando":
            self.disable_main_bottons()
            #DESTRUR
            self.box_matricula.destroy()
            self.boton_comenzar.destroy()
            #CREAR
            self.mostrar_mensaje_individual_ejecucion("SCRAPING EN EJECUCIÓN")
            self.mostrar_alerta_idividual_ejecucion("El bot esta en ejecución,no se recomienda cerrar la ventana ni pausar la secuencia,solo hagalo en caso de ser necesario")
            # ===================================MOSTRAR MATRICULA ================================================================
            self.etiqueta_matricula = tk.Label(text="", font=("Arial", 16, "bold"), bg="#ADD8E6", fg="black")
            self.etiqueta_matricula.place(x=590, y=350)

            self.boton_pausa = tk.Button(text="Pausar", font=("Arial", 16), bg="orange", fg="black",command=self.pausar_scraper)
            self.boton_pausa.place(x=500, y=250)
            self.boton_reanudar = tk.Button(text="Reanudar", font=("Arial", 16), bg="green", fg="black",command=self.reanudar_scraper)
            self.boton_reanudar.place(x=650, y=250)
            self.boton_parar = tk.Button(text="Parar", font=("Arial", 16), bg="red", fg="black",command=self.parar_scraper)
            self.boton_parar.place(x=820, y=250)
            self.boton_reanudar.config(state=tk.DISABLED)

        if estado == "individual_finalizado":
            # DESTRUIR
            self.boton_reanudar.destroy()
            self.boton_pausa.destroy()
            self.boton_parar.destroy()
            self.etiqueta_matricula.destroy()
            self.etiqueta_mensaje.destroy()

            if self.matricula_no_encotrada:
                self.mostrar_mensaje_individual("SCRAPING FINALIZADO")
                self.etiqueta_alerta.config(text="No se encontro la matricula , revise bien los cirterios de busqueda")
                self.etiqueta_alerta.place(x=20, y=60)
                self.etiqueta_mensaje.place(x=140, y=10)

                self.estado_actual = "Scraper_finalizado"  # condicion por si se oprime boton regresar
                self.boton_atras = tk.Button(text="Regresar", font=("Arial", 16, "bold"), bg="midnight blue",fg="white", command=self.atras)
                self.boton_atras.place(x=630, y=250)
                print("final")

                self.matricula_no_encotrada = False
            else:
                # CREAR
                self.mostrar_mensaje_individual("SCRAPING FINALIZADO")
                self.etiqueta_alerta.config(text="La busqueda ha sido realizada,recuerde el archivo quedo guardado en su escritorio")
                self.etiqueta_alerta.place(x=10, y=60)
                self.etiqueta_mensaje.place(x=140, y=10)
                self.boton_descargar = tk.Button(text="Guardar", font=("Arial", 16, "bold"), bg="midnight blue", fg="white",command=self.descargar_resultado)
                self.boton_descargar.place(x=550, y=250)

                self.estado_actual = "Scraper_finalizado"  # condicion por si se oprime boton regresar
                self.boton_atras = tk.Button(text="Regresar", font=("Arial", 16, "bold"), bg="midnight blue", fg="white",command=self.atras)
                self.boton_atras.place(x=720, y=250)
                print("final")


        if estado == "Grupal":
            self.etiqueta_cargar = tk.Label(self.frame_1, text="Seleccione el número de matriculas a buscar y el circulo registral",font=("Arial", 18, "bold"), bg='midnight blue', fg="white",wraplength=500)
            self.etiqueta_cargar.place(x=40, y=10)

            self.dropdown_num_matriculas = ttk.Combobox(self.frame_1, textvariable=self.num_matriculas,values=["1", "2", "3", "4", "5"], state="readonly")
            self.dropdown_num_matriculas.place(x=140, y=100)
            self.dropdown_num_matriculas.config(width=5, state="disabled")
            self.dropdown_num_matriculas.bind("<<ComboboxSelected>>", self.actualizar_cajas_texto)

            # ======================================================CIRCULOS REGISTRALES======================================================
            self.lista_desplegable = AutocompleteCombobox(self.frame_1, textvariable=self.municipio_seleccionado)
            self.lista_desplegable.place(x=240, y=100)
            self.lista_desplegable.config(width=25, height=5)
            self.lista_desplegable.set(self.circulos_registrales[0])
            self.lista_desplegable.set_completion_list(self.circulos_registrales)

            # Vincular el evento de clic (<Button-1>) para abrir la lista desplegable
            self.lista_desplegable.bind("<Button-1>", self.abrir_lista_desplegable)
            self.lista_desplegable.bind("<<ComboboxSelected>>", self.guardar_municipio_seleccionado_grupal)

        if estado == "grupal_ejecutando":
            # DESTRUIR
            self.boton_comenzar.destroy()
            self.boton_atras.destroy()
            self.etiqueta_verificar_matriculas_saved.destroy()
            if self.label:
                for self.label in self.labels:
                    self.label.destroy()
            if self.entry_box:
                for self.entry_box in self.entry_boxes:
                    self.entry_box.destroy()
            #CREAR
            self.mostrar_mensaje_excel_ejecucion("SCRAPING EN EJECUCIÓN")
            self.mostrar_alerta_excel_ejecucion("El bot esta en ejecución,no se recomienda cerrar la ventana ni pausar la secuencia,solo hagalo en caso de ser necesario")

            # ===================================MOSTRAR MATRICULA ================================================================
            self.etiqueta_matricula = tk.Label(text="", font=("Arial", 16, "bold"), bg="#ADD8E6", fg="black")
            self.etiqueta_matricula.place(x=590, y=350)
            # self.actualizar_etiqueta_matricula()  # Iniciar la actualización de la etiqueta de matrícula en la GUI

            self.barra_progreso = ttk.Progressbar(self.ventana, length=400, mode='determinate')
            self.barra_progreso.place(x=520, y=400)
            self.barra_progreso['value'] = 0  # Establecer la barra de progreso en 0 al inicio

            self.boton_pausa = tk.Button(text="Pausar", font=("Arial", 16), bg="orange", fg="black",command=self.pausar_scraper)
            self.boton_pausa.place(x=500, y=250)
            self.boton_reanudar = tk.Button(text="Reanudar", font=("Arial", 16), bg="green", fg="black",command=self.reanudar_scraper)
            self.boton_reanudar.place(x=650, y=250)
            self.boton_parar = tk.Button(text="Parar", font=("Arial", 16), bg="red", fg="black",command=self.parar_scraper)
            self.boton_parar.place(x=820, y=250)
            self.boton_reanudar.config(state=tk.DISABLED)

        if estado == "Excel":
            self.etiqueta_cargar = tk.Label(self.frame_1, text="Seleccione primero el circulo registral para cargar el archivo", font=("Arial", 16,"bold"),bg='midnight blue',fg="white", wraplength=400)
            self.etiqueta_cargar.place(x=90, y=10)
            # ======================================================CIRCULOS REGISTRALES======================================================
            self.lista_desplegable = AutocompleteCombobox(self.frame_1, textvariable=self.municipio_seleccionado)
            self.lista_desplegable.place(x=180, y=70)
            self.lista_desplegable.config(width=25, height=5)
            self.lista_desplegable.set(self.circulos_registrales[0])
            self.lista_desplegable.set_completion_list(self.circulos_registrales)

            # Vincular el evento de clic (<Button-1>) para abrir la lista desplegable
            self.lista_desplegable.bind("<Button-1>", self.abrir_lista_desplegable)
            self.lista_desplegable.bind("<<ComboboxSelected>>", self.guardar_municipio_seleccionado_excel)

            self.boton_cargar = tk.Button(self.frame_1,text="Cargar archivo", font=("Arial", 16,"bold"),state="disabled",bg="#ADD8E6",fg="black",width=13,command=self.cargar_archivo_excel)
            self.boton_cargar.place(x=175, y=110)

        if estado == "excel_ejecutando": # INDICA QUE EL SCRAPER ESTA EN EJECUCION
            # DESTRUIR
            self.boton_comenzar.destroy()
            self.etiqueta_mensaje.destroy()
            self.boton_atras.destroy()
            # CREAR
            self.mostrar_mensaje_excel_ejecucion("SCRAPING EN EJECUCIÓN")
            self.mostrar_alerta_excel_ejecucion("El bot esta en ejecución,no se recomienda cerrar la ventana ni pausar la secuencia,solo hagalo en caso de ser necesario")

            # ===================================MOSTRAR MATRICULA ================================================================
            self.etiqueta_matricula = tk.Label(text="", font=("Arial", 16, "bold"), bg="#ADD8E6", fg="black")
            self.etiqueta_matricula.place(x=590, y=350)
            #self.actualizar_etiqueta_matricula()  # Iniciar la actualización de la etiqueta de matrícula en la GUI

            self.barra_progreso = ttk.Progressbar(self.ventana, length=400, mode='determinate')
            self.barra_progreso.place(x=520, y=400)
            self.barra_progreso['value'] = 0  # Establecer la barra de progreso en 0 al inicio

            self.boton_pausa = tk.Button(text="Pausar", font=("Arial", 16), bg="orange", fg="black",command=self.pausar_scraper)
            self.boton_pausa.place(x=500, y=250)
            self.boton_reanudar = tk.Button(text="Reanudar", font=("Arial", 16), bg="green", fg="black",command=self.reanudar_scraper)
            self.boton_reanudar.place(x=650, y=250)
            self.boton_parar = tk.Button(text="Parar", font=("Arial", 16), bg="red", fg="black",command=self.parar_scraper)
            self.boton_parar.place(x=820, y=250)
            self.boton_reanudar.config(state=tk.DISABLED)

        if estado == "excel_parado": # INDICA SCRAPER EN PAUSA
            #DESTRUIR
            self.etiqueta_mensaje.destroy()
            self.etiqueta_alerta.destroy()
            self.boton_pausa.destroy()
            self.boton_reanudar.destroy()
            self.boton_parar.destroy()
            self.etiqueta_matricula.destroy()
            self.barra_progreso.destroy()
            print ("excel parado")
            # CREAR
            self.enable_main_bottons()
            self.show_state("Excel")

        if estado == "excel_finalizado": # INDICA  QUE EL SCRAPER HA FINALIZADO
            # DESTRUIR
            self.boton_reanudar.destroy()
            self.boton_pausa.destroy()
            self.boton_parar.destroy()
            self.etiqueta_matricula.destroy()
            self.barra_progreso.destroy()

            self.etiqueta_mensaje.destroy()
            # CREAR
            self.mostrar_mensaje_excel("SCRAPING FINALIZADO")
            self.etiqueta_alerta.config(text="La busqueda ha sido realizada,recuerde el archivo quedo guardado en su escritorio")
            self.etiqueta_alerta.place(x=10, y=60)
            self.etiqueta_mensaje.place(x=140, y=10)
            self.boton_descargar = tk.Button(text="Guardar", font=("Arial", 16, "bold"), bg="midnight blue", fg="white",command=self.descargar_resultado)
            self.boton_descargar.place(x=550, y=250)

            self.estado_actual = "Scraper_finalizado"  # condicion por si se oprime boton regresar
            self.boton_atras = tk.Button( text="Regresar", font=("Arial", 16, "bold"), bg="midnight blue",fg="white", command=self.atras)
            self.boton_atras.place(x=720, y=250)
            print ("final")
            #self.boton_descargar.config(state=tk.NORMAL)  # Habilitar el botón de descarga
#======================================MENSAJES==================================================
    # ==================================INDIVIDUAL=====================================================
    def mostrar_mensaje_individual(self,mensaje):
        self.etiqueta_mensaje = tk.Label(self.frame_1, text=mensaje, font=("Arial", 14,), bg="midnight blue",fg="white")
        self.etiqueta_mensaje.place(x=90, y=10)
    def mostrar_mensaje_individual_ejecucion (self, mensaje):
        self.etiqueta_mensaje = tk.Label(self.frame_1, text=mensaje, font=("Arial", 14,), bg="midnight blue",fg="white")
        self.etiqueta_mensaje.place(x=130, y=10)
    def mostrar_alerta_idividual_ejecucion(self,mensaje):
        self.etiqueta_alerta = tk.Label(self.frame_1, text=mensaje, font=("Arial", 14,), bg="midnight blue", fg="white",wraplength=550)
        self.etiqueta_alerta.place(x=7, y=60)
    #==================================EXCEL=====================================================
    def mostrar_mensaje_excel(self, mensaje):
        self.etiqueta_mensaje = tk.Label(self.frame_1,text=mensaje, font=("Arial", 14,),bg="midnight blue",fg="white")
        self.etiqueta_mensaje.place(x=90, y=10)
    def mostrar_mensaje_excel_ejecucion (self, mensaje):
        self.etiqueta_mensaje = tk.Label(self.frame_1, text=mensaje, font=("Arial", 14,), bg="midnight blue",fg="white")
        self.etiqueta_mensaje.place(x=130, y=10)
    def mostrar_alerta_excel_ejecucion (self, mensaje):
        self.etiqueta_alerta = tk.Label(self.frame_1, text=mensaje, font=("Arial", 14,), bg="midnight blue",fg="white",wraplength=550)
        self.etiqueta_alerta.place(x=7, y=60)
    def mostrar_circulo_seleccionado(self,mensaje):
        self.etiqueta_circulo =tk.Label(self.frame_1,text=mensaje, font=("Arial", 14,),bg="midnight blue",fg="white")
        self.etiqueta_circulo.place(x=90, y=50)
    def mostrar_ventana_espera(self):
        self.wait_window = tk.Toplevel(self.ventana)
        self.wait_window.title("Esperando")
        self.wait_window.geometry("300x300")

        # Centrar la ventana de espera
        self.window_width = self.ventana.winfo_screenwidth()  # ancho de la ventana requerido gracias a la funcion .winfo_reqwidth()
        self.window_height = self.ventana.winfo_screenheight()  # alto de la ventana requerido gracias a la funcion .winfo_reqheight()
        self.wventana_e = 300
        self.hventana_e = 300
        self.position_right = int(self.window_width / 2 - self.wventana_e / 2)  # posicion de la ventana la funcion winfo_screenwidth() determina el ancho de la pantalla
        self.position_down = int(self.window_height / 2 - self.hventana_e / 2)  # posicion de la ventana la funcion winfo_screenheight() determina el alto de la pantalla
        self.wait_window.geometry("+{}+{}".format(self.position_right,self.position_down))  # los valores position_right, position_down van en los corchetes gracias a la funcion .format
        font = ("Helvetica", 16, "bold")
        self.wait_label1 = tk.Label(self.wait_window, text="Cerrando Scraper...",font=font)
        self.wait_label1.pack()
        self.wait_label2 = tk.Label(self.wait_window, text=" No oprima ningun boton y no cierre la aplicación ",font=font,fg="red",wraplength=270)
        self.wait_label2.pack()

        # Cargar la imagen JPEG usando Pillow (PIL)
        imagen_alerta = Image.open("D:\pythonProject\VUR\Alerta.jpg")  # Cambia "ruta_de_la_imagen.jpg" a la ubicación de tu imagen JPEG
        imagen_alerta = imagen_alerta.resize((200, 200))  # Cambia el tamaño de la imagen según tus necesidades
        self.imagen = ImageTk.PhotoImage(imagen_alerta)

        # Mostrar la imagen en la ventana
        self.imagen_label = tk.Label(self.wait_window, image=self.imagen)
        self.imagen_label.pack()

        self.ventana.after(100, self.verificar_scraper_detenido)  # Verificar si el scraper se ha detenido
    def cargar_archivo_excel(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Archivo Excel", "*.xlsx")])
        self.clear_upload_widgets()  # elimino elementos de carga boton y etiqueta cargar

        if self.file_path:
            if self.file_path.endswith(".xlsx"):
                self.nombre_archivo = self.file_path.split("/")[-1]  # Obtener el nombre del archivo de la ruta
                self.mostrar_mensaje_excel(f"¡Archivo {self.nombre_archivo} se cargo exitosamente!")
                self.mostrar_circulo_seleccionado(f"¡ha seleccionado {self.seleccion_concatenado} !")
                self.boton_comenzar = tk.Button(self.frame_1,text="Comenzar Scraper", font=("Arial", 12,"bold"),bg="#ADD8E6",fg="black",command=lambda: self.ejecutar_scraper(archivo=self.file_path,circulo_registral=self.seleccion_concatenado,usuario=self.usuario,contrasena=self.contrasena))
                self.boton_comenzar.place(x=100, y=100)
                self.disable_main_bottons()

                self.estado_actual = "Archivo_cargado" # condicion por si se oprime boton regresar

                self.boton_atras = tk.Button(self.frame_1,text="Regresar", font=("Arial", 12,"bold"), bg="#ADD8E6",fg="black",command=self.atras)
                self.boton_atras.place(x=330, y=100)

            else:
                self.mostrar_mensaje_excel("Archivo no valido, intente de nuevo")
                self.boton_cargar = tk.Button(self.frame_1, text="Cargar archivo", font=("Arial", 16, "bold"),bg="#ADD8E6", fg="black", width=13, command=self.cargar_archivo_excel)
                self.boton_cargar.place(x=175, y=70)
        else:
            #No se ha seleccionado ningún archivo
            self.show_state("Excel")
    def guardar_matricula_ejecutar(self):
        matricula_individual = self.box_matricula.get()  # Obtén el valor actual
        print(matricula_individual)
        self.ejecutar_scraper(matricula_individual=matricula_individual,circulo_registral=self.seleccion_concatenado,usuario=self.usuario,contrasena=self.contrasena)
    def guardar_array_matriculas(self):
        self.disable_main_bottons()
        self.dropdown_num_matriculas.config(state=tk.DISABLED)
        self.lista_desplegable.config(state="disable")
        self.boton_reset.destroy()
        all_entries_completed = all(entry.get() for entry in self.entry_boxes) # METODO COMPRENSION DE LISTA verifica si todas las casillas estan llenas
        # OTRA MANERA DE HACERLO
        #all_entries_completed = True
        #for entry in self.entry_boxes:
            #if not entry.get():
                #all_entries_completed = False
                #break
        if all_entries_completed: # si todas las casillas estan llenas
            # Obtener los valores ingresados en las cajas de texto y guardarlos en la lista self.matriculas
            self.matricula_array = [entry.get() for entry in self.entry_boxes] # METODO COMPRENSION DE LISTA
            #OTRA MANERA DE HACERLO
            #self.matricula_array = []
            #for entry in self.entry_boxes:
                #matricula = entry.get()
                #self.matricula_array.append(matricula)
            print(self.matricula_array)
            self.boton_guardar.config(state=tk.DISABLED)
            if self.entry_boxes:
                for self.entry_box in self.entry_boxes: #desabilitar las cajar para verificar la seleccion
                    self.entry_box.config(state=tk.DISABLED)

            self.etiqueta_verificar_matriculas_saved = tk.Label(text="Verifique su elección", font=("Arial", 18,), bg="#ADD8E6",fg="black")
            self.etiqueta_verificar_matriculas_saved.place(x=790,y=250)
            self.boton_comenzar = tk.Button(text="Comenzar Scraper", font=("Arial", 10,"bold"),bg="midnight blue",fg="white",command=lambda: self.ejecutar_scraper(matricula_array=self.matricula_array,circulo_registral=self.seleccion_concatenado,usuario=self.usuario,contrasena=self.contrasena))
            self.boton_comenzar.place(x=780,y=300)

            self.estado_actual = "array_matriculas_cargado"  # condicion por si se oprime boton regresar

            self.boton_atras = tk.Button( text="Regresar", font=("Arial", 10, "bold"), bg="midnight blue",fg="white", command=self.atras)
            self.boton_atras.place(x=950, y=300)
        else:
            messagebox.showerror("Campos Incompletos", "Debe diligenciar todas las casillas antes de guardar.")
            self.estado_actual = "array_matriculas_cargado"  # condicion por si se oprime boton regresar
            self.boton_reset = tk.Button(text="Reset", font=("Arial", 14, "bold"), bg="midnight blue", fg="white",command=self.atras)
            self.boton_reset.place(x=600, y=280 + 50 * self.num_seleccionado)
    def guardar_municipio_seleccionado_excel(self,event):
        self.seleccion = self.municipio_seleccionado.get()

        # Verificar si se ha seleccionado un elemento de la lista desplegable
        if self.boton_cargar:
            if self.municipio_seleccionado.get():
                self.boton_cargar["state"] = "normal"
            else:
                self.boton_cargar["state"] = "disabled"

        # Concatenar "ORIP - " al valor seleccionado
        self.seleccion_concatenado = "ORIP - " + self.seleccion
        # Ahora 'seleccion' contiene el municipio seleccionado
        print("Municipio seleccionado:", self.seleccion_concatenado)
    def guardar_municipio_seleccionado_grupal(self,event):
        self.seleccion = self.municipio_seleccionado.get()
        self.dropdown_num_matriculas.config(width=5, state="normal")

        # Concatenar "ORIP - " al valor seleccionado
        self.seleccion_concatenado = "ORIP - " + self.seleccion
        # Ahora 'seleccion' contiene el municipio seleccionado
        print("Municipio seleccionado:", self.seleccion_concatenado)
    def guardar_municipio_seleccionado_individual(self,event):
        self.enable_box_matricula()
        self.seleccion = self.municipio_seleccionado.get()

        # Concatenar "ORIP - " al valor seleccionado
        self.seleccion_concatenado = "ORIP - " + self.seleccion
        # Ahora 'seleccion' contiene el municipio seleccionado
        print("Municipio seleccionado:", self.seleccion_concatenado)
    def abrir_lista_desplegable(self, event):
        # Abrir la lista desplegable automáticamente
        self.lista_desplegable.event_generate("<Down>")
    def ejecutar_scraper(self,archivo= None, matricula_individual= None,matricula_array= None,circulo_registral = None,usuario=None,contrasena=None):

        if matricula_individual:
            print("matricula individual")
            # Si se ingresó una matrícula individual, usarla para buscar
            #matricula_individual = int(self.matricula_caja)  # Obtener la matrícula individual ingresada
            matricula_individual = self.matricula_caja
            self.show_state("Individual_ejecutando")  # Estado ejecutando
            self.hilo_scraper = threading.Thread(target=self.ejecutar_scraper_en_hilo, args=(None,matricula_individual,None,circulo_registral,usuario,contrasena)) # ES NECESARIO PASAR TODOS LOS ARGUMENTO EN EL ORDEN CORRECTO
            self.hilo_scraper.daemon = True
            self.hilo_scraper.start()  # Ejecución en segundo hilo
        elif archivo and archivo.endswith(".xlsx"):
            print("archivo")
            # Si no se ingresó una matrícula individual, verificar si se seleccionó un archivo Excel válido
            #archivo = self.file_path  # Obtener la ruta del archivo Excel
            self.show_state("excel_ejecutando")  # Estado ejecutando
            self.hilo_scraper = threading.Thread(target=self.ejecutar_scraper_en_hilo, args=(archivo,None,None,circulo_registral,usuario,contrasena))
            self.hilo_scraper.daemon = True
            self.hilo_scraper.start()  # Ejecución en segundo hilo
        elif matricula_array: # grupal
            print("matricula array")
            self.show_state("grupal_ejecutando")
            self.hilo_scraper = threading.Thread(target=self.ejecutar_scraper_en_hilo, args=(None,None,matricula_array,circulo_registral,usuario,contrasena))  # ES NECESARIO PASAR TODOS LOS ARGUMENTO EN EL ORDEN CORRECTO
            self.hilo_scraper.daemon = True
            self.hilo_scraper.start()  # Ejecución en segundo hilo
        else:
            # Si no se ingresó una matrícula individual ni se seleccionó un archivo válido, mostrar un mensaje de error
            print("Error","Por favor, ingrese una matrícula individual válida o seleccione un archivo Excel (.xlsx).")
    def ejecutar_scraper_en_hilo(self, archivo=None,matricula_individual=None,matricula_array=None,circulo_registral=None,usuario=None,contrasena=None):
        if matricula_individual:
            print("matricula individual")
            hunter = VurScraper(matricula_individual=matricula_individual,circulo_registral=circulo_registral,usuario=usuario,contrasena=contrasena)
            self.hunter = hunter  # Guardar una referencia a la instancia de VurScraper
            self.actualizar_etiqueta_matricula()
            self.actualizar_barra()
            hunter.main()

            # El proceso ha terminado
            if not self.hunter.detener:  # si detener el falso
                self.ventana.event_generate("<<IndividualTerminado>>")  # Generar evento personalizado
        elif archivo:
            print("archivo")
            hunter = VurScraper(archivo=archivo,circulo_registral=circulo_registral,usuario=usuario,contrasena=contrasena)
            self.hunter = hunter  # Guardar una referencia a la instancia de VurScraper
            self.actualizar_etiqueta_matricula()
            self.actualizar_barra()
            hunter.main()
            print("terminmadoooo")
            #self.set_terminado()

            # El proceso ha terminado
            if not self.hunter.detener:  # si detener el falso
                self.ventana.event_generate("<<ExcelTerminado>>")  # Generar evento personalizado
        elif matricula_array: #grupal
            print("matricula_array")
            hunter = VurScraper(matricula_array=matricula_array,circulo_registral=circulo_registral,usuario=usuario,contrasena=contrasena)
            self.hunter = hunter  # Guardar una referencia a la instancia de VurScraper
            self.actualizar_etiqueta_matricula()
            self.actualizar_barra()
            hunter.main()

            # El proceso ha terminado
            if not self.hunter.detener:  # si detener el falso
                self.ventana.event_generate("<<ExcelTerminado>>")  # Generar evento personalizado
        else:
            return
            # El proceso ha terminado
    def verificar_scraper_detenido(self):
        if not self.hilo_scraper.is_alive():  # Si el hilo del scraper ha terminado
            self.wait_window.destroy()  # Cerrar la ventana de espera
            self.ventana.event_generate("<<ScraperParado>>")
        else:
            self.ventana.after(100, self.verificar_scraper_detenido)  # Continuar verificando
    def actualizar_etiqueta_matricula(self):
        if self.hilo_scraper.is_alive():
            if self.hunter.matricula_actual == self.hunter.matricula_no_encontrada:
               print("matricula no encontrada")
               self.matricula_no_encotrada = True
               self.etiqueta_matricula.config(text=f"Matrícula actual: {self.hunter.matricula_actual}")
               self.etiqueta_matricula.place(x=500, y=350)
            else:
               self.etiqueta_matricula.config(text=f"Matrícula actual: {self.hunter.matricula_actual}")

            self.ventana.after(1000,self.actualizar_etiqueta_matricula)  # Llama de nuevo a la función después de 1 segundo
    def actualizar_barra(self):
        if self.hilo_scraper.is_alive():
            matricula_actual = self.hunter.indice_actual
            total_matriculas = self.hunter.total_matriculas
            #if total_matriculas > 0:
            porcentaje_completado = (matricula_actual / total_matriculas) * 100
            self.barra_progreso['value'] = porcentaje_completado
            self.ventana.after(1000, self.actualizar_barra)
    def actualizar_cajas_texto(self, event):
        self.num_seleccionado = int(self.num_matriculas.get())

        # Eliminar las cajas de texto y etiquetas anteriores
        for self.label in self.labels:
            self.label.destroy()
        for self.entry_box in self.entry_boxes:
            self.entry_box.destroy()
        if hasattr(self, "boton_guardar"): # if self.boton_guardar:///hasattr es una función incorporada que se puede utilizar para verificar cualquier atributo en un objeto.
            self.boton_guardar.destroy()
        self.labels = []
        self.entry_boxes = []  # Limpiar la lista

        # Crear nuevas cajas de texto según el número seleccionado
        for i in range(self.num_seleccionado):
            label_text = f"Matrícula {i + 1}:"
            self.entry_box = tk.Entry(self.ventana)
            self.label = tk.Label(text=label_text, font=("Arial", 14), bg='#ADD8E6')
            self.label.place(x=400, y=250 + 50 * i)
            self.entry_box.place(x=600, y=250 + 50 * i)
            self.entry_boxes.append(self.entry_box)
            self.labels.append(self.label)

            # Configurar un botón para guardar las matrículas
        self.boton_guardar= tk.Button(self.ventana, text="Guardar Matrículas", font=("Arial", 14, "bold"), bg="midnight blue", fg="white", command=self.guardar_array_matriculas)
        self.boton_guardar.place(x=400, y=280 + 50 * self.num_seleccionado)

        # condicino falta pero la aplico para configurar el boton reset
        self.estado_actual = "array_matriculas_cargado"  # condicion por si se oprime boton regresar
        self.boton_reset = tk.Button(text="Reset", font=("Arial", 14, "bold"), bg="midnight blue", fg="white",command=self.atras)
        self.boton_reset.place(x=600, y=280 + 50 * self.num_seleccionado)
    def pausar_scraper(self):
        self.boton_pausa.config(state=tk.DISABLED)
        self.boton_reanudar.config(state=tk.NORMAL)
        self.hunter.pausar()
    def reanudar_scraper(self):
        self.boton_pausa.config(state=tk.NORMAL)
        self.boton_reanudar.config(state=tk.DISABLED)
        self.hunter.reanudar()
    def parar_scraper(self):
        if self.hilo_scraper and self.hilo_scraper.is_alive():
            self.hunter.detener_proceso()
            self.boton_parar.config(state=tk.DISABLED)
            self.mostrar_ventana_espera()
    def descargar_resultado(self):
        ruta_archivo_resultado = self.hunter.ruta_archivo_salida  # Obtén la ruta del archivo resultante desde la instancia de VurScraper
        if ruta_archivo_resultado:
            file_path = filedialog.asksaveasfilename(initialfile="proyecto",defaultextension=".xlsx", filetypes=[("Archivo Excel", "*.xlsx")])
            if file_path:
                shutil.copy(ruta_archivo_resultado, file_path)  # Copia el archivo resultante a la ubicación deseada
            #filedialog.asksaveasfilename(initialfile=filename, defaultextension=".xlsx",filetypes=[("Archivo Excel", "*.xlsx")], title="Guardar archivo")

if __name__ == "__main__":
    gui = Menu()
    #ui.ventana.mainloop()
    gui.inicio.mainloop()