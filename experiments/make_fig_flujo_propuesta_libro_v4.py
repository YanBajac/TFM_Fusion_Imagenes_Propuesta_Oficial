# -*- coding: utf-8 -*-
"""Figura fig:flujo_propuesta del libro (cap3, sec:propuesta): diagrama de bloques del operador.

QUE MUESTRA. El camino de src/fusion/optimal_top_hat.py::fuse_optimal con mode="sum", el de la
propuesta en todos los experimentos (run_all_fusions.py: CONFIG["Propuesta_Novedosa"]), caja por caja:
  1. Las dos entradas, la imagen visible y la infrarroja.
  2. Un recuadro discontinuo que se recorre una vez con cada imagen f (combined_top_hat):
       - con el disco D_r: WTH = f - apertura, BTH = cierre - f;
       - con cada uno de los cuatro segmentos S_{r,theta} (theta en _ANGLES = 0, 45, 90, 135): lo mismo;
       - el promedio de las cuatro WTH y, aparte, el de las cuatro BTH;
       - la suma del disco y del promedio, que da WTH_VIS y BTH_VIS con la visible y WTH_IR y BTH_IR
         con la infrarroja (Ecuacion eq:banco del libro). Esos nombres van como rotulo de las dos
         flechas que salen del recuadro.
     El rotulo del recuadro va sobre su borde, y la caja «Imagen f» recibe las dos entradas.
  3. El detalle claro, max(WTH_VIS, WTH_IR), y el oscuro, max(BTH_VIS, BTH_IR), pixel a pixel.
  4. La regla de fusion (Ecuacion eq:regla-tophat): la imagen base, (I_VIS + I_IR)/2, mas m por el
     detalle claro menos m por el oscuro, recortada al intervalo de 0 a 1. La imagen base sale
     directamente de las dos entradas: por eso las dos lineas laterales, que no pasan por el recuadro.
  5. La imagen fusionada F, con el borde azul de la propuesta.
Sin el ajuste por enjambre (va en otra figura) ni valores de r y m: el diagrama vale para cualquier
configuracion. La adoptada (r = 25, m = 0.30) se dice en la nota del libro.

COMPROBACION CONTRA EL CODIGO. Antes de dibujar, verificar_contra_codigo() rehace la fusion siguiendo
las cajas del diagrama, una por una, con OpenCV, y la compara con fuse_optimal sobre un par de imagenes
de prueba con la configuracion adoptada (leida de run_all_fusions.py sin ejecutarlo). Si el codigo de
src cambia y el diagrama deja de describirlo, el script se detiene. Los angulos de los segmentos y su
orden se toman de optimal_top_hat._ANGLES.

PICTOGRAMAS. El disco y los cuatro segmentos se dibujan con el mismo largo, 2r+1, como en el codigo.
El de 45 grados baja de izquierda a derecha, porque los angulos se miden con las filas creciendo hacia
abajo (cap3, Ecuacion eq:segmentos; linear_se en el codigo).

Estilo: el comun de las figuras del libro (experiments/estilo_figuras_libro.py): Times New Roman, cajas
rectas con relleno gris claro y borde gris, como las de fig_metodologia, flechas grises; la caja del
resultado con borde azul, el unico color.

Tamano de letra: el lienzo mide 0.8 del ancho de la caja de texto (160 mm), y el LaTeX la incluye con
width=0.8\\textwidth, de modo que los cuerpos de letra son los reales: 10 pt en los nombres de las cajas
y 9 pt en el detalle. Se guarda sin recortar, para conservar ese ancho. El script comprueba que cada
texto entre en su caja.

Salida: docs/libro_v4/figuras/fig_flujo_propuesta.png (300 ppp)

Uso (desde la raiz del repo):
    .venv\\Scripts\\python.exe -X utf8 experiments/make_fig_flujo_propuesta_libro_v4.py
"""
import ast
import os
import sys
from pathlib import Path

# La raiz del repo se puede pasar como argumento; si no, es la carpeta padre de la del script.
RAIZ = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(RAIZ))

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from estilo_figuras_libro import (ANCHO_TEXTO_PULG, AZUL, GRIS, GRIS_CLARO, GRIS_OSCURO, NEGRO,
                                  aplicar_estilo, guardar)
from src.fusion import optimal_top_hat as oth

ANCHO_LIBRO = 0.8                   # fraccion de \textwidth con que se incluye
ANCHO = ANCHO_LIBRO * ANCHO_TEXTO_PULG          # 5.04 pulgadas

BORDE = GRIS_OSCURO
TAM_TITULO, TAM_DETALLE = 10, 9
LW_CAJA = 0.8
LW_PROPUESTA = 1.4                  # el borde azul del resultado, un poco mas grueso
MARGEN = 0.07                       # aire minimo entre el texto y el borde de la caja (pulgadas)

# alturas de las bandas de texto dentro de una caja (pulgadas)
PAD = 0.07                          # arriba y abajo
H_TITULO = 0.20
H_LINEA = 0.165
H_FORMULA = 0.25                    # una linea con fraccion
HUECO = 0.24                        # entre dos filas de cajas, para la flecha

_textos = []                        # (artista, x0, x1, y0, y1 de su caja) para comprobar


# ---------------------------------------------------------------- comprobacion contra src
def _config_adoptada():
    """Lee PROP_R y PROP_M de experiments/run_all_fusions.py sin ejecutarlo."""
    fuente = RAIZ / "experiments" / "run_all_fusions.py"
    texto = fuente.read_text(encoding="utf-8")
    for nodo in ast.parse(texto).body:
        if (isinstance(nodo, ast.Assign) and isinstance(nodo.targets[0], ast.Tuple)
                and [t.id for t in nodo.targets[0].elts] == ["PROP_R", "PROP_M"]):
            r, m = ast.literal_eval(nodo.value)
            break
    else:
        raise SystemExit("run_all_fusions.py no define PROP_R, PROP_M")
    linea = next(l for l in texto.splitlines() if l.strip().startswith('"Propuesta_Novedosa": {'))
    if '"mode": "sum"' not in linea:
        raise SystemExit(f"la propuesta ya no usa mode='sum': {linea.strip()}")
    return r, m


def verificar_contra_codigo():
    """Rehace la fusion caja por caja y la compara con fuse_optimal. Devuelve (r, m) adoptados."""
    if tuple(oth._ANGLES) != (0, 45, 90, 135):
        raise SystemExit(f"los angulos del codigo cambiaron: {oth._ANGLES}")
    r, m = _config_adoptada()

    def apertura(f, b):
        return cv2.morphologyEx(f, cv2.MORPH_OPEN, b)

    def cierre(f, b):
        return cv2.morphologyEx(f, cv2.MORPH_CLOSE, b)

    def recuadro(f):
        """Lo que hace el recuadro discontinuo con una imagen f."""
        disco = oth.disk_se(r)
        wth_disco, bth_disco = f - apertura(f, disco), cierre(f, disco) - f
        segs = [oth.linear_se(r, th) for th in oth._ANGLES]
        prom_wth = sum(f - apertura(f, s) for s in segs) / 4
        prom_bth = sum(cierre(f, s) - f for s in segs) / 4
        return wth_disco + prom_wth, bth_disco + prom_bth

    # par de prueba: manchas claras y oscuras de varios tamanos sobre un fondo suave
    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:120, 0:150].astype(np.float32)
    pares = []
    for _ in range(2):
        img = 0.5 + 0.2 * np.sin(xx / 23.0) * np.cos(yy / 31.0)
        for _ in range(25):
            cy, cx = rng.uniform(0, 120), rng.uniform(0, 150)
            s = rng.uniform(1.5, 12.0)
            img += rng.uniform(-0.5, 0.5) * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s))
        pares.append(np.clip(img + rng.normal(0, 0.02, img.shape), 0, 1).astype(np.float32))
    vis, ir = pares

    wth_vis, bth_vis = recuadro(vis)
    wth_ir, bth_ir = recuadro(ir)
    claro = np.maximum(wth_vis, wth_ir)
    oscuro = np.maximum(bth_vis, bth_ir)
    base = (vis + ir) / 2
    F = np.clip(base + m * claro - m * oscuro, 0, 1)

    G = oth.fuse_optimal(vis, ir, r=r, m=m, mode="sum")
    dif = float(np.max(np.abs(F - G)))
    if dif > 1e-5:
        raise SystemExit(f"el diagrama no reproduce fuse_optimal: diferencia maxima {dif:.2e}")
    print(f"  diagrama = fuse_optimal(r={r}, m={m}, mode='sum'): diferencia maxima {dif:.1e}")
    return r, m


# ---------------------------------------------------------------- dibujo
def alto_de(contenido):
    h = 2 * PAD
    for tipo, *resto in contenido:
        h += {"tit": H_TITULO, "lin": H_LINEA, "formula": H_FORMULA}.get(tipo, 0)
        if tipo == "picto":
            h += resto[0]
    return h


def caja(ax, xc, y_sup, ancho, contenido, alto=None, borde=BORDE, lw=LW_CAJA, alinear="sup"):
    """Caja recta con relleno gris claro. contenido: lista de ("tit", texto), ("lin", texto), ("formula", texto) o
    ("picto", alto, funcion(ax, xc, yc)). Devuelve (x0, x1, y0, y1) de la caja.
    alinear="centro": el bloque de contenido se centra en un alto mayor que el suyo."""
    propio = alto_de(contenido)
    alto = alto or propio
    x0, x1, y1 = xc - ancho / 2, xc + ancho / 2, y_sup
    y0 = y1 - alto
    ax.add_patch(Rectangle((x0, y0), ancho, alto, linewidth=lw, edgecolor=borde,
                           facecolor=GRIS_CLARO, zorder=2))
    y = y1 - PAD - (alto - propio) / 2
    for tipo, *resto in contenido:
        if tipo == "picto":
            h, funcion = resto
            funcion(ax, xc, y - h / 2)
            y -= h
            continue
        h = {"tit": H_TITULO, "lin": H_LINEA, "formula": H_FORMULA}[tipo]
        t = ax.text(xc, y - h / 2, resto[0], ha="center", va="center", zorder=3,
                    fontsize=TAM_TITULO if tipo == "tit" else TAM_DETALLE,
                    fontweight="bold" if tipo == "tit" else "normal", color=NEGRO)
        _textos.append((t, x0, x1, y0, y1))
        y -= h
    return x0, x1, y0, y1


PUNTA = dict(arrowstyle="-|>", color=BORDE, lw=0.9, mutation_scale=11, shrinkA=0, shrinkB=0)


def conector(ax, puntos):
    """Linea quebrada gris por los puntos dados, con punta de flecha en el ultimo."""
    xs, ys = zip(*puntos)
    if len(puntos) > 2:
        ax.plot(xs[:-1], ys[:-1], color=BORDE, lw=0.9, solid_joinstyle="miter",
                solid_capstyle="butt", zorder=1)
    ax.annotate("", xy=puntos[-1], xytext=puntos[-2], arrowprops=PUNTA, zorder=1)


def picto_disco(radio_dibujo):
    def dibujar(ax, xc, yc):
        ax.add_patch(Circle((xc, yc), radio_dibujo, facecolor=GRIS, edgecolor=BORDE,
                            linewidth=0.8, zorder=3))
    return dibujar


def picto_segmentos(medio_largo, separacion, h_rotulo):
    """Los cuatro segmentos, en el orden de _ANGLES, con su angulo debajo. Angulos de imagen: las
    filas crecen hacia abajo, asi que el de 45 grados baja de izquierda a derecha."""
    def dibujar(ax, xc, yc):
        n = len(oth._ANGLES)
        y_seg = yc + h_rotulo / 2
        for k, th in enumerate(oth._ANGLES):
            x = xc + (k - (n - 1) / 2) * separacion
            a = np.deg2rad(th)
            dx, dy = medio_largo * np.cos(a), -medio_largo * np.sin(a)
            ax.plot([x - dx, x + dx], [y_seg - dy, y_seg + dy], color=BORDE, lw=2.2,
                    solid_capstyle="butt", zorder=3)
            ax.text(x, y_seg - medio_largo - 0.03 - (h_rotulo - 0.03) / 2, f"{th}°",
                    ha="center", va="center", fontsize=TAM_DETALLE, color=NEGRO, zorder=3)
    return dibujar


def comprobar(fig, ax):
    """Falla si algun texto no entra en su caja con el margen pedido, a lo ancho o a lo alto.
    Las coordenadas de los datos son pulgadas (los ejes ocupan toda la figura, 1 unidad = 1 pulgada)."""
    r = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    for t, x0, x1, y0, y1 in _textos:
        bb = t.get_window_extent(renderer=r).transformed(inv)
        if bb.x0 < x0 + MARGEN or bb.x1 > x1 - MARGEN:
            raise SystemExit(f"no entra a lo ancho ({bb.width:.2f} in de {x1 - x0:.2f}): {t.get_text()}")
        if bb.y0 < y0 + MARGEN / 3 or bb.y1 > y1 - MARGEN / 3:
            raise SystemExit(f"no entra a lo alto (texto {bb.y0:.3f} a {bb.y1:.3f}, caja {y0:.3f} "
                             f"a {y1:.3f}): {t.get_text()}")


def main():
    r_adoptado, m_adoptado = verificar_contra_codigo()
    aplicar_estilo()

    W = ANCHO
    CARRIL = 0.09                   # x de las lineas laterales de la imagen base
    MARCO_X0, MARCO_X1 = 0.23, W - 0.23     # recuadro discontinuo
    IN_X0, IN_X1 = MARCO_X0 + 0.12, MARCO_X1 - 0.12
    ANCHO_IZQ, ANCHO_DER = 1.62, 2.50
    XL = IN_X0 + ANCHO_IZQ / 2      # columna del disco
    XR = IN_X1 - ANCHO_DER / 2      # columna de los segmentos
    ANCHO_ENT = 1.70                # las dos entradas, alineadas con los bordes interiores
    X_ENT_V, X_ENT_I = IN_X0 + ANCHO_ENT / 2, IN_X1 - ANCHO_ENT / 2
    X_CLARO, X_OSCURO = 1.30, W - 1.30
    ANCHO_DET = 1.90

    # ------------------------------------------------ contenidos
    entrada_v = [("tit", "Imagen visible $I_{\\mathrm{VIS}}$")]
    entrada_i = [("tit", "Imagen infrarroja $I_{\\mathrm{IR}}$")]
    caja_f = [("tit", "Imagen $f$"), ("lin", "$I_{\\mathrm{VIS}}$ o $I_{\\mathrm{IR}}$")]
    H_ROT = 0.16
    caja_seg = [("tit", "Cuatro segmentos $S_{r,\\theta}$"),
                ("picto", 0.25 + H_ROT, picto_segmentos(0.11, 0.42, H_ROT)),
                ("lin", "Top-Hat blanca y negra con cada uno")]
    caja_disco = [("tit", "Disco $D_r$"),
                  ("picto", 0.28, picto_disco(0.11)),
                  ("lin", "Top-Hat blanca y negra")]
    caja_prom = [("tit", "Promedio de los cuatro"),
                 ("lin", "uno para la blanca (WTH)"),
                 ("lin", "y otro para la negra (BTH)")]
    caja_suma = [("tit", "Suma del disco y del promedio"),
                 ("lin", "la WTH del disco más la WTH promedio, y lo mismo con la BTH")]
    caja_claro = [("tit", "Detalle claro"),
                  ("lin", "$\\max(\\mathrm{WTH}_{\\mathrm{VIS}},\\, \\mathrm{WTH}_{\\mathrm{IR}})$"),
                  ("lin", "el mayor, píxel a píxel")]
    caja_oscuro = [("tit", "Detalle oscuro"),
                   ("lin", "$\\max(\\mathrm{BTH}_{\\mathrm{VIS}},\\, \\mathrm{BTH}_{\\mathrm{IR}})$"),
                   ("lin", "el mayor, píxel a píxel")]
    caja_regla = [("tit", "Regla de fusión con el peso $m$"),
                  ("lin", "imagen base: promedio de las dos, "
                          "$(I_{\\mathrm{VIS}} + I_{\\mathrm{IR}})\\,/\\,2$"),
                  ("lin", "$F$ = imagen base + $m$ · detalle claro − $m$ · detalle oscuro,"),
                  ("lin", "recortada al intervalo de 0 a 1")]
    caja_res = [("tit", "Imagen fusionada $F$")]

    # ------------------------------------------------ alturas y posiciones, de arriba hacia abajo
    h_ent = alto_de(entrada_v)
    h_f, h_seg = alto_de(caja_f), alto_de(caja_seg)
    h_disco, h_prom = alto_de(caja_disco), alto_de(caja_prom)
    h_suma = alto_de(caja_suma)
    h_det = alto_de(caja_claro)
    h_regla, h_res = alto_de(caja_regla), alto_de(caja_res)
    ROTULO_FLECHA = 0.22            # tramo de las flechas que salen del recuadro, con su rotulo

    y = -0.04                                   # se trabaja con y negativas y se corrige al final
    y_ent = y
    y -= h_ent + 0.30
    y_marco_sup = y                             # el rotulo del recuadro va sobre esta linea
    y -= 0.15
    y_filaA = y                                 # tope de los segmentos
    y -= h_seg + HUECO
    y_filaB = y
    y -= max(h_disco, h_prom) + HUECO
    y_suma = y
    y -= h_suma + 0.08
    y_marco_inf = y
    y -= ROTULO_FLECHA + 0.06
    y_det = y
    y -= h_det + HUECO
    y_regla = y
    y -= h_regla + HUECO
    y_res = y
    y -= h_res + 0.04
    ALTO = -y

    fig = plt.figure(figsize=(W, ALTO))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(-ALTO, 0)
    ax.axis("off")

    # ------------------------------------------------ cajas
    ev = caja(ax, X_ENT_V, y_ent, ANCHO_ENT, entrada_v)
    ei = caja(ax, X_ENT_I, y_ent, ANCHO_ENT, entrada_i)

    ax.add_patch(Rectangle((MARCO_X0, y_marco_inf), MARCO_X1 - MARCO_X0, y_marco_sup - y_marco_inf,
                           linewidth=0.8, edgecolor=BORDE, facecolor="none",
                           linestyle=(0, (4, 2.5)), zorder=0))
    # rotulo del recuadro, sobre su borde superior, como el de un grupo de opciones en Word
    ax.text(MARCO_X1 - 0.14, y_marco_sup, "Se repite con cada imagen, por separado",
            ha="right", va="center", fontsize=TAM_DETALLE, style="italic", color=GRIS_OSCURO,
            zorder=3, bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none"))

    sg = caja(ax, XR, y_filaA, ANCHO_DER, caja_seg)
    yc_A = y_filaA - h_seg / 2
    cf = caja(ax, XL, yc_A + h_f / 2, 1.20, caja_f)
    dc = caja(ax, XL, y_filaB, ANCHO_IZQ, caja_disco)
    pr = caja(ax, XR, y_filaB, ANCHO_DER, caja_prom)
    su = caja(ax, W / 2, y_suma, IN_X1 - IN_X0, caja_suma)
    cl = caja(ax, X_CLARO, y_det, ANCHO_DET, caja_claro)
    co = caja(ax, X_OSCURO, y_det, ANCHO_DET, caja_oscuro)
    rg = caja(ax, W / 2, y_regla, IN_X1 - IN_X0, caja_regla)
    rs = caja(ax, W / 2, y_res, 1.80, caja_res, borde=AZUL, lw=LW_PROPUESTA)

    # ------------------------------------------------ flechas
    # las dos entradas llegan a la caja f (cada una por su lado: la caja se recorre dos veces)
    x_fv, x_fi = XL - 0.22, XL + 0.22
    conector(ax, [(x_fv, ev[2]), (x_fv, cf[3])])
    y_codo = (ei[2] + y_marco_sup) / 2
    conector(ax, [(X_ENT_I, ei[2]), (X_ENT_I, y_codo), (x_fi, y_codo), (x_fi, cf[3])])
    # f va al disco y a los segmentos
    conector(ax, [(cf[1], yc_A), (sg[0], yc_A)])
    conector(ax, [(XL, cf[2]), (XL, dc[3])])
    conector(ax, [(XR, sg[2]), (XR, pr[3])])
    # disco y promedio se suman
    conector(ax, [(XL, dc[2]), (XL, su[3])])
    conector(ax, [(XR, pr[2]), (XR, su[3])])
    # la suma da las WTH y las BTH de las dos imagenes; cada flecha lleva su rotulo debajo del recuadro
    conector(ax, [(X_CLARO, su[2]), (X_CLARO, cl[3])])
    conector(ax, [(X_OSCURO, su[2]), (X_OSCURO, co[3])])
    y_rot = (y_marco_inf + cl[3]) / 2
    for x, texto in ((X_CLARO, "$\\mathrm{WTH}_{\\mathrm{VIS}}$ y $\\mathrm{WTH}_{\\mathrm{IR}}$"),
                     (X_OSCURO, "$\\mathrm{BTH}_{\\mathrm{VIS}}$ y $\\mathrm{BTH}_{\\mathrm{IR}}$")):
        ax.text(x + 0.07, y_rot, texto, ha="left", va="center", fontsize=TAM_DETALLE, color=NEGRO)
    conector(ax, [(X_CLARO, cl[2]), (X_CLARO, rg[3])])
    conector(ax, [(X_OSCURO, co[2]), (X_OSCURO, rg[3])])
    # la imagen base sale directamente de las dos entradas, por fuera del recuadro
    yc_regla = (rg[2] + rg[3]) / 2
    yc_ent = (ev[2] + ev[3]) / 2
    conector(ax, [(ev[0], yc_ent), (CARRIL, yc_ent), (CARRIL, yc_regla), (rg[0], yc_regla)])
    conector(ax, [(ei[1], yc_ent), (W - CARRIL, yc_ent), (W - CARRIL, yc_regla), (rg[1], yc_regla)])
    # la regla da la imagen fusionada
    conector(ax, [(W / 2, rg[2]), (W / 2, rs[3])])

    comprobar(fig, ax)
    print(f"  configuracion adoptada (para la nota): r = {r_adoptado}, m = {m_adoptado}")
    guardar(fig, "fig_flujo_propuesta", ancho_libro=ANCHO_LIBRO, recortar=False)
    plt.close(fig)


if __name__ == "__main__":
    main()
