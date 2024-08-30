from enum import Enum


class PermissionEnum(str, Enum):
    VER_INICIO = "ver_inicio"
    VER_CATEGORIAS_SUSCRIPTOR = "ver_categorias_suscriptor"
    VER_CATEGORIAS_PAGO = "ver_categorias_pago"
    CREAR_ARTICULOS = "crear_articulos"
    EDITAR_ARTICULOS = "editar_articulos"
    MODERAR_ARTICULOS = "moderar_articulos"
    PUBLICAR_COMENTARIOS = "publicar_comentarios"
    LEER_COMENTARIOS = "leer_comentarios"
    EVALUAR_ARTICULOS = "evaluar_articulos"
    MANEJO_ROLES = "manejo_roles"
