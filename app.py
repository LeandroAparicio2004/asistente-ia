import tkinter as tk
from tkinter import filedialog
import threading
import os
import queue
import shutil
from datetime import datetime

from agent import interpretar
from executor import ACCIONES, ACCIONES_ALIAS
from voice import hablar, escuchar
from history import registrar, ver_historial
from memory import limpiar_memoria
from reminders import iniciar_monitor
from actions.programadas import iniciar_monitor_programadas
from config import SANDBOX_PATH

# ─── PALETA WARM EDITORIAL ────────────────────────────────────────────────────

C = {
    "bg":           "#13120f",
    "surface":      "#1a1916",
    "surface2":     "#201f1b",
    "surface3":     "#272622",
    "border":       "#2e2d28",
    "border2":      "#3a3832",
    "accent":       "#c8a96e",
    "accent2":      "#a8855a",
    "accent_dim":   "#6b5438",
    "accent_dark":  "#1e180f",
    "text":         "#e8e0d0",
    "text_dim":     "#7a7060",
    "text_dimmer":  "#3a3528",
    "user_left":    "#c8a96e",
    "bot_left":     "#3a3832",
    "error_left":   "#8b3a3a",
    "error_text":   "#e07070",
    "warn":         "#c8903a",
    "notif_left":   "#4a6b3a",
    "notif_text":   "#90c870",
    "sys_text":     "#3a3528",
    "select_bg":    "#2e2510",
    "select_fg":    "#c8a96e",
}

FONT_SERIF = ("Georgia", 12)
FONT_SERIF_SM = ("Georgia", 10)
FONT_SERIF_LG = ("Georgia", 14)
FONT_SERIF_TITLE = ("Georgia", 15, "bold")
FONT_MONO = ("Consolas", 10)
FONT_MONO_SM = ("Consolas", 9)

mensaje_queue = queue.Queue()


# ─── MENSAJE ──────────────────────────────────────────────────────────────────

class Mensaje(tk.Frame):
    def __init__(self, parent, texto, rol, app_ref, **kwargs):
        super().__init__(parent, bg=C["bg"], **kwargs)
        self.app_ref = app_ref
        self.texto_completo = texto
        self.rol = rol
        self._construir(texto, rol)

    def _construir(self, texto, rol):
        es_usuario = rol == "usuario"
        es_error = rol == "error"
        es_sistema = rol == "sistema"
        es_notif = rol == "notificacion"

        if es_usuario:
            color_linea = C["user_left"]
            fg = C["text"]
            bg_msg = C["surface2"]
            pad_i = 80
            pad_d = 16
            anchor_pack = "e"
            mostrar_botones = True
        elif es_error:
            color_linea = C["error_left"]
            fg = C["error_text"]
            bg_msg = C["surface"]
            pad_i = 16
            pad_d = 80
            anchor_pack = "w"
            mostrar_botones = False
        elif es_sistema:
            color_linea = C["sys_text"]
            fg = C["sys_text"]
            bg_msg = C["bg"]
            pad_i = 40
            pad_d = 40
            anchor_pack = "center"
            mostrar_botones = False
        elif es_notif:
            color_linea = C["notif_left"]
            fg = C["notif_text"]
            bg_msg = C["surface"]
            pad_i = 16
            pad_d = 80
            anchor_pack = "w"
            mostrar_botones = True
        else:
            color_linea = C["bot_left"]
            fg = C["text"]
            bg_msg = C["surface"]
            pad_i = 16
            pad_d = 80
            anchor_pack = "w"
            mostrar_botones = True

        wrapper = tk.Frame(self, bg=C["bg"])
        wrapper.pack(
            fill="x" if es_sistema else "none",
            anchor=anchor_pack,
            padx=(pad_i, pad_d),
            pady=(3, 3)
        )

        # Línea vertical de color
        if not es_sistema:
            tk.Frame(wrapper, bg=color_linea, width=2).pack(
                side="left", fill="y"
            )

        contenido = tk.Frame(wrapper, bg=bg_msg)
        contenido.pack(side="left", fill="x", expand=True)

        # Meta row — timestamp + botones
        meta = tk.Frame(contenido, bg=bg_msg)
        meta.pack(fill="x", padx=(10, 8), pady=(5, 0))

        ts = datetime.now().strftime("%H:%M")
        rol_label = {
            "usuario": "tú",
            "asistente": "asistente",
            "error": "error",
            "sistema": "",
            "notificacion": "recordatorio"
        }.get(rol, rol)

        tk.Label(
            meta,
            text=f"{rol_label}  ·  {ts}",
            bg=bg_msg, fg=C["text_dim"],
            font=FONT_MONO_SM
        ).pack(side="left")

        if mostrar_botones:
            btn_f = tk.Frame(meta, bg=bg_msg)
            btn_f.pack(side="right")

            def _hacer_boton(sym, cmd):
                b = tk.Label(
                    btn_f, text=sym,
                    bg=bg_msg, fg=C["text_dim"],
                    font=FONT_MONO_SM, cursor="hand2"
                )
                b.pack(side="left", padx=3)
                b.bind("<Button-1>", lambda e: cmd())
                b.bind("<Enter>", lambda e: b.configure(fg=C["accent"]))
                b.bind("<Leave>", lambda e: b.configure(fg=C["text_dim"]))

            _hacer_boton("copiar", self._copiar)
            _hacer_boton("leer", self._leer)

        # Separador fino
        tk.Frame(contenido, bg=C["border"], height=1).pack(
            fill="x", padx=10, pady=(3, 0)
        )

        # Texto seleccionable
        txt = tk.Text(
            contenido,
            bg=bg_msg, fg=fg,
            font=FONT_SERIF,
            relief="flat",
            wrap="word",
            state="normal",
            cursor="xterm",
            selectbackground=C["select_bg"],
            selectforeground=C["select_fg"],
            exportselection=True,
            height=1,
            padx=10, pady=6,
            spacing1=3, spacing3=3,
            borderwidth=0
        )
        txt.insert("1.0", texto)
        txt.configure(state="disabled")
        txt.pack(fill="x", pady=(0, 6))
        self._txt = txt
        self.after(100, lambda: self._ajustar(txt))

    def _ajustar(self, txt):
        txt.configure(state="normal")
        txt.update_idletasks()
        altura = txt.count("1.0", "end", "displaylines")
        if altura:
            lineas = altura[0]
        else:
            lineas = int(txt.index("end-1c").split(".")[0])
        txt.configure(height=max(1, lineas + 1), state="disabled")

    def _copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.texto_completo)
        self.app_ref._set_status("Copiado", C["accent"])

    def _leer(self):
        texto = self.texto_completo
        threading.Thread(
            target=lambda: hablar(texto),
            daemon=True
        ).start()
        try:
            self.app_ref._set_status("Leyendo...", C["accent_dim"])
        except Exception:
            pass


# ─── APP ──────────────────────────────────────────────────────────────────────

class AsistenteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asistente")
        self.geometry("960x720")
        self.minsize(700, 500)
        self.configure(bg=C["bg"])

        self.imagen_adjunta = None
        self.procesando = False
        self.escuchando = False
        self._modelo_actual = "LLaMA 3.3"
        self._placeholder = True

        self._build()
        self._iniciar_monitores()
        self._verificar_queue()
        self.after(400, self._bienvenida)

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_chat()
        self._build_img_bar()
        self._build_input()
        self._build_status()

    # ─── HEADER ───────────────────────────────────────────────────────────────

    def _build_header(self):
        h = tk.Frame(self, bg=C["surface"], height=50)
        h.grid(row=0, column=0, sticky="ew")
        h.grid_propagate(False)
        h.grid_columnconfigure(1, weight=1)

        tk.Frame(h, bg=C["accent"], height=1).place(
            x=0, rely=0, relwidth=1
        )

        left = tk.Frame(h, bg=C["surface"])
        left.grid(row=0, column=0, padx=20, pady=10)

        tk.Label(
            left, text="Asistente",
            bg=C["surface"], fg=C["text"],
            font=FONT_SERIF_TITLE
        ).pack(side="left")

        tk.Label(
            left, text=" — personal",
            bg=C["surface"], fg=C["text_dim"],
            font=FONT_SERIF_SM
        ).pack(side="left", pady=(3, 0))

        self.lbl_modelo = tk.Label(
            h, text=self._modelo_actual,
            bg=C["surface"], fg=C["accent_dim"],
            font=FONT_MONO_SM
        )
        self.lbl_modelo.grid(row=0, column=1)

        tk.Label(
            h,
            text=os.path.basename(SANDBOX_PATH),
            bg=C["surface"], fg=C["text_dimmer"],
            font=FONT_MONO_SM
        ).grid(row=0, column=2, padx=20)

    # ─── CHAT ─────────────────────────────────────────────────────────────────

    def _build_chat(self):
        w = tk.Frame(self, bg=C["bg"])
        w.grid(row=1, column=0, sticky="nsew")
        w.grid_columnconfigure(0, weight=1)
        w.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            w, bg=C["bg"],
            highlightthickness=0, bd=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        sb = tk.Scrollbar(w, orient="vertical", command=self.canvas.yview,
                          bg=C["surface"], troughcolor=C["bg"],
                          relief="flat", bd=0, width=6)
        sb.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=sb.set)

        self.chat_frame = tk.Frame(self.canvas, bg=C["bg"])
        self._cwin = self.canvas.create_window(
            (0, 0), window=self.chat_frame, anchor="nw"
        )

        self.chat_frame.bind("<Configure>", self._on_cfg)
        self.canvas.bind("<Configure>", self._on_canvas_cfg)
        self.bind_all("<MouseWheel>", self._on_scroll)

    # ─── IMG BAR ──────────────────────────────────────────────────────────────

    def _build_img_bar(self):
        self.img_bar = tk.Frame(self, bg=C["accent_dark"], height=26)
        self.lbl_img = tk.Label(
            self.img_bar, text="",
            bg=C["accent_dark"], fg=C["accent"],
            font=FONT_MONO_SM
        )
        self.lbl_img.pack(side="left", padx=12)
        tk.Button(
            self.img_bar, text="×",
            bg=C["accent_dark"], fg=C["text_dim"],
            relief="flat", font=("Georgia", 11),
            cursor="hand2",
            activebackground=C["accent_dark"],
            activeforeground=C["accent"],
            command=self._quitar_imagen
        ).pack(side="right", padx=8)

    # ─── INPUT ────────────────────────────────────────────────────────────────

    def _build_input(self):
        tk.Frame(self, bg=C["border2"], height=1).grid(
            row=3, column=0, sticky="ew"
        )

        inp = tk.Frame(self, bg=C["surface"], height=76)
        inp.grid(row=4, column=0, sticky="ew")
        inp.grid_propagate(False)
        inp.grid_columnconfigure(1, weight=1)

        btn_cfg = dict(
            bg=C["surface"], fg=C["text_dim"],
            relief="flat", font=("Georgia", 13),
            cursor="hand2", width=3,
            activebackground=C["surface2"],
            activeforeground=C["accent"]
        )

        self.btn_img_inp = tk.Button(
            inp, text="⊕", **btn_cfg,
            command=self._adjuntar_imagen
        )
        self.btn_img_inp.grid(row=0, column=0, padx=(14, 4), pady=14)

        # Entrada multilínea
        ef = tk.Frame(inp, bg=C["border"])
        ef.grid(row=0, column=1, padx=4, pady=14, sticky="ew")

        self.entrada = tk.Text(
            ef,
            bg=C["surface2"], fg=C["text_dim"],
            insertbackground=C["accent"],
            relief="flat", font=FONT_SERIF,
            height=2, wrap="word",
            padx=12, pady=8,
            selectbackground=C["select_bg"],
            selectforeground=C["select_fg"],
            borderwidth=0,
            spacing1=2, spacing3=2
        )
        self.entrada.pack(padx=1, pady=1, fill="both")

        # Placeholder
        self._ph_texto = "Escribí aquí...   Shift+Enter para nueva línea"
        self.entrada.insert("1.0", self._ph_texto)
        self.entrada.bind("<FocusIn>", self._ph_in)
        self.entrada.bind("<FocusOut>", self._ph_out)
        self.entrada.bind("<Return>", self._on_enter)
        self.entrada.bind("<Shift-Return>", self._on_shift_enter)

        self.btn_voz = tk.Button(
            inp, text="◎", **btn_cfg,
            command=self._toggle_voz
        )
        self.btn_voz.grid(row=0, column=2, padx=4, pady=14)

        self.btn_send = tk.Button(
            inp, text="→",
            bg=C["accent_dim"], fg=C["bg"],
            relief="flat", font=("Georgia", 16, "bold"),
            cursor="hand2", width=3,
            activebackground=C["accent"],
            activeforeground=C["bg"],
            command=self._enviar
        )
        self.btn_send.grid(row=0, column=3, padx=(4, 14), pady=14)

    def _build_status(self):
        self.status_lbl = tk.Label(
            self, text="Listo",
            bg=C["bg"], fg=C["text_dimmer"],
            font=FONT_MONO_SM, anchor="w"
        )
        self.status_lbl.grid(row=5, column=0, sticky="ew", padx=16, pady=(1, 3))

    # ─── PLACEHOLDER ──────────────────────────────────────────────────────────

    def _ph_in(self, e):
        contenido = self.entrada.get("1.0", "end-1c")
        if contenido == self._ph_texto:
            self.entrada.delete("1.0", "end")
            self.entrada.configure(fg=C["text"])
            self._placeholder = False

    def _ph_out(self, e=None):
        contenido = self.entrada.get("1.0", "end-1c").strip()
        if not contenido:
            self.entrada.delete("1.0", "end")
            self.entrada.insert("1.0", self._ph_texto)
            self.entrada.configure(fg=C["text_dim"])
            self._placeholder = True

    def _on_enter(self, e):
        if not self._placeholder:
            self._enviar()
        return "break"

    def _on_shift_enter(self, e):
        return None

    # ─── CHAT MÉTODOS ─────────────────────────────────────────────────────────

    def _agregar_mensaje(self, texto, rol):
        m = Mensaje(self.chat_frame, texto, rol, self)
        m.pack(fill="x", pady=0)
        self.after(100, self._scroll_bottom)

    def _scroll_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _on_cfg(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_cfg(self, e):
        self.canvas.itemconfig(self._cwin, width=e.width)

    def _on_scroll(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _bienvenida(self):
        self._agregar_mensaje(
            "Hola. Podés escribir, hablar o adjuntar una imagen.\n"
            "Shift+Enter para salto de línea · copiar y leer en cada mensaje.",
            "asistente"
        )

    def _set_status(self, texto, color=None):
        self.status_lbl.configure(
            text=texto,
            fg=color or C["text_dimmer"]
        )

    def _set_modelo(self, nombre):
        self._modelo_actual = nombre
        self.lbl_modelo.configure(text=nombre)

    # ─── IMAGEN ───────────────────────────────────────────────────────────────

    def _adjuntar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")]
        )
        if not ruta:
            return
        nombre = os.path.basename(ruta)
        shutil.copy2(ruta, os.path.join(SANDBOX_PATH, nombre))
        self.imagen_adjunta = nombre
        self.lbl_img.configure(text=f"  imagen adjunta:  {nombre}")
        self.img_bar.grid(row=2, column=0, sticky="ew")
        self._set_status(f"Imagen lista: {nombre}", C["accent"])

    def _quitar_imagen(self):
        self.imagen_adjunta = None
        self.img_bar.grid_remove()
        self._set_status("Listo")

    # ─── VOZ ──────────────────────────────────────────────────────────────────

    def _toggle_voz(self):
        if self.procesando or self.escuchando:
            return
        self.escuchando = True
        self.btn_voz.configure(fg=C["error_text"], text="●")
        self._set_status("Escuchando...", C["error_text"])
        threading.Thread(target=self._escuchar_voz, daemon=True).start()

    def _escuchar_voz(self):
        texto = escuchar()
        self.escuchando = False
        self.after(0, lambda: self.btn_voz.configure(fg=C["text_dim"], text="◎"))
        if texto:
            self.after(0, lambda: self._set_entrada(texto))
            self.after(100, self._enviar)
        else:
            self.after(0, lambda: self._set_status("No se escuchó nada", C["warn"]))

    def _set_entrada(self, texto):
        self.entrada.delete("1.0", "end")
        self.entrada.configure(fg=C["text"])
        self.entrada.insert("1.0", texto)
        self._placeholder = False

    # ─── ENVIAR ───────────────────────────────────────────────────────────────

    def _enviar(self):
        if self.procesando:
            return
        texto = self.entrada.get("1.0", "end-1c").strip()
        if not texto or texto == self._ph_texto:
            return
        
        self.entrada.delete("1.0", "end")
        self.entrada.configure(fg=C["text_dim"])
        self._placeholder = False
        
        if self.imagen_adjunta:
            msg = f"{texto} [imagen: {self.imagen_adjunta}]"
            self._agregar_mensaje(f"{texto} - {self.imagen_adjunta}", "usuario")
            self._quitar_imagen()
        else:
            msg = texto
            self._agregar_mensaje(texto, "usuario")
            
        self.procesando = True
        self.btn_send.configure(state="disabled", fg=C["text_dim"])
        self._set_status("Pensando...", C["accent_dim"])
        
        threading.Thread(target=self._procesar, args=(msg,), daemon=True).start()

    # ─── PROCESAR ─────────────────────────────────────────────────────────────

    def _procesar(self, mensaje):
        try:
            resultado = interpretar(mensaje)
            accion = resultado.get("accion")
            parametros = resultado.get("parametros", {})
            descripcion = resultado.get("descripcion", "")

            from agent import _modelo_actual as ma
            if ma:
                self.after(0, lambda: self._set_modelo(ma))

            if accion == "ninguna":
                self.after(0, lambda: self._agregar_mensaje(descripcion, "asistente"))
                self.after(0, lambda: self._set_status("Listo"))
                threading.Thread(target=lambda: hablar(descripcion), daemon=True).start()
                self.after(0, self._fin)

            elif accion == "error":
                self.after(0, lambda: self._agregar_mensaje(descripcion, "error"))
                self.after(0, lambda: self._set_status("Error", C["error_text"]))
                self.after(0, self._fin)

            elif accion == "ver_historial":
                h = ver_historial()
                self.after(0, lambda: self._agregar_mensaje(h, "asistente"))
                self.after(0, lambda: self._set_status("Listo"))
                self.after(0, self._fin)

            elif accion == "limpiar_memoria":
                self.after(0, lambda: self._confirmar(
                    "¿Limpiar toda la memoria del asistente?",
                    lambda: self._exec("limpiar_memoria", {})
                ))

            else:
                accion_real = ACCIONES_ALIAS.get(accion, accion)
                if accion_real not in ACCIONES:
                    self.after(0, lambda: self._agregar_mensaje(
                        f"Acción desconocida: {accion}", "error"
                    ))
                    self.after(0, lambda: self._set_status("Listo"))
                    self.after(0, self._fin)
                else:
                    self.after(0, lambda: self._confirmar(
                        descripcion,
                        lambda: self._exec(accion_real, parametros)
                    ))

        except Exception as e:
            self.after(0, lambda: self._agregar_mensaje(f"Error: {str(e)}", "error"))
            self.after(0, lambda: self._set_status("Error", C["error_text"]))
            self.after(0, self._fin)

    def _exec(self, accion, parametros):
        def _run():
            try:
                self.after(0, lambda: self._set_status("Ejecutando...", C["accent"]))
                res = ACCIONES[accion](**parametros)
                registrar(accion, parametros, res)
                self.after(0, lambda: self._agregar_mensaje(res, "asistente"))
                self.after(0, lambda: self._set_status("Listo"))
                threading.Thread(target=lambda: hablar(res), daemon=True).start()
            except Exception as e:
                err = f"Error: {str(e)}"
                self.after(0, lambda: self._agregar_mensaje(err, "error"))
                self.after(0, lambda: self._set_status("Error", C["error_text"]))
            finally:
                self.after(0, self._fin)
        threading.Thread(target=_run, daemon=True).start()

    def _fin(self):
        self.procesando = False
        self.btn_send.configure(state="normal", fg=C["bg"])

    # ─── CONFIRMACIÓN ─────────────────────────────────────────────────────────

    def _confirmar(self, descripcion, callback):
        v = tk.Toplevel(self)
        v.title("")
        v.geometry("460x185")
        v.resizable(False, False)
        v.configure(bg=C["surface"])
        v.grab_set()
        v.lift()

        tk.Frame(v, bg=C["accent"], height=1).pack(fill="x")

        tk.Label(
            v, text="Confirmar",
            bg=C["surface"], fg=C["text_dim"],
            font=FONT_MONO_SM
        ).pack(pady=(14, 4))

        tk.Label(
            v, text=descripcion,
            bg=C["surface"], fg=C["text"],
            font=FONT_SERIF,
            wraplength=400, justify="center"
        ).pack(padx=24, pady=8)

        tk.Frame(v, bg=C["border"], height=1).pack(fill="x", pady=8)

        bf = tk.Frame(v, bg=C["surface"])
        bf.pack()

        def ok():
            v.destroy()
            callback()

        def cancel():
            v.destroy()
            self._agregar_mensaje("Cancelado.", "sistema")
            self._set_status("Listo")
            self._fin()

        tk.Button(
            bf, text="Confirmar",
            bg=C["accent_dim"], fg=C["bg"],
            relief="flat", font=("Georgia", 11),
            cursor="hand2", padx=22, pady=6,
            activebackground=C["accent"],
            activeforeground=C["bg"],
            command=ok
        ).pack(side="left", padx=10)

        tk.Button(
            bf, text="Cancelar",
            bg=C["surface3"], fg=C["text_dim"],
            relief="flat", font=("Georgia", 11),
            cursor="hand2", padx=22, pady=6,
            activebackground=C["surface2"],
            activeforeground=C["text"],
            command=cancel
        ).pack(side="left", padx=10)

    # ─── NOTIFICACIONES ───────────────────────────────────────────────────────

    def _verificar_queue(self):
        try:
            while True:
                msg = mensaje_queue.get_nowait()
                self._notificacion(msg)
        except queue.Empty:
            pass
        self.after(1000, self._verificar_queue)

    def _notificacion(self, mensaje):
        self._agregar_mensaje(mensaje, "notificacion")
        v = tk.Toplevel(self)
        v.title("")
        v.geometry("360x130")
        v.resizable(False, False)
        v.configure(bg=C["surface"])
        v.attributes("-topmost", True)

        tk.Frame(v, bg=C["notif_left"], height=1).pack(fill="x")

        tk.Label(
            v, text="Recordatorio",
            bg=C["surface"], fg=C["notif_text"],
            font=FONT_MONO_SM
        ).pack(pady=(12, 4))

        tk.Label(
            v, text=mensaje,
            bg=C["surface"], fg=C["text"],
            font=FONT_SERIF, wraplength=320
        ).pack(pady=4)

        tk.Button(
            v, text="OK",
            bg=C["surface3"], fg=C["text"],
            relief="flat", font=("Georgia", 10),
            cursor="hand2", padx=18, pady=4,
            command=v.destroy
        ).pack(pady=8)

    def _iniciar_monitores(self):
        iniciar_monitor()
        iniciar_monitor_programadas()


# ─── PARCHE RECORDATORIOS ─────────────────────────────────────────────────────

def _parchear_recordatorios():
    import reminders as rem
    def nuevo_loop():
        import time
        while rem._monitor_activo:
            try:
                data = rem._cargar()
                ahora = datetime.now()
                hubo_cambio = False
                for r in data:
                    if r["disparado"]:
                        continue
                    cuando = datetime.fromisoformat(r["cuando"])
                    if ahora >= cuando:
                        r["disparado"] = True
                        hubo_cambio = True
                        mensaje_queue.put(r["mensaje"])
                        try:
                            import winsound
                            for _ in range(3):
                                winsound.Beep(1000, 400)
                                time.sleep(0.2)
                        except Exception:
                            pass
                if hubo_cambio:
                    rem._guardar(data)
            except Exception:
                pass
            time.sleep(30)
    rem._monitor_loop = nuevo_loop


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _parchear_recordatorios()
    app = AsistenteApp()
    app.mainloop()