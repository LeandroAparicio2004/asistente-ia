import tkinter as tk
from tkinter import filedialog, scrolledtext
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

# ─── PALETA NEOBRUTALIST ──────────────────────────────────────────────────────

C = {
    "bg":           "#0a0a0a",
    "surface":      "#111111",
    "surface2":     "#1a1a1a",
    "surface3":     "#222222",
    "border":       "#2a2a2a",
    "border2":      "#333333",
    "accent":       "#00ff88",
    "accent_dim":   "#00aa55",
    "accent_dark":  "#003322",
    "text":         "#e8e8e8",
    "text_dim":     "#666666",
    "text_dimmer":  "#333333",
    "user_bg":      "#0d1f2d",
    "user_border":  "#1a4a6e",
    "bot_bg":       "#111111",
    "bot_border":   "#2a2a2a",
    "error_bg":     "#1a0a0a",
    "error_text":   "#ff4444",
    "warn_text":    "#ffaa00",
    "sys_text":     "#444444",
    "select_bg":    "#003322",
}

FONT_MONO = ("Consolas", 12)
FONT_MONO_SM = ("Consolas", 10)
FONT_MONO_LG = ("Consolas", 14)
FONT_MONO_XL = ("Consolas", 16, "bold")

mensaje_queue = queue.Queue()

# ─── BURBUJA DE MENSAJE ───────────────────────────────────────────────────────

class BurbujaMensaje(tk.Frame):
    def __init__(self, parent, texto, rol, app_ref, **kwargs):
        super().__init__(parent, bg=C["bg"], **kwargs)
        self.app_ref = app_ref
        self.texto_completo = texto
        self.rol = rol
        self._build(texto, rol)

    def _build(self, texto, rol):
        es_usuario = rol == "usuario"
        es_error = rol == "error"
        es_sistema = rol == "sistema"
        es_notif = rol == "notificacion"

        if es_usuario:
            bg = C["user_bg"]
            border = C["user_border"]
            fg = C["text"]
            prefix = "▶"
            prefix_color = C["accent"]
            pad_left = 120
            pad_right = 12
        elif es_error:
            bg = C["error_bg"]
            border = C["error_text"]
            fg = C["error_text"]
            prefix = "✗"
            prefix_color = C["error_text"]
            pad_left = 12
            pad_right = 120
        elif es_sistema:
            bg = C["bg"]
            border = C["border"]
            fg = C["sys_text"]
            prefix = "—"
            prefix_color = C["text_dimmer"]
            pad_left = 60
            pad_right = 60
        elif es_notif:
            bg = C["accent_dark"]
            border = C["accent_dim"]
            fg = C["accent"]
            prefix = "◉"
            prefix_color = C["accent"]
            pad_left = 12
            pad_right = 120
        else:
            bg = C["bot_bg"]
            border = C["bot_border"]
            fg = C["text"]
            prefix = "◈"
            prefix_color = C["accent_dim"]
            pad_left = 12
            pad_right = 120

        outer = tk.Frame(self, bg=C["bg"])
        outer.pack(fill="x", padx=0, pady=1)

        # Contenedor con borde
        container = tk.Frame(outer, bg=border)
        container.pack(
            fill="none" if not es_sistema else "x",
            anchor="e" if es_usuario else ("center" if es_sistema else "w"),
            padx=(pad_left, pad_right),
            pady=2
        )

        inner = tk.Frame(container, bg=bg)
        inner.pack(padx=1, pady=1, fill="x")

        # Header — prefijo + timestamp + botones
        header = tk.Frame(inner, bg=bg)
        header.pack(fill="x", padx=8, pady=(6, 0))

        tk.Label(
            header, text=prefix,
            bg=bg, fg=prefix_color,
            font=FONT_MONO_SM
        ).pack(side="left")

        ts = datetime.now().strftime("%H:%M")
        tk.Label(
            header, text=f"  {ts}",
            bg=bg, fg=C["text_dimmer"],
            font=FONT_MONO_SM
        ).pack(side="left")

        # Botones acción (solo para mensajes de asistente y usuario)
        if not es_sistema:
            btn_frame = tk.Frame(header, bg=bg)
            btn_frame.pack(side="right")

            btn_cfg = dict(
                bg=bg, fg=C["text_dimmer"],
                relief="flat", font=FONT_MONO_SM,
                cursor="hand2", padx=4,
                activebackground=C["surface3"],
                activeforeground=C["accent"]
            )

            tk.Button(
                btn_frame, text="⊕",
                command=self._copiar, **btn_cfg
            ).pack(side="left", padx=2)

            tk.Button(
                btn_frame, text="▷",
                command=self._leer, **btn_cfg
            ).pack(side="left", padx=2)

        # Texto seleccionable
        txt = tk.Text(
            inner,
            bg=bg, fg=fg,
            font=FONT_MONO,
            relief="flat",
            wrap="word",
            cursor="arrow",
            state="normal",
            selectbackground=C["select_bg"],
            selectforeground=C["accent"],
            exportselection=True,
            height=1,
            padx=8, pady=4,
            spacing1=2, spacing3=2
        )
        txt.insert("1.0", texto)
        txt.configure(state="disabled")
        txt.pack(fill="x", padx=0, pady=(2, 6))

        # Ajustar altura automáticamente
        self.after(10, lambda: self._ajustar_altura(txt))

        self._txt_widget = txt

    def _ajustar_altura(self, txt):
        txt.configure(state="normal")
        lines = int(txt.index("end-1c").split(".")[0])
        txt.configure(height=max(1, lines), state="disabled")

    def _copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.texto_completo)
        self.app_ref._set_status("Copiado al portapapeles", C["accent"])

    def _leer(self):
        threading.Thread(
            target=lambda: hablar(self.texto_completo),
            daemon=True
        ).start()
        self.app_ref._set_status("Leyendo...", C["accent_dim"])


# ─── APP PRINCIPAL ────────────────────────────────────────────────────────────

class AsistenteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ASISTENTE IA")
        self.geometry("980x740")
        self.minsize(720, 520)
        self.configure(bg=C["bg"])

        self.imagen_adjunta = None
        self.procesando = False
        self.escuchando = False
        self._modelo_actual = "LLaMA 3.3"

        self._build_ui()
        self._iniciar_monitores()
        self._verificar_queue()
        self.after(300, self._bienvenida)

    # ─── BUILD ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_chat()
        self._build_img_bar()
        self._build_input()
        self._build_status()

    def _build_header(self):
        h = tk.Frame(self, bg=C["surface"], height=48)
        h.grid(row=0, column=0, sticky="ew")
        h.grid_propagate(False)
        h.grid_columnconfigure(1, weight=1)

        # Línea acento top
        tk.Frame(h, bg=C["accent"], height=2).place(x=0, y=0, relwidth=1)

        left = tk.Frame(h, bg=C["surface"])
        left.grid(row=0, column=0, padx=16, pady=8)

        tk.Label(
            left, text="◈",
            bg=C["surface"], fg=C["accent"],
            font=("Consolas", 18, "bold")
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            left, text="ASISTENTE",
            bg=C["surface"], fg=C["text"],
            font=("Consolas", 13, "bold")
        ).pack(side="left")

        tk.Label(
            left, text=" IA",
            bg=C["surface"], fg=C["accent"],
            font=("Consolas", 13, "bold")
        ).pack(side="left")

        self.lbl_modelo = tk.Label(
            h, text=f"● {self._modelo_actual}",
            bg=C["surface"], fg=C["accent"],
            font=FONT_MONO_SM
        )
        self.lbl_modelo.grid(row=0, column=1)

        right = tk.Frame(h, bg=C["surface"])
        right.grid(row=0, column=2, padx=16)

        tk.Label(
            right,
            text=f"⬡ {os.path.basename(SANDBOX_PATH)}",
            bg=C["surface"], fg=C["text_dim"],
            font=FONT_MONO_SM
        ).pack(side="left", padx=(0, 16))

    def _build_chat(self):
        wrapper = tk.Frame(self, bg=C["bg"])
        wrapper.grid(row=1, column=0, sticky="nsew")
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            wrapper, bg=C["bg"],
            highlightthickness=0, bd=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        sb = tk.Scrollbar(wrapper, orient="vertical", command=self.canvas.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=sb.set)

        self.chat_frame = tk.Frame(self.canvas, bg=C["bg"])
        self._win = self.canvas.create_window(
            (0, 0), window=self.chat_frame, anchor="nw"
        )

        self.chat_frame.bind("<Configure>", self._on_cfg)
        self.canvas.bind("<Configure>", self._on_canvas_cfg)
        self.bind_all("<MouseWheel>", self._on_scroll)

    def _build_img_bar(self):
        self.img_bar = tk.Frame(self, bg="#0a1a0a", height=28)
        self.lbl_img = tk.Label(
            self.img_bar, text="",
            bg="#0a1a0a", fg=C["accent"],
            font=FONT_MONO_SM
        )
        self.lbl_img.pack(side="left", padx=10)
        tk.Button(
            self.img_bar, text="✕",
            bg="#0a1a0a", fg=C["text_dim"],
            relief="flat", font=FONT_MONO_SM,
            cursor="hand2",
            activebackground="#0a1a0a",
            activeforeground=C["accent"],
            command=self._quitar_imagen
        ).pack(side="right", padx=6)

    def _build_input(self):
        tk.Frame(self, bg=C["accent"], height=1).grid(
            row=3, column=0, sticky="ew"
        )

        inp = tk.Frame(self, bg=C["surface"], height=80)
        inp.grid(row=4, column=0, sticky="ew")
        inp.grid_propagate(False)
        inp.grid_columnconfigure(1, weight=1)

        btn_cfg = dict(
            bg=C["surface2"], fg=C["text_dim"],
            relief="flat", font=("Consolas", 15),
            cursor="hand2", width=3,
            activebackground=C["surface3"],
            activeforeground=C["accent"]
        )

        # Botón imagen
        self.btn_img = tk.Button(
            inp, text="⊞", **btn_cfg,
            command=self._adjuntar_imagen
        )
        self.btn_img.grid(row=0, column=0, padx=(12, 6), pady=16)

        # Text widget multilínea con Shift+Enter
        entry_container = tk.Frame(inp, bg=C["border"], bd=0)
        entry_container.grid(row=0, column=1, padx=6, pady=16, sticky="ew")

        self.entrada = tk.Text(
            entry_container,
            bg=C["surface2"], fg=C["text"],
            insertbackground=C["accent"],
            relief="flat", font=FONT_MONO,
            height=2, wrap="word",
            padx=10, pady=8,
            selectbackground=C["select_bg"],
            selectforeground=C["accent"]
        )
        self.entrada.pack(padx=1, pady=1, fill="both")

        # Enter envía, Shift+Enter hace salto de línea
        self.entrada.bind("<Return>", self._on_enter)
        self.entrada.bind("<Shift-Return>", self._on_shift_enter)

        # Placeholder
        self._placeholder_activo = True
        self._placeholder_text = "Escribí tu mensaje... (Shift+Enter para salto de línea)"
        self.entrada.insert("1.0", self._placeholder_text)
        self.entrada.configure(fg=C["text_dim"])
        self.entrada.bind("<FocusIn>", self._on_focus_in)
        self.entrada.bind("<FocusOut>", self._on_focus_out)

        # Botón voz
        self.btn_voz = tk.Button(
            inp, text="⊙", **btn_cfg,
            command=self._toggle_voz
        )
        self.btn_voz.grid(row=0, column=2, padx=6, pady=16)

        # Botón enviar
        self.btn_enviar = tk.Button(
            inp, text="⊳",
            bg=C["accent_dark"], fg=C["accent"],
            relief="flat", font=("Consolas", 17, "bold"),
            cursor="hand2", width=3,
            activebackground=C["accent"],
            activeforeground=C["bg"],
            command=self._enviar
        )
        self.btn_enviar.grid(row=0, column=3, padx=(6, 12), pady=16)

    def _build_status(self):
        self.status = tk.Label(
            self, text="◎  Sistema listo",
            bg=C["bg"], fg=C["text_dimmer"],
            font=FONT_MONO_SM, anchor="w"
        )
        self.status.grid(row=5, column=0, sticky="ew", padx=14, pady=(2, 4))

    # ─── PLACEHOLDER ──────────────────────────────────────────────────────────

    def _on_focus_in(self, e):
        if self._placeholder_activo:
            self.entrada.delete("1.0", "end")
            self.entrada.configure(fg=C["text"])
            self._placeholder_activo = False

    def _on_focus_out(self, e):
        if not self.entrada.get("1.0", "end").strip():
            self.entrada.insert("1.0", self._placeholder_text)
            self.entrada.configure(fg=C["text_dim"])
            self._placeholder_activo = True

    # ─── ENTER / SHIFT+ENTER ──────────────────────────────────────────────────

    def _on_enter(self, event):
        self._enviar()
        return "break"

    def _on_shift_enter(self, event):
        return None  # Comportamiento por defecto — inserta newline

    # ─── CHAT ─────────────────────────────────────────────────────────────────

    def _agregar_mensaje(self, texto: str, rol: str):
        burbuja = BurbujaMensaje(
            self.chat_frame, texto, rol, self
        )
        burbuja.pack(fill="x", padx=0, pady=0)
        self.after(80, self._scroll_bottom)

    def _scroll_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _on_cfg(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_cfg(self, e):
        self.canvas.itemconfig(self._win, width=e.width)

    def _on_scroll(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _bienvenida(self):
        self._agregar_mensaje(
            "Sistema iniciado. Escribe, habla o adjunta una imagen.\n"
            "Shift+Enter para salto de línea. ⊕ para copiar. ▷ para escuchar.",
            "asistente"
        )

    def _set_status(self, texto, color=None):
        self.status.configure(
            text=f"◎  {texto}",
            fg=color or C["text_dimmer"]
        )

    def _set_modelo(self, nombre):
        self._modelo_actual = nombre
        self.lbl_modelo.configure(text=f"● {nombre}")

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
        self.lbl_img.configure(text=f"⊞  {nombre}")
        self.img_bar.grid(row=2, column=0, sticky="ew")
        self._set_status(f"Imagen: {nombre}", C["accent"])

    def _quitar_imagen(self):
        self.imagen_adjunta = None
        self.img_bar.grid_remove()
        self._set_status("Sistema listo")

    # ─── VOZ ──────────────────────────────────────────────────────────────────

    def _toggle_voz(self):
        if self.procesando or self.escuchando:
            return
        self.escuchando = True
        self.btn_voz.configure(fg=C["error_text"], text="⊗")
        self._set_status("Escuchando...", C["error_text"])
        threading.Thread(target=self._escuchar_voz, daemon=True).start()

    def _escuchar_voz(self):
        texto = escuchar()
        self.escuchando = False
        self.after(0, lambda: self.btn_voz.configure(fg=C["text_dim"], text="⊙"))
        if texto:
            self.after(0, lambda: self._set_entrada(texto))
            self.after(100, self._enviar)
        else:
            self.after(0, lambda: self._set_status("No se escuchó nada", C["warn_text"]))

    def _set_entrada(self, texto):
        if self._placeholder_activo:
            self.entrada.delete("1.0", "end")
            self.entrada.configure(fg=C["text"])
            self._placeholder_activo = False
        else:
            self.entrada.delete("1.0", "end")
        self.entrada.insert("1.0", texto)

    # ─── ENVIAR ───────────────────────────────────────────────────────────────

    def _enviar(self):
        if self.procesando:
            return
        if self._placeholder_activo:
            return

        texto = self.entrada.get("1.0", "end").strip()
        if not texto:
            return

        self.entrada.delete("1.0", "end")
        self._on_focus_out(None)

        if self.imagen_adjunta:
            msg = f"{texto} [imagen: {self.imagen_adjunta}]"
            self._agregar_mensaje(f"{texto}  ⊞ {self.imagen_adjunta}", "usuario")
            self._quitar_imagen()
        else:
            msg = texto
            self._agregar_mensaje(texto, "usuario")

        self.procesando = True
        self.btn_enviar.configure(state="disabled", fg=C["text_dim"])
        self._set_status("Procesando...", C["accent_dim"])

        threading.Thread(target=self._procesar, args=(msg,), daemon=True).start()

    # ─── PROCESAR ─────────────────────────────────────────────────────────────

    def _procesar(self, mensaje):
        try:
            resultado = interpretar(mensaje)
            accion = resultado.get("accion")
            parametros = resultado.get("parametros", {})
            descripcion = resultado.get("descripcion", "")

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
                self.after(0, lambda: self._set_status("Error", C["error_text"]))
                self.after(0, self._fin)

            elif accion == "ver_historial":
                h = ver_historial()
                self.after(0, lambda: self._agregar_mensaje(h, "asistente"))
                self.after(0, lambda: self._set_status("Listo"))
                self.after(0, self._fin)

            elif accion == "limpiar_memoria":
                self.after(0, lambda: self._confirmar(
                    "¿Limpiar toda la memoria?",
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
                self._set_status("Ejecutando...", C["accent"])
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
        self.btn_enviar.configure(state="normal", fg=C["accent"])

    # ─── CONFIRMACIÓN ─────────────────────────────────────────────────────────

    def _confirmar(self, descripcion, callback):
        v = tk.Toplevel(self)
        v.title("")
        v.geometry("480x190")
        v.resizable(False, False)
        v.configure(bg=C["surface"])
        v.grab_set()
        v.lift()

        tk.Frame(v, bg=C["accent"], height=2).pack(fill="x")

        tk.Label(
            v, text="CONFIRMAR ACCIÓN",
            bg=C["surface"], fg=C["accent"],
            font=("Consolas", 10, "bold")
        ).pack(pady=(14, 6))

        tk.Label(
            v, text=descripcion,
            bg=C["surface"], fg=C["text"],
            font=FONT_MONO,
            wraplength=420, justify="center"
        ).pack(padx=24, pady=6)

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
            bf, text="[ CONFIRMAR ]",
            bg=C["accent_dark"], fg=C["accent"],
            relief="flat", font=("Consolas", 11, "bold"),
            cursor="hand2", padx=20, pady=6,
            activebackground=C["accent"],
            activeforeground=C["bg"],
            command=ok
        ).pack(side="left", padx=10)

        tk.Button(
            bf, text="[ CANCELAR ]",
            bg=C["surface3"], fg=C["text_dim"],
            relief="flat", font=("Consolas", 11),
            cursor="hand2", padx=20, pady=6,
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
        self._agregar_mensaje(f"Recordatorio: {mensaje}", "notificacion")
        v = tk.Toplevel(self)
        v.title("")
        v.geometry("380x130")
        v.resizable(False, False)
        v.configure(bg=C["surface"])
        v.attributes("-topmost", True)
        v.lift()

        tk.Frame(v, bg=C["accent"], height=2).pack(fill="x")

        tk.Label(
            v, text="◉  RECORDATORIO",
            bg=C["surface"], fg=C["accent"],
            font=("Consolas", 11, "bold")
        ).pack(pady=(12, 4))

        tk.Label(
            v, text=mensaje,
            bg=C["surface"], fg=C["text"],
            font=FONT_MONO, wraplength=340
        ).pack(pady=4)

        tk.Button(
            v, text="[ OK ]",
            bg=C["accent_dark"], fg=C["accent"],
            relief="flat", font=("Consolas", 10, "bold"),
            cursor="hand2", padx=16, pady=4,
            command=v.destroy
        ).pack(pady=8)

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