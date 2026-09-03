import customtkinter as ctk
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

# ─── PALETA ───────────────────────────────────────────────────────────────────

COLORS = {
    "bg":           "#0f0f0f",
    "surface":      "#161616",
    "surface2":     "#1e1e1e",
    "surface3":     "#252525",
    "border":       "#2a2a2a",
    "accent":       "#e8d5b0",
    "accent2":      "#c4a882",
    "accent_dim":   "#8a7a62",
    "text":         "#f0ece4",
    "text_dim":     "#8a8680",
    "text_dimmer":  "#4a4744",
    "user_bubble":  "#1c2333",
    "user_accent":  "#3d5a8a",
    "bot_bubble":   "#1a1a1a",
    "error":        "#3d1515",
    "error_text":   "#e07070",
    "success":      "#70c090",
    "warning":      "#e0a050",
    "notify":       "#2a2010",
}

mensaje_queue = queue.Queue()

# ─── APP ──────────────────────────────────────────────────────────────────────

class AsistenteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Asistente IA")
        self.geometry("960x720")
        self.minsize(720, 520)
        self.configure(fg_color=COLORS["bg"])

        ctk.set_appearance_mode("dark")

        self.imagen_adjunta = None
        self.procesando = False
        self.escuchando = False
        self._modelo_actual = "LLaMA 3.3"

        self._build_ui()
        self._iniciar_monitores()
        self._verificar_queue()

        self.after(400, self._bienvenida)

    # ─── BUILD UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_chat()
        self._build_input()
        self._build_statusbar()

    def _build_header(self):
        h = tk.Frame(self, bg=COLORS["surface"], height=52)
        h.grid(row=0, column=0, sticky="ew")
        h.grid_propagate(False)
        h.grid_columnconfigure(1, weight=1)

        # Línea decorativa
        tk.Frame(h, bg=COLORS["accent"], height=1).place(x=0, rely=0, relwidth=1)

        # Logo + nombre
        logo_frame = tk.Frame(h, bg=COLORS["surface"])
        logo_frame.grid(row=0, column=0, padx=(18, 0), pady=8)

        tk.Label(
            logo_frame, text="◈", bg=COLORS["surface"],
            fg=COLORS["accent"], font=("Georgia", 18)
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            logo_frame, text="ASISTENTE IA",
            bg=COLORS["surface"], fg=COLORS["text"],
            font=("Georgia", 13, "bold")
        ).pack(side="left")

        # Modelo
        self.lbl_modelo = tk.Label(
            h, text=f"◉  {self._modelo_actual}",
            bg=COLORS["surface"], fg=COLORS["success"],
            font=("Consolas", 10)
        )
        self.lbl_modelo.grid(row=0, column=1, padx=10)

        # Sandbox
        tk.Label(
            h, text=f"⬡  {os.path.basename(SANDBOX_PATH)}",
            bg=COLORS["surface"], fg=COLORS["text_dim"],
            font=("Consolas", 10)
        ).grid(row=0, column=2, padx=(0, 18))

    def _build_chat(self):
        # Contenedor del chat con scroll
        outer = tk.Frame(self, bg=COLORS["bg"])
        outer.grid(row=1, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            outer, bg=COLORS["bg"],
            highlightthickness=0, bd=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.chat_inner = tk.Frame(self.canvas, bg=COLORS["bg"])
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.chat_inner, anchor="nw"
        )

        self.chat_inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Imagen adjunta indicator (oculto por defecto)
        self.img_bar = tk.Frame(self, bg="#1a1610", height=32)
        self.lbl_img_adjunta = tk.Label(
            self.img_bar, text="", bg="#1a1610",
            fg=COLORS["accent"], font=("Consolas", 10)
        )
        self.lbl_img_adjunta.pack(side="left", padx=12)
        tk.Button(
            self.img_bar, text="✕", bg="#1a1610", fg=COLORS["text_dim"],
            relief="flat", font=("Consolas", 10), cursor="hand2",
            activebackground="#1a1610", activeforeground=COLORS["accent"],
            command=self._quitar_imagen
        ).pack(side="right", padx=8)

    def _build_input(self):
        # Separador
        tk.Frame(self, bg=COLORS["border"], height=1).grid(
            row=3, column=0, sticky="ew"
        )

        inp = tk.Frame(self, bg=COLORS["surface"], height=68)
        inp.grid(row=4, column=0, sticky="ew")
        inp.grid_propagate(False)
        inp.grid_columnconfigure(1, weight=1)

        btn_cfg = dict(
            bg=COLORS["surface2"], fg=COLORS["text_dim"],
            relief="flat", font=("Consolas", 14), cursor="hand2",
            activebackground=COLORS["surface3"],
            activeforeground=COLORS["accent"],
            width=3, height=1
        )

        # Botón imagen
        self.btn_img = tk.Button(inp, text="⊞", **btn_cfg, command=self._adjuntar_imagen)
        self.btn_img.grid(row=0, column=0, padx=(12, 6), pady=14)

        # Entry
        entry_frame = tk.Frame(inp, bg=COLORS["surface3"], bd=0)
        entry_frame.grid(row=0, column=1, padx=6, pady=14, sticky="ew")

        self.entrada = tk.Entry(
            entry_frame,
            bg=COLORS["surface3"], fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat", font=("Georgia", 13),
            disabledbackground=COLORS["surface3"]
        )
        self.entrada.pack(padx=12, pady=8, fill="x")
        self.entrada.bind("<Return>", lambda e: self._enviar())

        # Botón voz
        self.btn_voz = tk.Button(inp, text="⊙", **btn_cfg, command=self._toggle_voz)
        self.btn_voz.grid(row=0, column=2, padx=6, pady=14)

        # Botón enviar
        self.btn_enviar = tk.Button(
            inp, text="⊳",
            bg=COLORS["accent_dim"], fg=COLORS["bg"],
            relief="flat", font=("Georgia", 16, "bold"),
            cursor="hand2", width=3, height=1,
            activebackground=COLORS["accent"],
            activeforeground=COLORS["bg"],
            command=self._enviar
        )
        self.btn_enviar.grid(row=0, column=3, padx=(6, 12), pady=14)

    def _build_statusbar(self):
        self.status_bar = tk.Label(
            self, text="◎  Listo",
            bg=COLORS["bg"], fg=COLORS["text_dimmer"],
            font=("Consolas", 9), anchor="w"
        )
        self.status_bar.grid(row=5, column=0, sticky="ew", padx=14, pady=(2, 4))

    # ─── CHAT MENSAJES ────────────────────────────────────────────────────────

    def _agregar_mensaje(self, texto: str, rol: str):
        es_usuario = rol == "usuario"
        es_error = rol == "error"
        es_sistema = rol == "sistema"
        es_notif = rol == "notificacion"

        outer = tk.Frame(self.chat_inner, bg=COLORS["bg"])
        outer.pack(fill="x", padx=0, pady=2)

        if es_usuario:
            bg_burbuja = COLORS["user_bubble"]
            fg_texto = COLORS["text"]
            padx_left = 120
            padx_right = 16
            prefix = ""
            anchor = "e"
            border_color = COLORS["user_accent"]
        elif es_error:
            bg_burbuja = COLORS["error"]
            fg_texto = COLORS["error_text"]
            padx_left = 16
            padx_right = 120
            prefix = "◈ "
            anchor = "w"
            border_color = COLORS["error_text"]
        elif es_sistema:
            bg_burbuja = COLORS["surface"]
            fg_texto = COLORS["text_dimmer"]
            padx_left = 60
            padx_right = 60
            prefix = "— "
            anchor = "center"
            border_color = COLORS["border"]
        elif es_notif:
            bg_burbuja = COLORS["notify"]
            fg_texto = COLORS["warning"]
            padx_left = 16
            padx_right = 120
            prefix = "◉ "
            anchor = "w"
            border_color = COLORS["warning"]
        else:
            bg_burbuja = COLORS["bot_bubble"]
            fg_texto = COLORS["text"]
            padx_left = 16
            padx_right = 120
            prefix = ""
            anchor = "w"
            border_color = COLORS["border"]

        # Contenedor con borde izquierdo decorativo
        row_frame = tk.Frame(outer, bg=COLORS["bg"])
        row_frame.pack(
            fill="x" if es_sistema else "none",
            anchor=anchor,
            padx=(padx_left, padx_right),
            pady=3
        )

        # Línea decorativa izquierda
        if not es_sistema:
            tk.Frame(row_frame, bg=border_color, width=2).pack(side="left", fill="y")

        # Prefijo / avatar
        if not es_sistema:
            if es_usuario:
                avatar = "  ↳ "
            else:
                avatar = "  ◈ "
            tk.Label(
                row_frame, text=avatar,
                bg=bg_burbuja, fg=border_color,
                font=("Georgia", 11)
            ).pack(side="left")

        # Texto principal
        txt_frame = tk.Frame(row_frame, bg=bg_burbuja)
        txt_frame.pack(side="left", fill="x", expand=True)

        # Timestamp
        ts = datetime.now().strftime("%H:%M")
        tk.Label(
            txt_frame,
            text=ts,
            bg=bg_burbuja,
            fg=COLORS["text_dimmer"],
            font=("Consolas", 8),
            anchor="w"
        ).pack(padx=(10, 10), pady=(6, 0), anchor="w")

        # Mensaje
        tk.Label(
            txt_frame,
            text=prefix + texto,
            bg=bg_burbuja,
            fg=fg_texto,
            font=("Georgia", 12),
            wraplength=580,
            justify="left",
            anchor="w"
        ).pack(padx=(10, 14), pady=(2, 8), anchor="w")

        # Scroll al final
        self.after(50, self._scroll_bottom)

    def _scroll_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bienvenida(self):
        self._agregar_mensaje(
            "Hola. Estoy listo para ayudarte.\nPodés escribir, hablar o adjuntar una imagen.",
            "asistente"
        )

    def _set_status(self, texto: str, color: str = None):
        self.status_bar.configure(
            text=f"◎  {texto}",
            fg=color or COLORS["text_dimmer"]
        )

    def _set_modelo(self, nombre: str):
        self._modelo_actual = nombre
        self.lbl_modelo.configure(text=f"◉  {nombre}")

    # ─── IMAGEN ───────────────────────────────────────────────────────────────

    def _adjuntar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")]
        )
        if not ruta:
            return
        nombre = os.path.basename(ruta)
        destino = os.path.join(SANDBOX_PATH, nombre)
        shutil.copy2(ruta, destino)
        self.imagen_adjunta = nombre
        self.lbl_img_adjunta.configure(text=f"⊞  {nombre}")
        self.img_bar.grid(row=2, column=0, sticky="ew")
        self._set_status(f"Imagen adjunta: {nombre}", COLORS["accent"])

    def _quitar_imagen(self):
        self.imagen_adjunta = None
        self.img_bar.grid_remove()
        self._set_status("Listo")

    # ─── VOZ ──────────────────────────────────────────────────────────────────

    def _toggle_voz(self):
        if self.procesando:
            return
        if not self.escuchando:
            self.escuchando = True
            self.btn_voz.configure(
                fg=COLORS["error_text"],
                text="⊗"
            )
            self._set_status("Escuchando...", COLORS["error_text"])
            threading.Thread(target=self._escuchar_voz, daemon=True).start()

    def _escuchar_voz(self):
        texto = escuchar()
        self.escuchando = False
        self.after(0, lambda: self.btn_voz.configure(
            fg=COLORS["text_dim"], text="⊙"
        ))
        if texto:
            self.after(0, lambda: self.entrada.delete(0, "end"))
            self.after(0, lambda: self.entrada.insert(0, texto))
            self.after(100, self._enviar)
        else:
            self.after(0, lambda: self._set_status("No se escuchó nada", COLORS["warning"]))

    # ─── ENVIAR ───────────────────────────────────────────────────────────────

    def _enviar(self):
        if self.procesando:
            return
        texto = self.entrada.get().strip()
        if not texto:
            return

        self.entrada.delete(0, "end")

        if self.imagen_adjunta:
            msg_completo = f"{texto} [imagen: {self.imagen_adjunta}]"
            self._agregar_mensaje(f"{texto}  ⊞ {self.imagen_adjunta}", "usuario")
            self._quitar_imagen()
        else:
            msg_completo = texto
            self._agregar_mensaje(texto, "usuario")

        self.procesando = True
        self.btn_enviar.configure(state="disabled", bg=COLORS["surface3"])
        self._set_status("Pensando...", COLORS["accent_dim"])

        threading.Thread(
            target=self._procesar, args=(msg_completo,), daemon=True
        ).start()

    def _procesar(self, mensaje: str):
        try:
            resultado = interpretar(mensaje)
            accion = resultado.get("accion")
            parametros = resultado.get("parametros", {})
            descripcion = resultado.get("descripcion", "")

            # Actualizar modelo en header
            from agent import _modelo_actual
            if _modelo_actual:
                self.after(0, lambda: self._set_modelo(_modelo_actual))

            if accion == "ninguna":
                self.after(0, lambda: self._agregar_mensaje(descripcion, "asistente"))
                self.after(0, lambda: self._set_status("Listo"))
                threading.Thread(target=lambda: hablar(descripcion), daemon=True).start()
                self.after(0, self._fin)

            elif accion == "error":
                self.after(0, lambda: self._agregar_mensaje(descripcion, "error"))
                self.after(0, lambda: self._set_status("Error", COLORS["error_text"]))
                self.after(0, self._fin)

            elif accion == "ver_historial":
                h = ver_historial()
                self.after(0, lambda: self._agregar_mensaje(h, "asistente"))
                self.after(0, lambda: self._set_status("Listo"))
                self.after(0, self._fin)

            elif accion == "limpiar_memoria":
                self.after(0, lambda: self._confirmar(
                    "¿Limpiar toda la memoria del asistente?",
                    lambda: self._exec("limpiar_memoria", {}, "Limpiar memoria")
                ))

            else:
                accion_real = ACCIONES_ALIAS.get(accion, accion)
                if accion_real not in ACCIONES:
                    self.after(0, lambda: self._agregar_mensaje(
                        f"No conozco esa acción: {accion}", "error"
                    ))
                    self.after(0, lambda: self._set_status("Listo"))
                    self.after(0, self._fin)
                else:
                    self.after(0, lambda: self._confirmar(
                        descripcion,
                        lambda: self._exec(accion_real, parametros, descripcion)
                    ))

        except Exception as e:
            self.after(0, lambda: self._agregar_mensaje(f"Error inesperado: {str(e)}", "error"))
            self.after(0, lambda: self._set_status("Error", COLORS["error_text"]))
            self.after(0, self._fin)

    def _exec(self, accion: str, parametros: dict, descripcion: str):
        def _run():
            try:
                self.after(0, lambda: self._set_status("Ejecutando...", COLORS["accent"]))
                funcion = ACCIONES[accion]
                res = funcion(**parametros)
                registrar(accion, parametros, res)
                self.after(0, lambda: self._agregar_mensaje(res, "asistente"))
                self.after(0, lambda: self._set_status("Listo"))
                threading.Thread(target=lambda: hablar(res), daemon=True).start()
            except Exception as e:
                err = f"Error al ejecutar: {str(e)}"
                self.after(0, lambda: self._agregar_mensaje(err, "error"))
                self.after(0, lambda: self._set_status("Error", COLORS["error_text"]))
            finally:
                self.after(0, self._fin)

        threading.Thread(target=_run, daemon=True).start()

    def _fin(self):
        self.procesando = False
        self.btn_enviar.configure(state="normal", bg=COLORS["accent_dim"])

    # ─── CONFIRMACIÓN ─────────────────────────────────────────────────────────

    def _confirmar(self, descripcion: str, callback):
        v = tk.Toplevel(self)
        v.title("")
        v.geometry("460x200")
        v.resizable(False, False)
        v.configure(bg=COLORS["surface"])
        v.grab_set()
        v.lift()

        # Borde superior decorativo
        tk.Frame(v, bg=COLORS["accent"], height=1).pack(fill="x")

        tk.Label(
            v, text="Confirmar acción",
            bg=COLORS["surface"], fg=COLORS["text_dim"],
            font=("Consolas", 10)
        ).pack(pady=(16, 4))

        tk.Label(
            v, text=descripcion,
            bg=COLORS["surface"], fg=COLORS["text"],
            font=("Georgia", 12),
            wraplength=400, justify="center"
        ).pack(padx=24, pady=8)

        tk.Frame(v, bg=COLORS["border"], height=1).pack(fill="x", pady=8)

        btn_frame = tk.Frame(v, bg=COLORS["surface"])
        btn_frame.pack()

        def ok():
            v.destroy()
            callback()

        def cancel():
            v.destroy()
            self._agregar_mensaje("Acción cancelada.", "sistema")
            self._set_status("Listo")
            self._fin()

        tk.Button(
            btn_frame, text="Confirmar",
            bg=COLORS["accent_dim"], fg=COLORS["bg"],
            relief="flat", font=("Georgia", 11),
            cursor="hand2", padx=24, pady=6,
            activebackground=COLORS["accent"],
            activeforeground=COLORS["bg"],
            command=ok
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame, text="Cancelar",
            bg=COLORS["surface3"], fg=COLORS["text_dim"],
            relief="flat", font=("Georgia", 11),
            cursor="hand2", padx=24, pady=6,
            activebackground=COLORS["surface2"],
            activeforeground=COLORS["text"],
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

    def _notificacion(self, mensaje: str):
        self._agregar_mensaje(f"Recordatorio: {mensaje}", "notificacion")

        v = tk.Toplevel(self)
        v.title("Recordatorio")
        v.geometry("360x140")
        v.resizable(False, False)
        v.configure(bg=COLORS["surface"])
        v.attributes("-topmost", True)
        v.lift()

        tk.Frame(v, bg=COLORS["warning"], height=1).pack(fill="x")

        tk.Label(
            v, text="◉  Recordatorio",
            bg=COLORS["surface"], fg=COLORS["warning"],
            font=("Consolas", 11)
        ).pack(pady=(14, 6))

        tk.Label(
            v, text=mensaje,
            bg=COLORS["surface"], fg=COLORS["text"],
            font=("Georgia", 12), wraplength=320
        ).pack(pady=6)

        tk.Button(
            v, text="OK",
            bg=COLORS["surface3"], fg=COLORS["text"],
            relief="flat", font=("Georgia", 11),
            cursor="hand2", padx=20, pady=4,
            command=v.destroy
        ).pack(pady=10)

    # ─── MONITORES ────────────────────────────────────────────────────────────

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