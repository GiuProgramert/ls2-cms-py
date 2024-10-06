from enum import Enum


class PermissionEnum(str, Enum):
    """
    Enumeración que define una lista de permisos específicos utilizados en el sistema.

    Cada permiso está asociado a una cadena única que representa una acción o un conjunto de acciones
    que un usuario puede realizar.

    Permisos:
        - VER_INICIO: Permite ver la página de inicio.
        - VER_CATEGORIAS_SUSCRIPTOR: Permite ver categorías accesibles solo para suscriptores.
        - VER_CATEGORIAS_PAGO: Permite ver categorías que requieren un pago.
        - CREAR_ARTICULOS: Permite crear nuevos artículos.
        - EDITAR_ARTICULOS: Permite editar artículos existentes.
        - MODERAR_ARTICULOS: Permite moderar artículos (aprobación, rechazo, etc.).
        - PUBLICAR_COMENTARIOS: Permite publicar comentarios en artículos.
        - LEER_COMENTARIOS: Permite leer comentarios en artículos.
        - EVALUAR_ARTICULOS: Permite calificar artículos (ej. dar me gusta).
        - MANEJO_ROLES: Permite gestionar roles de usuario.
        - MANEJAR_CATEGORIAS: Permite manejar categorías de artículos.
    """

    VER_INICIO = "ver_inicio"
    VER_CATEGORIAS_SUSCRIPTOR = "ver_categorias_suscriptor"
    VER_CATEGORIAS_PAGO = "ver_categorias_pago" # se utiliza para ver todo lo comprado por cms, permiso del financiero
    CREAR_ARTICULOS = "crear_articulos"
    EDITAR_ARTICULOS = "editar_articulos"  # editar articulos en edicion
    EDITAR_ARTICULOS_BORRADOR = "editar_articulos_borrador"
    MODERAR_ARTICULOS = "moderar_articulos"  # permiso para publicar
    PUBLICAR_COMENTARIOS = "publicar_comentarios"
    LEER_COMENTARIOS = "leer_comentarios"
    EVALUAR_ARTICULOS = "evaluar_articulos"
    MANEJO_ROLES = "manejo_roles"
    MANEJAR_CATEGORIAS = "manejar_categorias"
