from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("acerca/", views.acerca, name="acerca"),
    path("servicios/", views.servicios, name="servicios"),
    path("contacto/", views.contacto, name="contacto"),
    path("cotizacion/", views.cotizacion, name="cotizacion"),
    path("login/", views.login_empleados, name="login_empleados"),
    path("logout/", views.logout, name="logout"),
    # CRUD Empleados
    path("empleados/", views.lista_empleados, name="lista_empleados"),
    path("empleados/alta/", views.alta_empleado, name="alta_empleado"),
    path("empleados/modificar/<int:legajo>/", views.modificar_empleado, name="modificar_empleado"),
    path("empleados/eliminar/<int:legajo>/", views.eliminar_empleado, name="eliminar_empleado"),
    # CRUD Ficha Técnica
    path("fichas/", views.lista_fichas, name="lista_fichas"),
    path("fichas/alta/", views.alta_ficha, name="alta_ficha"),
    path("fichas/modificar/<int:nro_ficha>/", views.modificar_ficha, name="modificar_ficha"),
    path("fichas/eliminar/<int:nro_ficha>/", views.eliminar_ficha, name="eliminar_ficha"),
    # CRUD Presupuesto
    path("presupuestos/", views.lista_presupuestos, name="lista_presupuestos"),
    path("presupuestos/alta/", views.alta_presupuesto, name="alta_presupuesto"),
    path("presupuestos/modificar/<int:nro_presupuesto>/", views.modificar_presupuesto, name="modificar_presupuesto"),
    path("presupuestos/eliminar/<int:nro_presupuesto>/", views.eliminar_presupuesto, name="eliminar_presupuesto"),
]
