# -*- coding: utf-8 -*-
"""Estilo comun de las figuras del libro (docs/libro_v4/figuras).

POR QUE UN MODULO. Con un bloque de rcParams en cada generador de figura, las tipografias, los
tamanos de letra y los grises se separan, y una figura dibujada mas ancha que la pagina queda con la
letra en 6 pt cuando LaTeX la reduce. Todas importan esto, para que se vean como una sola familia.

EL ESTILO: sencillo y sobrio.
  - Fondo blanco, ejes finos, sin sombras, degradados ni adornos.
  - Grises para todo; el azul #4472c4 solo para la propuesta (su barra, su linea, su marco, su caja).
    Nada de rojo.
  - Tipografia con serifa: Times New Roman si esta instalada (Windows la trae), si no, DejaVu Serif.
    Las letras matematicas ($r$, $m$) van en STIX, que es del mismo corte que Times.
  - Sin titulo dentro de la imagen: el titulo va en el \\caption del libro.
  - Punto decimal, rotulos en castellano.

TAMANO DE LETRA. El ancho de la caja de texto del libro es 160 mm (A4 con margenes de 25 mm). Cada
figura se dibuja con el ancho al que el LaTeX la incluye (ANCHO_TEXTO_PULG, o 0.9 de el, etc.), asi los
cuerpos de letra que se fijan aca son los que se imprimen: 10 pt el texto general, 9.5 pt las marcas de
los ejes. guardar() avisa en cuanto queda escalada la letra si el recorte final cambia el ancho.

NOMBRES de los metodos: se leen del diccionario CORTO de tools/generar_tablas_libro.py, que es el que
usan las tablas, para que figura y tabla digan lo mismo. Ahi «Curvelet» (el nombre en el codigo y en los
CSV) es la DWT (db4), y «Propuesta_Novedosa» es la propuesta.

Uso, desde un generador en experiments/:
    from estilo_figuras_libro import aplicar_estilo, guardar, AZUL, GRIS, NOMBRES, ANCHO_TEXTO_PULG
    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(ANCHO_TEXTO_PULG, 3.5))
    ...
    guardar(fig, "fig_algo")            # -> docs/libro_v4/figuras/fig_algo.png, 300 ppp
"""
import ast
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

RAIZ = Path(__file__).resolve().parents[1]
FIGURAS = RAIZ / "docs" / "libro_v4" / "figuras"
REPORTES = RAIZ / "experiments" / "results" / "metrics_reports"

# ---------------------------------------------------------------- colores
AZUL = "#4472c4"           # solo la propuesta
NEGRO = "#000000"          # texto y trazo principal
GRIS_OSCURO = "#595959"    # bordes de barras y cajas, texto secundario, segunda serie
GRIS = "#bfbfbf"           # barras de los demas metodos, curvas de referencia
GRIS_CLARO = "#f2f2f2"     # relleno de cajas
GRIS_REJILLA = "#d9d9d9"   # lineas de la cuadricula, cuando hay

# ---------------------------------------------------------------- medidas
ANCHO_TEXTO_MM = 160
ANCHO_TEXTO_PULG = ANCHO_TEXTO_MM / 25.4      # 6.30 pulgadas
DPI = 300

TAM_TEXTO = 10             # rotulos de ejes, textos dentro del grafico
TAM_MARCAS = 9.5           # numeros de los ejes
TAM_LEYENDA = 9.5


def _fuente_serif():
    nombres = {f.name for f in font_manager.fontManager.ttflist}
    return "Times New Roman" if "Times New Roman" in nombres else "DejaVu Serif"


FUENTE = _fuente_serif()


def aplicar_estilo():
    """Configura matplotlib con el estilo comun. Se llama una vez, antes de crear las figuras."""
    plt.rcdefaults()
    plt.rcParams.update({
        # tipografia
        "font.family": "serif",
        "font.serif": [FUENTE, "DejaVu Serif"],
        "mathtext.fontset": "stix" if FUENTE == "Times New Roman" else "dejavuserif",
        "font.size": TAM_TEXTO,
        "axes.labelsize": TAM_TEXTO,
        "axes.titlesize": TAM_TEXTO,
        "xtick.labelsize": TAM_MARCAS,
        "ytick.labelsize": TAM_MARCAS,
        "legend.fontsize": TAM_LEYENDA,
        "text.color": NEGRO,
        "axes.labelcolor": NEGRO,
        "axes.titleweight": "normal",
        # punto decimal y signo menos de verdad, sin depender del idioma del sistema
        "axes.formatter.use_locale": False,
        "axes.unicode_minus": True,
        # ejes finos, sin adornos
        "axes.linewidth": 0.6,
        "axes.edgecolor": NEGRO,
        "axes.facecolor": "white",
        "axes.grid": False,
        "axes.axisbelow": True,
        "grid.color": GRIS_REJILLA,
        "grid.linewidth": 0.5,
        "grid.linestyle": "-",
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.color": NEGRO,
        "ytick.color": NEGRO,
        "lines.linewidth": 1.2,
        "patch.linewidth": 0.6,
        "patch.edgecolor": GRIS_OSCURO,
        "hatch.linewidth": 0.5,
        # leyenda: recuadro fino y recto, sin sombra
        "legend.frameon": True,
        "legend.fancybox": False,
        "legend.shadow": False,
        "legend.framealpha": 1.0,
        "legend.edgecolor": GRIS_OSCURO,
        # salida
        "figure.facecolor": "white",
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
        "image.cmap": "gray",
    })


def guardar(fig, nombre, ancho_libro=1.0, recortar=True):
    """Escribe docs/libro_v4/figuras/<nombre>.png a 300 ppp, fondo blanco, sin canal alfa.

    ancho_libro: fraccion de \\textwidth con que el LaTeX incluye la figura (1.0, 0.9, 0.8...). Solo
    sirve para avisar: si el recorte deja la imagen mas angosta o mas ancha que ese ancho, LaTeX la
    estira o la achica, y la letra se imprime en esa proporcion.
    recortar: bbox ajustado al contenido (lo normal). Los diagramas que ya miden justo el ancho de la
    pagina pueden pasar False para conservar el lienzo tal cual.
    """
    from PIL import Image

    FIGURAS.mkdir(parents=True, exist_ok=True)
    destino = FIGURAS / f"{nombre}.png"
    extra = {"bbox_inches": "tight", "pad_inches": 0.03} if recortar else {}
    fig.savefig(destino, dpi=DPI, facecolor="white", edgecolor="white", **extra)
    # sin canal alfa: el fondo ya es blanco y el archivo pesa menos
    with Image.open(destino) as im:
        if im.mode != "RGB":
            im.convert("RGB").save(destino, optimize=True, dpi=(DPI, DPI))
    with Image.open(destino) as im:
        ancho_px, alto_px = im.size
    ancho_pulg, alto_pulg = ancho_px / DPI, alto_px / DPI
    escala = ancho_libro * ANCHO_TEXTO_PULG / ancho_pulg
    print(f"  {destino.relative_to(RAIZ)}: {ancho_pulg:.2f} x {alto_pulg:.2f} pulg; "
          f"incluida a {ancho_libro:g} del ancho de texto, la letra se imprime a {escala:.3f} "
          f"de su tamano ({TAM_TEXTO} pt -> {TAM_TEXTO * escala:.1f} pt)")
    return destino


# ---------------------------------------------------------------- nombres de los metodos
# Copia de respaldo del diccionario CORTO de tools/generar_tablas_libro.py, por si ese archivo no se
# pudiera leer. Lo normal es leerlo de alli (ver _leer_nombres), para que figuras y tablas coincidan.
_NOMBRES_RESPALDO = {
    "PiramideLaplace": "Pirámide de Laplace", "RatioPiramide": "Pirámide de razón",
    "DWT": "DWT (Haar)", "DTCWT": "DTCWT", "Curvelet": "DWT (db4)",
    "TopHat_Clasico": "Top-Hat clásico", "Propuesta_Novedosa": "Propuesta",
    "VIS": "Visible sola", "IR": "Infrarroja sola", "Promedio": "Promedio simple",
}


def _leer_nombres():
    """Lee CORTO de tools/generar_tablas_libro.py sin ejecutar ese script (solo se analiza el texto)."""
    fuente = RAIZ / "tools" / "generar_tablas_libro.py"
    try:
        arbol = ast.parse(fuente.read_text(encoding="utf-8"))
        for nodo in arbol.body:
            if isinstance(nodo, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "CORTO" for t in nodo.targets):
                return dict(ast.literal_eval(nodo.value))
    except (OSError, SyntaxError, ValueError) as e:
        print(f"  aviso: no se pudo leer CORTO de {fuente.name} ({e}); se usa la copia de respaldo")
        return dict(_NOMBRES_RESPALDO)
    print(f"  aviso: {fuente.name} no define CORTO; se usa la copia de respaldo")
    return dict(_NOMBRES_RESPALDO)


NOMBRES = _leer_nombres()
PROPUESTA = "Propuesta_Novedosa"     # clave interna de la propuesta en los CSV


def es_propuesta(clave):
    return clave == PROPUESTA


def color_metodo(clave):
    """Azul para la propuesta, gris para todo lo demas."""
    return AZUL if es_propuesta(clave) else GRIS
