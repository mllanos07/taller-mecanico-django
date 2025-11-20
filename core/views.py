from django.shortcuts import render, redirect
from django.contrib import messages

def inicio(request):
    """
    Página principal: hero, resumen de servicios, CTA
    """
    servicios = [
        {"titulo": "Cambio de aceite", "descripcion": "Cambio de aceite y filtro con marcas reconocidas."},
        {"titulo": "Frenos", "descripcion": "Revisión y reemplazo de pastillas, discos y calibración."},
        {"titulo": "Suspensión", "descripcion": "Reparación y ajuste de amortiguadores y resortes."},
        {"titulo": "Electricidad", "descripcion": "Diagnóstico y solución de fallas eléctricas."},
        {"titulo": "Alineación", "descripcion": "Alineación y balanceo para mayor vida útil de neumáticos."},
    ]
    return render(request, "inicio.html", {"servicios": servicios})

def acerca(request):
    """
    Página 'Quienes somos': misión, visión, historia y equipo
    """
    equipo = [
        {"nombre": "Mateo Ulla", "rol": "Jefe de taller"},
        {"nombre": "Matías Llanos", "rol": "Administración"},
        {"nombre": "Santino Macchiarola", "rol": "Técnico mecánico"},
        {"nombre": "Oriana Daer", "rol": "Secretaria"},
    ]
    contexto = {
        "mision": "Brindar soluciones automotrices confiables y accesibles.",
        "vision": "Ser el taller de referencia en la región por calidad y servicio.",
        "historia": "Fundado en 2010, crecemos gracias al boca a boca y trabajo serio.",
        "equipo": equipo,
    }
    return render(request, "acerca.html", contexto)

def servicios(request):
    """
    Página que lista todos los servicios (detalle)
    """
    lista_servicios = [
        {"titulo": "Mecánica general", "detalle": "Reparaciones de motor, caja, embrague y partes mecánicas."},
        {"titulo": "Repuestos", "detalle": "Suministro y montaje de repuestos originales y genéricos."},
        {"titulo": "Diagnóstico", "detalle": "Equipo de diagnóstico OBD-II para fallas complejas."},
        {"titulo": "Pre-ITV", "detalle": "Revisión previa para asegurar que el vehículo pase la verificación."},
        {"titulo": "Servicio rápido", "detalle": "Cambios de aceite y servicios en el día."},
    ]
    return render(request, "servicios.html", {"lista_servicios": lista_servicios})

def contacto(request):
    """
    Formulario de contacto — no persiste (por petición sin models), solo demo.
    """
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        mensaje = request.POST.get("mensaje")
        # Aquí normalmente guardaríamos o enviaríamos un email.
        # Para la entrega práctica, solo mostramos un mensaje de éxito.
        messages.success(request, f"Gracias {nombre}. Tu mensaje fue recibido.")
        return redirect("contacto")
    return render(request, "contacto.html")

def cotizacion(request):
    """
    Solicitud de presupuesto — interfaz solamente.
    """
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        vehiculo = request.POST.get("vehiculo")
        servicio_solicitado = request.POST.get("servicio")
        telefono = request.POST.get("telefono")
        messages.success(request, "Solicitud enviada. Nos comunicaremos a la brevedad.")
        return redirect("cotizacion")
    servicios_form = ["Cambio de aceite", "Frenos", "Alineación", "Diagnóstico", "Repuestos"]
    return render(request, "cotizacion.html", {"servicios": servicios_form})

import mysql.connector

def login_empleados(request):
    """
    Login real: valida credenciales contra MySQL y guarda tipo de usuario en sesión.
    """
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # Admin hardcodeado
        if username == "admin" and password == "admin123":
            request.session["user_type"] = "admin"
            request.session["username"] = "admin"
            return redirect("lista_empleados")
        # Empleado: buscar en la base de datos
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="root", database="taller_mecanico"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM empleado WHERE usuario=%s AND contrasena=%s", (username, password))
            empleado = cursor.fetchone()
            if empleado:
                request.session["user_type"] = "empleado"
                request.session["empleado_id"] = empleado["id"]
                request.session["username"] = username
                return redirect("lista_empleados")
            else:
                error = "Credenciales incorrectas"
        except Exception as ex:
            error = f"Error de conexión: {ex}"
    return render(request, "login.html", {"error": error})

def panel(request):
    """
    Panel especial para admin y empleados autenticados.
    """

    user_type = request.session.get("user_type")
    username = request.session.get("username")
    if not user_type:
        return redirect("login_empleados")
    return render(request, "panel.html", {"user_type": user_type, "username": username})

def logout(request):
    """
    Cierra la sesión y redirige al inicio.
    """
    request.session.flush()
    return redirect("inicio")

# --- CRUD EMPLEADOS ---
def lista_empleados(request):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor(dictionary=True)
    empleado = None
    # Si viene para modificar
    if request.method == "GET" and "modificar" in request.GET:
        legajo = request.GET.get("modificar")
        cursor.execute("SELECT emp.legajo, per.dni, per.nombre, per.apellido FROM empleado emp INNER JOIN persona per ON emp.dni = per.dni WHERE emp.legajo = %s", (legajo,))
        empleado = cursor.fetchone()
    # Si viene para alta o modificación
    if request.method == "POST":
        if "modificar" in request.POST: # Modificación
            legajo = request.POST.get("legajo")
            nombre = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            cursor2 = conn.cursor()
            cursor2.execute("UPDATE persona SET nombre=%s, apellido=%s WHERE dni=(SELECT dni FROM empleado WHERE legajo=%s)", (nombre, apellido, legajo))
            conn.commit()
            return redirect("lista_empleados")
        else: # Alta
            legajo = request.POST.get("legajo")
            dni = request.POST.get("dni")
            nombre = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            cursor2 = conn.cursor()
            cursor2.execute("INSERT INTO persona (dni, nombre, apellido) VALUES (%s, %s, %s)", (dni, nombre, apellido))
            cursor2.execute("INSERT INTO empleado (legajo, dni) VALUES (%s, %s)", (legajo, dni))
            conn.commit()
            return redirect("lista_empleados")
    cursor.execute("""
        SELECT emp.legajo, per.dni, per.nombre, per.apellido
        FROM empleado emp INNER JOIN persona per ON emp.dni = per.dni
        ORDER BY emp.legajo
    """)
    empleados = cursor.fetchall()
    return render(request, "empleados_lista.html", {"empleados": empleados, "empleado": empleado})

def alta_empleado(request):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    if request.method == "POST":
        legajo = request.POST.get("legajo")
        dni = request.POST.get("dni")
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO persona (dni, nombre, apellido) VALUES (%s, %s, %s)", (dni, nombre, apellido))
        cursor.execute("INSERT INTO empleado (legajo, dni) VALUES (%s, %s)", (legajo, dni))
        conn.commit()
        return redirect("lista_empleados")
    return render(request, "empleados_alta.html")

def modificar_empleado(request, legajo):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT emp.legajo, per.dni, per.nombre, per.apellido FROM empleado emp INNER JOIN persona per ON emp.dni = per.dni WHERE emp.legajo = %s", (legajo,))
    empleado = cursor.fetchone()
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        cursor2 = conn.cursor()
        cursor2.execute("UPDATE persona SET nombre=%s, apellido=%s WHERE dni=%s", (nombre, apellido, empleado["dni"]))
        conn.commit()
        return redirect("lista_empleados")
    return render(request, "empleados_modificar.html", {"empleado": empleado})

def eliminar_empleado(request, legajo):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT dni FROM empleado WHERE legajo = %s", (legajo,))
    empleado = cursor.fetchone()
    cursor2 = conn.cursor()
    cursor2.execute("DELETE FROM empleado WHERE legajo = %s", (legajo,))
    cursor2.execute("DELETE FROM persona WHERE dni = %s", (empleado["dni"],))
    conn.commit()
    return redirect("lista_empleados")

# --- CRUD FICHA TECNICA ---
def lista_fichas(request):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor(dictionary=True)
    ficha = None
    # Si viene para modificar
    if request.method == "GET" and "modificar" in request.GET:
        nro_ficha = request.GET.get("modificar")
        cursor.execute("SELECT * FROM ficha_tecnica WHERE nro_ficha = %s", (nro_ficha,))
        ficha = cursor.fetchone()
    # Si viene para alta
    if request.method == "POST":
        if "nro_ficha" in request.POST and not request.POST.get("modificar"): # Alta
            nro_ficha = request.POST.get("nro_ficha")
            cod_cliente = request.POST.get("cod_cliente")
            vehiculo = request.POST.get("vehiculo")
            subtotal = request.POST.get("subtotal")
            mano_obra = request.POST.get("mano_obra")
            total_general = request.POST.get("total_general")
            cursor2 = conn.cursor()
            cursor2.execute("INSERT INTO ficha_tecnica (nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general) VALUES (%s, %s, %s, %s, %s, %s)", (nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general))
            conn.commit()
            return redirect("lista_fichas")
        elif "modificar" in request.POST: # Modificación
            nro_ficha = request.POST.get("nro_ficha")
            cod_cliente = request.POST.get("cod_cliente")
            vehiculo = request.POST.get("vehiculo")
            subtotal = request.POST.get("subtotal")
            mano_obra = request.POST.get("mano_obra")
            total_general = request.POST.get("total_general")
            cursor2 = conn.cursor()
            cursor2.execute("UPDATE ficha_tecnica SET cod_cliente=%s, vehiculo=%s, subtotal=%s, mano_obra=%s, total_general=%s WHERE nro_ficha=%s", (cod_cliente, vehiculo, subtotal, mano_obra, total_general, nro_ficha))
            conn.commit()
            return redirect("lista_fichas")
    cursor.execute("SELECT * FROM ficha_tecnica ORDER BY nro_ficha")
    fichas = cursor.fetchall()
    return render(request, "fichas_lista.html", {"fichas": fichas, "ficha": ficha})

def alta_ficha(request):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    if request.method == "POST":
        nro_ficha = request.POST.get("nro_ficha")
        cod_cliente = request.POST.get("cod_cliente")
        vehiculo = request.POST.get("vehiculo")
        subtotal = request.POST.get("subtotal")
        mano_obra = request.POST.get("mano_obra")
        total_general = request.POST.get("total_general")
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ficha_tecnica (nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general) VALUES (%s, %s, %s, %s, %s, %s)", (nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general))
        conn.commit()
        return redirect("lista_fichas")
    return render(request, "fichas_alta.html")

def modificar_ficha(request, nro_ficha):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ficha_tecnica WHERE nro_ficha = %s", (nro_ficha,))
    ficha = cursor.fetchone()
    if request.method == "POST":
        cod_cliente = request.POST.get("cod_cliente")
        vehiculo = request.POST.get("vehiculo")
        subtotal = request.POST.get("subtotal")
        mano_obra = request.POST.get("mano_obra")
        total_general = request.POST.get("total_general")
        cursor2 = conn.cursor()
        cursor2.execute("UPDATE ficha_tecnica SET cod_cliente=%s, vehiculo=%s, subtotal=%s, mano_obra=%s, total_general=%s WHERE nro_ficha=%s", (cod_cliente, vehiculo, subtotal, mano_obra, total_general, nro_ficha))
        conn.commit()
        return redirect("lista_fichas")
    return render(request, "fichas_modificar.html", {"ficha": ficha})

def eliminar_ficha(request, nro_ficha):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ficha_tecnica WHERE nro_ficha = %s", (nro_ficha,))
    conn.commit()
    return redirect("lista_fichas")

# --- CRUD PRESUPUESTO ---
def lista_presupuestos(request):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        nro_presupuesto = request.POST.get("nro_presupuesto")
        cod_cliente = request.POST.get("cod_cliente")
        descripcion = request.POST.get("descripcion")
        total_presupuesto = request.POST.get("total_presupuesto")
        total_gastado = request.POST.get("total_gastado")
        cursor2 = conn.cursor()
        cursor2.execute("INSERT INTO presupuesto (nro_presupuesto, cod_cliente, descripcion, total_presupuesto, total_gastado) VALUES (%s, %s, %s, %s, %s)", (nro_presupuesto, cod_cliente, descripcion, total_presupuesto, total_gastado))
        conn.commit()
        return redirect("lista_presupuestos")
    cursor.execute("SELECT * FROM presupuesto ORDER BY nro_presupuesto")
    presupuestos = cursor.fetchall()
    return render(request, "presupuestos_lista.html", {"presupuestos": presupuestos})

def alta_presupuesto(request):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    if request.method == "POST":
        nro_presupuesto = request.POST.get("nro_presupuesto")
        cod_cliente = request.POST.get("cod_cliente")
        descripcion = request.POST.get("descripcion")
        total_presupuesto = request.POST.get("total_presupuesto")
        total_gastado = request.POST.get("total_gastado")
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO presupuesto (nro_presupuesto, cod_cliente, descripcion, total_presupuesto, total_gastado) VALUES (%s, %s, %s, %s, %s)", (nro_presupuesto, cod_cliente, descripcion, total_presupuesto, total_gastado))
        conn.commit()
        return redirect("lista_presupuestos")
    return render(request, "presupuestos_alta.html")

def modificar_presupuesto(request, nro_presupuesto):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM presupuesto WHERE nro_presupuesto = %s", (nro_presupuesto,))
    presupuesto = cursor.fetchone()
    if request.method == "POST":
        cod_cliente = request.POST.get("cod_cliente")
        descripcion = request.POST.get("descripcion")
        total_presupuesto = request.POST.get("total_presupuesto")
        total_gastado = request.POST.get("total_gastado")
        cursor2 = conn.cursor()
        cursor2.execute("UPDATE presupuesto SET cod_cliente=%s, descripcion=%s, total_presupuesto=%s, total_gastado=%s WHERE nro_presupuesto=%s", (cod_cliente, descripcion, total_presupuesto, total_gastado, nro_presupuesto))
        conn.commit()
        return redirect("lista_presupuestos")
    return render(request, "presupuestos_modificar.html", {"presupuesto": presupuesto})

def eliminar_presupuesto(request, nro_presupuesto):
    if request.session.get("user_type") != "admin":
        return redirect("login_empleados")
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="taller_mecanico")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM presupuesto WHERE nro_presupuesto = %s", (nro_presupuesto,))
    conn.commit()
    return redirect("lista_presupuestos")
   