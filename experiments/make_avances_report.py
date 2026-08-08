# -*- coding: utf-8 -*-
"""Genera docs/Avances_Tesis.pdf — informe de avances (diseno simple tipo Word).
Propuesta con SUMA de ramas (r=25, m=0.30) vs 6 comparativos (LP, RP, DWT, DTCWT,
CVT, Top-Hat clasico) + deteccion LLVIP. Requiere Microsoft Edge para el paso HTML->PDF.
Uso: .venv\Scripts\python.exe -X utf8 experiments/make_avances_report.py"""
import base64, io, json, os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
warnings.filterwarnings("ignore")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG  = os.path.join(ROOT, "docs", "figures")
CUAL = os.path.join(FIG, "cualitativas")
# --------------------------------------------------------------- variante
# VARIANTE_AVANCES=restringido -> configuracion con el rango publicado m en [0,30; 2,00]
# VARIANTE_AVANCES=libre       -> configuracion con el rango de m ampliado
from datetime import date as _date
_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre")
_h = _date.today()
FECHA = f"{_h.day} de {_MESES[_h.month - 1]} de {_h.year}"

VARIANTE = os.environ.get("VARIANTE_AVANCES", "restringido").strip().lower()
assert VARIANTE in ("restringido", "libre"), f"VARIANTE_AVANCES invalida: {VARIANTE}"
LIBRE = (VARIANTE == "libre")

V = {
    "m": "0,0703" if LIBRE else "0,30",
    "rango": "[0,05; 1,20]" if LIBRE else "[0,30; 2,00]",
    "rango_anexo": "[0,01; 2,00]" if LIBRE else "[0,30; 2,00]",
    "etiqueta": ("configuración LIBRE — rango del peso ampliado"
                 if LIBRE else "configuración oficial — rango publicado del peso"),
    # La variante oficial ocupa el nombre canonico; la alternativa lleva sufijo.
    "sufijo": "_libre" if LIBRE else "",
}

MR = os.path.join(ROOT, "experiments", "results",
                  "metrics_reports_libre" if LIBRE else "metrics_reports")
OUT  = os.path.join(ROOT, "docs", "_local")
os.makedirs(OUT, exist_ok=True)
HTML_OUT = os.path.join(OUT, f"Avances_Tesis{V['sufijo']}.html")
PDF_OUT  = os.path.join(ROOT, "docs", f"Avances_Tesis{V['sufijo']}.pdf")
print(f"VARIANTE: {VARIANTE} | metricas: {os.path.basename(MR)} | salida: {os.path.basename(PDF_OUT)}")

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10, "axes.grid": True, "grid.alpha": 0.3, "grid.linewidth": 0.5,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
})

def b64(data, mime="image/png"):
    return f"data:{mime};base64," + base64.b64encode(data).decode()

def fig_to_b64(fig, dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return b64(buf.getvalue())

def file_img_b64(path, max_w=1400, jpeg_q=85):
    im = Image.open(path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=jpeg_q)
    return b64(buf.getvalue(), "image/jpeg")

def formula_b64(tex, fs=14):
    fig = plt.figure(figsize=(0.1, 0.1))
    t = fig.text(0, 0, f"${tex}$", fontsize=fs, color="black")
    fig.canvas.draw()
    bb = t.get_window_extent()
    fig.set_size_inches(bb.width / fig.dpi + 0.15, bb.height / fig.dpi + 0.12)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return b64(buf.getvalue())

# ------------------------------------------------------------------ datos
means = pd.read_csv(os.path.join(MR, "descriptive_means.csv")).set_index("method")
fried = pd.read_csv(os.path.join(MR, "friedman_results.csv"))
wilc  = pd.read_csv(os.path.join(MR, "wilcoxon_results.csv"))
rankm = pd.read_csv(os.path.join(MR, "ranking_methods.csv"), index_col=0)
grid  = pd.read_csv(os.path.join(MR, "pso_grid_search_fo_propuesta.csv")).rename(
    columns={"Fo_opt": "F_opt"})
det   = pd.read_csv(os.path.join(MR, "detection_llvip_map.csv")).set_index("method")

PROP = "Propuesta_Novedosa"
ORDEN = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
         "TopHat_Clasico", PROP]
LBL = {"PiramideLaplace": "Pirámide de Laplace (LP)",
       "RatioPiramide": "Ratio of low-pass Pyramid (RP)",
       "DWT": "Wavelet discreta (DWT)",
       "DTCWT": "Dual-Tree Complex Wavelet (DTCWT)",
       "Curvelet": "Curvelet (CVT)",
       "TopHat_Clasico": "Top-Hat clásico",
       PROP: f"Propuesta novedosa (r=25, m={V['m']})"}
SHORT = {"PiramideLaplace": "LP", "RatioPiramide": "RP", "DWT": "DWT", "DTCWT": "DTCWT",
         "Curvelet": "CVT", "TopHat_Clasico": "TH clás.", PROP: "Propuesta"}
DIRECTION = {"EN": 1, "SD": 1, "FE": 1, "MG": 1, "MI_vis": 1, "MI_ir": 1, "SF": 1,
             "SSIM": 1, "PSNR": 1}
METS = list(DIRECTION.keys())

def tabla_metodos(methods, resaltar=None):
    best = {}
    for mk in METS:
        vals = {m: means.loc[m, mk] for m in methods}
        best[mk] = (max if DIRECTION[mk] > 0 else min)(vals, key=vals.get)
    head = "".join(f'<th>{mk}&nbsp;{"↑" if DIRECTION[mk] > 0 else "↓"}</th>' for mk in METS)
    rows = []
    for m in methods:
        tds = []
        for mk in METS:
            v = means.loc[m, mk]
            b = "<b>" if best.get(mk) == m else ""
            tds.append(f'<td>{b}{v:.3f}{"</b>" if b else ""}</td>')
        name = LBL.get(m, m)
        if m == resaltar:
            name = f"<b>{name}</b>"
        rows.append(f'<tr><td class="l">{name}</td>{"".join(tds)}</tr>')
    return (f'<table><tr><th class="l">Método</th>{head}</tr>{"".join(rows)}</table>')

n_best_prop = sum(1 for mk in METS
                  if (max if DIRECTION[mk] > 0 else min)(
                      {m: means.loc[m, mk] for m in ORDEN},
                      key=lambda k: {m: means.loc[m, mk] for m in ORDEN}[k]) == PROP)

# ------------------------------------------------------------------ valores de la narrativa
_rk = rankm["avg_rank"].sort_values()
POS_RANK = list(_rk.index).index(PROP) + 1
VAL_RANK = f"{_rk[PROP]:.2f}".replace(".", ",")
LIDER_RANK = f"{_rk.iloc[0]:.2f}".replace(".", ",")

# Las TRES agregaciones que ranking_methods.csv ya calcula. El informe leia solo la primera, que
# es la que mas favorece a la propuesta, y afirmaba «con separacion estadisticamente
# significativa» sin ningun test que respaldara esa separacion: Friedman y Wilcoxon corren por
# metrica sobre los valores, no sobre el rango promedio. Las tres columnas estan en el CSV, una al
# lado de la otra, de modo que cualquiera que lo abra ve lo que el informe no decia — y con la
# tercera hay EMPATE. Publicarlo es mejor que ocultarlo: el orden de merito dependiendo de como se
# agrega es exactamente lo que sostiene H2, o sea el segundo aporte del trabajo.
_AGREG = [("avg_rank", "Rangos por métrica, las nueve",
           "el criterio del trabajo de referencia"),
          ("avg_rank_sin_FE", "Rangos por métrica, sin FE",
           "las ocho dimensiones efectivas: FE es EN reescalada"),
          ("avg_rank_medias", "Rango de los promedios",
           "se promedia primero y se rankea después")]


def _pos_val(col):
    s_ = rankm[col].sort_values()
    return list(s_.index).index(PROP) + 1, s_[PROP], s_


AG_FILAS = []
for _c, _et, _por in _AGREG:
    _p, _v, _s = _pos_val(_c)
    _empatan = [i for i in _s.index if abs(_s[i] - _v) < 5e-4 and i != PROP]
    # Cuando la propuesta lidera, repetir «lider: la propuesta (su propio valor)» no informa nada:
    # lo util es quien le sigue y por cuanto. La cuarta columna muestra eso.
    _otros = [i for i in _s.index if i != PROP and i not in _empatan]
    _seg = _otros[0] if _otros else None
    AG_FILAS.append((_et, _por, _p, _v, _seg, (_s[_seg] if _seg else float("nan")), _empatan))
# el empate de la tercera agregacion es el dato que hace valer la tabla; si desaparece, el parrafo
# que lo comenta deja de tener sentido y hay que reescribirlo
AG_EMPATE = AG_FILAS[2][6]
POS_MEDIAS = AG_FILAS[2][2]

_coma = lambda v, nd: f"{v:.{nd}f}".replace(".", ",")

# ---------------------------------------------------------------- las siete hipotesis
# El informe usaba «H5» como etiqueta sin definirla en ninguna parte. La tabla las enuncia y dice
# donde se contrasta cada una EN ESTE INFORME, que no es donde las contrasta el libro. Las dos
# columnas de la derecha estan escritas a mano a proposito: son una afirmacion editorial sobre la
# estructura del propio documento, no una cifra derivable de un CSV.
_HIP = [
    ("H1", "operador", "El banco no mejora de manera uniforme: desplaza el punto de operación "
     "hacia la actividad espacial y en contra de la fidelidad a las fuentes.",
     "§8 y §9"),
    ("H2", "criterio", "El orden de mérito no es propiedad del operador sino del criterio: cambia "
     "al cambiar la composición del conjunto de métricas, sin que cambie ninguna imagen.",
     "§9 y §10"),
    ("H3", "criterio", "La batería de nueve métricas «mayor es mejor» es insuficiente: sus "
     "métricas de actividad crecen con la varianza inyectada y no distinguen detalle de ruido.",
     "§7 (resumen)"),
    ("H4", "criterio", "La batería contiene al menos una métrica que no aporta información "
     "independiente de las demás.",
     "§9"),
    ("H5", "criterio", "La optimización no determina la configuración adoptada: los dos "
     "hiperparámetros se apoyan en parte del mismo criterio con que después se evalúa.",
     "§5, once páginas"),
    ("H6", "criterio", "El orden de mérito de las métricas de imagen no predice el orden de "
     "utilidad en la tarea, y ninguna fusión supera por un margen distinguible a la mejor "
     "modalidad individual.",
     "§13 y §14"),
    ("H7", "operador", "Con el radio y el peso igualados, el banco de cinco elementos produce un "
     "perfil de métricas distinto del que produce el disco único.",
     "§10"),
]
assert sum(1 for _h in _HIP if _h[1] == "criterio") == 5 and len(_HIP) == 7, \
    "el reparto 2 operador / 5 criterio es el argumento de los dos aportes: si cambia, hay que " \
    "reescribir la lectura de la pagina y la lamina 4 del deck"
TAB_HIPOTESIS = (
    '<table class="chica"><thead><tr><th>H</th><th>Familia</th>'
    '<th class="l">Enunciado</th><th>En este informe</th></tr></thead><tbody>'
    + "".join(f"<tr><td><b>{h}</b></td><td>{fam}</td><td class='l'>{txt}</td><td>{dnd}</td></tr>"
              for h, fam, txt, dnd in _HIP) + '</tbody></table>')


# las columnas de metrica de ranking_methods.csv, o sea todo lo que no es una agregacion
N_METRICAS_RK = len([c for c in rankm.columns if not c.startswith("avg_rank")])
def _celda_seg(p, emp, seg, vseg):
    """Cuarta columna: con quien empata, o a quien le lleva ventaja y por cuanto."""
    if emp:
        return ('<b>empata</b> con ' + ' y '.join(LBL.get(x, x).split(" (")[0] for x in emp))
    if seg is None:
        return "&mdash;"
    quien = LBL.get(seg, seg).split(" (")[0]
    return (f'le sigue {quien} ({_coma(vseg, 3)})' if p == 1
            else f'lidera {quien} ({_coma(vseg, 3)})')


TAB_AGREGACIONES = (
    '<table class="chica"><thead><tr><th class="l">Forma de agregar</th>'
    '<th>Puesto de la propuesta</th><th>Valor</th>'
    '<th class="l">El rival más cercano</th></tr></thead><tbody>'
    + "".join(
        f"<tr><td class='l'>{et}<br><span style='font-size:8.5pt;color:#444'>{por}</span></td>"
        f"<td>{p}.º{' <b>(empate)</b>' if emp else ''}</td><td>{_coma(v, 3)}</td>"
        f"<td class='l'>{_celda_seg(p, emp, seg, vseg)}</td></tr>"
        for et, por, p, v, seg, vseg, emp in AG_FILAS) + '</tbody></table>')

# Potencia del contraste de McNemar del conteo por escena (experiments/potencia_mcnemar.py).
# El informe decia que la hipotesis de traslacion «se rechaza, con muestra suficiente». El
# contraste es un McNemar exacto que NO rechaza —p = 0,21—, de modo que apoyarse en el exige decir
# para que diferencia alcanza la muestra. Eso es una cuenta y ahora esta corrida.
_pot = pd.read_csv(os.path.join(MR, "potencia_mcnemar.csv"))
_d80 = _pot[_pot.potencia >= 0.80]
POT_DELTA80 = f"{float(_d80.delta_pp.iloc[0]):.1f}".replace(".", ",")
_cr = pd.read_csv(os.path.join(MR, "complementariedad_resumen.csv")).set_index("entrada")
POT_B = int(_cr.loc[PROP, "gana_vs_VIS"])
POT_C = int(_cr.loc[PROP, "pierde_vs_VIS"])
POT_ND = POT_B + POT_C
_dif_obs = 100.0 * (_cr.loc[PROP, "recupera_ambas"] - _cr.loc["VIS", "recupera_ambas"]) / _cr.loc[PROP, "escenas"]
POT_DIF_OBS = f"{abs(_dif_obs):.1f}".replace(".", ",")
POT_EN_OBS = f"{float(_pot.iloc[(_pot.delta_pp - abs(_dif_obs)).abs().argsort().iloc[0]].potencia):.2f}".replace(".", ",")
assert _dif_obs < 0, "la diferencia por escena dejo de ser adversa: revisar el parrafo de H6"
_fus = det.drop(index=[x for x in ("VIS", "IR") if x in det.index])
LLVIP_PROP = f"{det.loc[PROP, 'mAP50']:.3f}".replace(".", ",")
LLVIP_LO = f"{_fus['mAP50'].min():.3f}".replace(".", ",")
LLVIP_HI = f"{_fus['mAP50'].max():.3f}".replace(".", ",")
# El visible y el infrarrojo estaban escritos a mano en la lectura de la Tabla 9, con
# 0,808 y 0,957 de una corrida anterior, mientras la tabla de arriba —generada desde el
# CSV— imprimia 0,813 y 0,971. Ahora los tres salen del mismo dato.
LLVIP_VIS = f"{det.loc['VIS', 'mAP50']:.3f}".replace(".", ",")
LLVIP_IR = f"{det.loc['IR', 'mAP50']:.3f}".replace(".", ",")

# Composicion del corpus: los 20 pares NO son 20 sujetos independientes. Cuatro escenas
# aportan varias tomas, de modo que los bloques de Friedman y Wilcoxon no son plenamente
# independientes. El libro lo declara dos veces —una como limitacion— y este informe lo
# omitia por completo, presentando n = 20 bloques donde hay 13 sujetos.
import re as _re


def _sujeto(nombre):
    for patron in (r'^(APC_\d+)_view_\d+',
                   r'^(Athena_soldier_behind_smoke)_\d+',
                   r'^(Athena_soldier_in_trench)_\d+'):
        m = _re.match(patron, nombre)
        if m:
            return m.group(1)
    return nombre


_grupos = {}
for _img in pd.read_csv(os.path.join(MR, "all_metrics.csv")).image.unique():
    _grupos.setdefault(_sujeto(_img), []).append(_img)
N_SUJETOS = len(_grupos)
_ETIQ = {'APC_1': 'APC_1', 'APC_3': 'APC_3',
         'Athena_soldier_behind_smoke': 'el soldado tras la cortina de humo',
         'Athena_soldier_in_trench': 'el soldado en trinchera'}
_PALABRA = {2: 'dos tomas', 3: 'tres tomas'}
SUJETOS_MULTI = '; '.join(
    f"{_ETIQ.get(k, k)} con {_PALABRA.get(len(v), str(len(v)) + ' tomas')}"
    for k, v in sorted(_grupos.items(), key=lambda x: (-len(x[1]), x[0])) if len(v) > 1)
_N_PARES = sum(len(v) for v in _grupos.values())
assert SUJETOS_MULTI and N_SUJETOS < _N_PARES, \
    f"se esperaban escenas repetidas y hay {N_SUJETOS} sujetos para {_N_PARES} pares"
_m3 = pd.read_csv(os.path.join(MR, "detection_m3fd_map.csv")).set_index("method")
_m3["par"] = (_m3["AP50_People"] + _m3["AP50_Lamp"]) / 2
_m3f = _m3.drop(index=[x for x in ("VIS", "IR") if x in _m3.index])
M3_PROP_PAR = f"{_m3.loc[PROP, 'par']:.3f}".replace(".", ",")
M3_PROP_MAP = f"{_m3.loc[PROP, 'mAP50']:.3f}".replace(".", ",")
M3_MEJOR = _m3f["par"].idxmax()
M3_MEJOR_PAR = f"{_m3f['par'].max():.3f}".replace(".", ",")
M3_PROP_ES_MEJOR = (M3_MEJOR == PROP)
M3_SUPERA_AMBAS = bool(_m3.loc[PROP, "par"] > _m3.loc["VIS", "par"]
                       and _m3.loc[PROP, "par"] > _m3.loc["IR", "par"])

# Tamano de la particion de prueba, leido del dataset generado (no fijado a mano).
_m3dir = os.path.join(ROOT, "datasets", "m3fd_test_VIS", "images", "val")
M3_N = (len([f for f in os.listdir(_m3dir) if f.lower().endswith((".jpg", ".png"))])
        if os.path.isdir(_m3dir) else 500)


def _n(x, d=3):
    return f"{x:.{d}f}".replace(".", ",")


# Lectura de la tabla de AP por clase construida desde los datos: cada afirmacion se verifica antes de
# escribirse, porque con un split o un checkpoint distintos varias de ellas se invierten.
_sup_amb = [k for k in _m3f.index
            if _m3f.loc[k, "par"] > _m3.loc["VIS", "par"]
            and _m3f.loc[k, "par"] > _m3.loc["IR", "par"]]
_rec_ambas = [k for k in _m3f.index
              if _m3f.loc[k, "AP50_People"] > 0 and _m3f.loc[k, "AP50_Lamp"] > 0]
_pos_par = int(_m3f["par"].rank(ascending=False)[PROP])
_mejor_map = _m3["mAP50"].idxmax()

LECTURA_M3FD = (
    f"Lectura: la complementariedad de las dos clases queda a la vista en las modalidades "
    f"individuales — el infrarrojo alcanza {_n(_m3.loc['IR', 'AP50_People'])} en personas frente a "
    f"{_n(_m3.loc['IR', 'AP50_Lamp'])} en luces, y el visible presenta el patrón inverso "
    f"({_n(_m3.loc['VIS', 'AP50_People'])} y {_n(_m3.loc['VIS', 'AP50_Lamp'])}). "
    + (f"<b>{len(_rec_ambas)} de las {len(_m3f)} fusiones detectan objetos de ambas clases</b> en una "
       "sola imagen"
       # La frase "algo que el IR no logra" solo es cierta si el IR es practicamente ciego a
       # Lamp; con un detector bien entrenado el IR la detecta, peor pero no de forma nula.
       + (", con un AP en luces muy superior al del infrarrojo, que apenas las distingue. "
          if _m3.loc["IR", "AP50_Lamp"] < 0.10 else
          f", y todas mejoran el AP en luces del infrarrojo ({_n(_m3.loc['IR', 'AP50_Lamp'])}), "
          "que es su clase débil. ")
       if len(_rec_ambas) else "")
    + (f"En el promedio del par, <b>{len(_sup_amb)} de las {len(_m3f)} fusiones "
       f"{'supera' if len(_sup_amb) == 1 else 'superan'} a ambas modalidades</b> "
       f"({', '.join(LBL.get(k, k).split(' (')[0] for k in _sup_amb)}). "
       if _sup_amb else
       f"<b>Ninguna de las {len(_m3f)} fusiones supera a ambas modalidades</b> en el promedio del "
       f"par: el mejor valor de una fusión es {M3_MEJOR_PAR} "
       f"({LBL.get(M3_MEJOR, M3_MEJOR).split(' (')[0]}) frente a "
       f"{_n(_m3.loc['VIS', 'par'])} del visible. ")
    + f"La propuesta obtiene <b>{M3_PROP_PAR}</b> en el par (puesto {_pos_par} de {len(_m3f)} entre "
      f"las fusiones) y {M3_PROP_MAP} de mAP global. "
    + f"El mejor mAP global de las seis clases lo conserva "
      f"<b>{LBL.get(_mejor_map, _mejor_map).split(' (')[0]}</b> "
      f"({_n(_m3.loc[_mejor_map, 'mAP50'])}), por la abundancia de vehículos diurnos. "
    + "Los valores absolutos son moderados: subconjunto reducido y modelo nano.")

# Parrafo y pie de la figura cualitativa, tomados del JSON que emite
# make_figura_detecciones_m3fd.py: con otro test las escenas y los conteos cambian.
_djs = os.path.join(MR, "figura_detecciones_m3fd.json")
if os.path.exists(_djs):
    import json as _json
    _dd = _json.load(open(_djs, encoding="utf-8"))
    _e = {x["lado"]: x for x in _dd["escenas"]}
    _pa, _pb = _e.get("people"), _e.get("lamp")
    def _pl(n, sing, plur):
        return f"{n} {sing if n == 1 else plur}"

    _frases = []
    if _pa:
        _p = _pa["people"]
        _cmp = ("supera a ambas modalidades" if _p[PROP] > max(_p["VIS"], _p["IR"])
                else "queda entre ambas" if _p[PROP] > min(_p["VIS"], _p["IR"])
                else "no mejora a ninguna")
        _frases.append(
            f"en la escena superior ({_pa['escena']}) la fusión detecta "
            f"<b>{_pl(_p[PROP], 'persona', 'personas')}</b> frente a {_p['VIS']} del visible y "
            f"{_p['IR']} del infrarrojo, es decir que {_cmp}")
    if _pb:
        _l, _pp = _pb["lamp"], _pb["people"]
        _t = (f"en la inferior ({_pb['escena']}) el infrarrojo detecta "
              f"{_pl(_l['IR'], 'luz', 'luces')} y la fusión conserva <b>{_l[PROP]}</b>, "
              f"las mismas que el visible" if _l[PROP] == _l["VIS"] else
              f"en la inferior ({_pb['escena']}) el infrarrojo detecta "
              f"{_pl(_l['IR'], 'luz', 'luces')} y la fusión conserva <b>{_l[PROP]}</b>")
        # Solo se afirma que estan las dos clases si la fusion detecta objetos de ambas.
        if _l[PROP] > 0 and _pp[PROP] > 0:
            _t += (f", junto con {_pl(_pp[PROP], 'persona', 'personas')}: "
                   "<b>ambas clases en una sola imagen</b>")
        elif _pp[PROP] == 0 and _pp["VIS"] > 0:
            _t += (f"; en esa escena, en cambio, la fusión <b>pierde</b> "
                   + ("la persona" if _pp["VIS"] == 1 else f"las {_pp['VIS']} personas")
                   + " que sí detecta el visible")
        _frases.append(_t)
    PARRAFO_DETECCIONES = (
        "Dos escenas de la partición de prueba con las detecciones del modelo único dibujadas "
        "(personas en granate, luces en azul); se eligieron automáticamente entre las escenas cuya "
        "anotación contiene ambas clases, sin intervención manual. "
        + ("; ".join(_frases)[:1].upper() + "; ".join(_frases)[1:] + "."))
    PIE_DETECCIONES = (f"Detecciones del modelo único VIS+IR sobre las escenas "
                       f"{' y '.join(x['escena'] for x in _dd['escenas'])} de M3FD "
                       f"(conf ≥ {_n(_dd['conf'], 2)}).")
else:
    PARRAFO_DETECCIONES = (
        "Dos escenas de la partición de prueba con las detecciones del modelo único dibujadas "
        "(personas en granate, luces en azul), elegidas automáticamente entre las escenas cuya "
        "anotación contiene ambas clases complementarias.")
    PIE_DETECCIONES = "Detecciones del modelo único VIS+IR sobre dos escenas de M3FD."

# ------------------------------------------------- justificacion del peso m adoptado
# Cuatro criterios convergentes, cada uno de un CSV distinto: monotonia de la aptitud,
# energia del operador (equivalencia del realce), saturacion del recorte, y la tension con
# las metricas de evaluacion. Se derivan del dato para que la seccion no quede desactualizada.
_bm = pd.read_csv(os.path.join(MR, "barrido_metricas_vs_m.csv"))
_bm = _bm[_bm.operador == "propuesta"].sort_values("m").reset_index(drop=True)
_bm30 = _bm[_bm.m >= 0.30].reset_index(drop=True)
import numpy as _np

# La aptitud que se publica es la del enjambre (curva_aptitud_vs_m.csv), la misma que
# reportan la Tabla 1 de este informe, el libro y el deck: 1,7057 en r = 25, m = 0,30.
# barrido_metricas_vs_m.csv reconstruye Fo con el SSIM y el PSNR de evaluators.py y da
# 1,6870 sobre las MISMAS tres escenas: son dos implementaciones de la misma aptitud, y
# publicar la reconstruida hacia que este informe se contradijera consigo mismo.
_cv = pd.read_csv(os.path.join(MR, "curva_aptitud_vs_m.csv")).sort_values("m")
_cv["m"] = _cv["m"].round(4)
_bm30["m"] = _bm30["m"].round(4)
_cv30 = _cv[_cv.m >= 0.30].reset_index(drop=True)
_dif = _np.diff(_cv30["Fo_propuesta"].values)
M_CRECIENTES = int((_dif > 0).sum())
M_TRAMOS = len(_dif)
FO_M030 = float(_cv30["Fo_propuesta"].iloc[0])
FO_M200 = float(_cv30["Fo_propuesta"].iloc[-1])
FN_M030 = float(_bm30["F_nueve"].iloc[0])
FN_M200 = float(_bm30["F_nueve"].iloc[-1])
# la columna de aptitud de la tabla pasa a ser la del enjambre; el resto de las columnas
# (suma de las nueve, SSIM, SF) sigue siendo la del barrido determinista
_bm30 = _bm30.merge(_cv[["m", "Fo_propuesta"]], on="m", how="left")
assert _bm30["Fo_propuesta"].notna().all(), "hay un m del barrido que la curva no cubre"
_bm30["F_o"] = _bm30["Fo_propuesta"]

_en = pd.read_csv(os.path.join(MR, "aptitud_operador_energia.csv")).set_index("operador")
_i_clas = [i for i in _en.index if "clásico" in i or "clasico" in i][0]
_i_prop = [i for i in _en.index if "Propuesta" in i][0]
W_CLAS = float(_en.loc[_i_clas, "detalle_medio"])
W_PROP = float(_en.loc[_i_prop, "detalle_medio"])
GANANCIA = W_PROP / W_CLAS
M_EQUIV = 0.30 * GANANCIA                    # a que m del disco unico equivale nuestro 0,30
RANGO_LO, RANGO_HI = 0.30 / GANANCIA, 2.00 / GANANCIA   # el rango publicado, traducido
POS_EN_RANGO = 100.0 * (M_EQUIV - 0.30) / (2.00 - 0.30)

# ------------------------------------------------- el barrido del trabajo de referencia
# Las 125 corridas de Ortega y Espinoza (2025), extraidas de sus anexos por
# experiments/referencia_pso_ortega_espinoza.py. Sirven para delimitar a quien corresponde
# el m = 0,30: con el disco unico y la MISMA aptitud y el MISMO rango, su optimo es
# interior. El anclaje al piso es una propiedad del operador, no de la aptitud.
_ref = pd.read_csv(os.path.join(MR, "referencia_pso_ortega_espinoza.csv"))
REF_N = len(_ref)
N_CFG = len(grid)                    # las 25 configuraciones de enjambre de esta tesis
_ref_med = _ref.groupby("escena")["m"].median()
_ref_piso = _ref.groupby("escena")["m"].apply(lambda s: int((s - 0.30).abs().lt(5e-3).sum()))
REF_M_MED = f"{_ref.m.median():.3f}".replace(".", ",")
REF_M_MIN = f"{_ref.m.min():.3f}".replace(".", ",")
REF_M_MAX = f"{_ref.m.max():.3f}".replace(".", ",")
REF_M_MED_MIN = f"{_ref_med.min():.3f}".replace(".", ",")
REF_M_MED_MAX = f"{_ref_med.max():.3f}".replace(".", ",")
REF_PISO = int(_ref_piso.max())
REF_ESC_PISO = _ref_piso.idxmax()
REF_R25 = int((_ref.r == 25).sum())
REF_R1 = int((_ref.r == 1).sum())
REF_R25_PCT = f"{100 * REF_R25 / REF_N:.0f}"
# las afirmaciones del parrafo tienen que ser ciertas sobre el dato
assert _ref_piso.gt(0).sum() == 1, "ya no es una sola escena la que se ancla en el piso"
assert (_ref_med > 0.30).sum() == 4, "cambio el numero de escenas con optimo interior"
_fil_ref = "".join(
    f"<tr><td class='l'>{_e}</td>"
    + f"<td>{_ref_med[_e]:.3f}".replace(".", ",") + "</td>"
    + f"<td>{_ref.loc[_ref.escena == _e, 'm'].min():.3f}".replace(".", ",")
    + " – " + f"{_ref.loc[_ref.escena == _e, 'm'].max():.3f}".replace(".", ",") + "</td>"
    + f"<td>{_ref_piso[_e]} de 25</td>"
    + f"<td>{int(_ref.loc[_ref.escena == _e, 'r'].median())}</td></tr>"
    for _e in sorted(_ref_med.index))
TAB_REFERENCIA = ('<table class="chica"><thead><tr><th class="l">Escena</th>'
                  '<th>m mediana</th><th>m mínimo – máximo</th>'
                  '<th>corridas en el piso 0,30</th><th>r mediana</th>'
                  '</tr></thead><tbody>' + _fil_ref + '</tbody></table>')

# --------------------------------------------------- perfil del detector y cuadro de deteccion
# Las cifras de arquitectura, entorno y protocolo NO se citan de la documentacion de la
# biblioteca: las mide experiments/perfil_detector.py sobre los checkpoints entrenados de este
# trabajo y las lee de los args.yaml de cada corrida.
_det = json.load(open(os.path.join(MR, "detector_perfil.json"), encoding="utf-8"))
_dm = _det["modelos"]["m3fd"]
_hp = _det["hiperparametros"]["m3fd"]
_env = _det["entorno"]
_bl = _dm["bloques"]

YOLO_PARAMS = f"{_dm['parametros']:,}".replace(",", ".")
YOLO_GFLOPS = f"{_dm['gflops']:.1f}".replace(".", ",")
YOLO_MODULOS = _dm["modulos"]
YOLO_IMGSZ = _hp["imgsz"]
YOLO_EPOCAS = _hp["epochs"]
YOLO_PATIENCE = _hp["patience"]
YOLO_CLOSE_MOSAIC = _hp["close_mosaic"]
YOLO_UPSAMPLE = _bl["Upsample"]
YOLO_CONCAT = _bl["Concat"]
YOLO_COMPOSICION = (f"{_bl['Conv']} convoluciones, {_bl['C2f']} bloques C2f "
                    f"—con {_bl['Bottleneck']} cuellos de botella internos—, "
                    f"{_bl['SPPF']} agrupamiento piramidal SPPF, {_bl['Concat']} concatenaciones, "
                    f"{_bl['Upsample']} sobremuestreos y {_bl['Detect']} cabezal de detección "
                    f"con módulo DFL")
YOLO_ENTORNO = (f"Ultralytics {_env['ultralytics']} sobre PyTorch {_env['torch']}"
                + (f", en una {_env['gpu']}" if _env.get("gpu") else ", en CPU"))

_dd = _det["datos"]
LLVIP_TRAIN = f"{_dd['llvip_Propuesta_Novedosa'].get('train', 0):,}".replace(",", ".")
LLVIP_VAL = f"{_dd['llvip_Propuesta_Novedosa'].get('val', 0):,}".replace(",", ".")
M3FD_TRAIN = f"{_dd['m3fd_mixto'].get('train', 0):,}".replace(",", ".")
M3FD_VAL = f"{_dd['m3fd_mixto'].get('val', 0):,}".replace(",", ".")
M3FD_TEST = f"{_dd['m3fd_test_Propuesta_Novedosa'].get('val', 0):,}".replace(",", ".")
M3FD_COMP = f"{_dd['m3fd_comp_Propuesta_Novedosa'].get('val', 0):,}".replace(",", ".")
M3FD_CLASES = ", ".join(_dm["clases"])

# La tabla va en dos columnas de pares: con una sola, sus 24 filas desbordan a una pagina
# que queda casi vacia. Los valores se dejan LITERALES —con punto decimal— porque son los
# del archivo de configuracion y alguien puede querer copiarlos tal cual.
_pares_hp = [(_det["etiquetas_hiper"][k], _hp[k]) for k in _det["etiquetas_hiper"]
             if k in _hp and _hp[k] is not None]
_mitad = (len(_pares_hp) + 1) // 2
_fil_hp = "".join(
    "<tr>" + "".join(
        f"<td class='l'>{p[0]}</td><td>{p[1]}</td>" if p else "<td></td><td></td>"
        for p in (_pares_hp[i], _pares_hp[i + _mitad] if i + _mitad < len(_pares_hp) else None))
    + "</tr>" for i in range(_mitad))
TAB_YOLO_HIPER = ('<table class="chica"><thead><tr><th class="l">Parámetro</th><th>Valor</th>'
                  '<th class="l">Parámetro</th><th>Valor</th></tr></thead><tbody>'
                  + _fil_hp + '</tbody></table>')

# Cuadro comparativo de la prueba de deteccion: las dos pruebas y el conteo por escena en una
# sola tabla, que es lo que permite ver que ninguna entrada gana en todo.
_lld = pd.read_csv(os.path.join(MR, "detection_llvip_map.csv")).set_index("method")
_m3d = pd.read_csv(os.path.join(MR, "detection_m3fd_map.csv")).set_index("method")
_cpd = pd.read_csv(os.path.join(MR, "complementariedad_resumen.csv")).set_index("entrada")
_m3d["par"] = (_m3d.AP50_People + _m3d.AP50_Lamp) / 2
_ORD_DET = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
            "TopHat_Clasico", "Propuesta_Novedosa"]
_COLS_DET = [("LLVIP mAP@0,5", lambda k: _lld.loc[k, "mAP50"], 3),
             ("LLVIP mAP@0,5:0,95", lambda k: _lld.loc[k, "mAP50_95"], 3),
             ("M3FD mAP@0,5", lambda k: _m3d.loc[k, "mAP50"], 3),
             ("AP People", lambda k: _m3d.loc[k, "AP50_People"], 3),
             ("AP Lamp", lambda k: _m3d.loc[k, "AP50_Lamp"], 3),
             ("Promedio del par", lambda k: _m3d.loc[k, "par"], 3),
             ("Escenas con ambas clases", lambda k: _cpd.loc[k, "pct_ambas"], 1)]
_mejor_det = {nom: max(_ORD_DET, key=f) for nom, f, _ in _COLS_DET}
_fil_det = ""
for _k in _ORD_DET:
    _nom = LBL.get(_k, _k).split(" (")[0]
    _tds = ""
    for _nomc, _f, _nd in _COLS_DET:
        _v = f"{_f(_k):.{_nd}f}".replace(".", ",") + (" %" if "Escenas" in _nomc else "")
        _es = (_mejor_det[_nomc] == _k)
        _tds += f"<td>{'<b>' if _es else ''}{_v}{'</b>' if _es else ''}</td>"
    _fil_det += (f"<tr><td class='l'>{'<b>' if _k == PROP else ''}{_nom}"
                 f"{'</b>' if _k == PROP else ''}</td>{_tds}</tr>")
TAB_DETECCION = ('<table class="chica"><thead><tr><th class="l">Entrada</th>'
                 + "".join(f"<th>{c[0]}</th>" for c in _COLS_DET)
                 + '</tr></thead><tbody>' + _fil_det + '</tbody></table>')
DET_LIDERES = "; ".join(
    f"{_nomc}: {LBL.get(_mejor_det[_nomc], _mejor_det[_nomc]).split(' (')[0]}"
    for _nomc, _, _ in _COLS_DET)

# la comparativa cualitativa por metodo sobre una escena
# la columna escena es un identificador con ceros a la izquierda (00231): si se lee como
# numero, el pie de la figura contradice el rotulo que la propia figura lleva grabado
# el grafo del detector, leido del checkpoint por make_figura_arquitectura_yolo.py
_arq = json.load(open(os.path.join(MR, "arquitectura_yolo.json"), encoding="utf-8"))
_ac = {c["i"]: c for c in _arq["capas"]}
_adet = _arq["capas"][-1]
ARQ_CAPAS = len(_arq["capas"])
ARQ_IMGSZ = _arq["meta"]["imgsz"]
ARQ_CKPT = _arq["meta"]["checkpoint"]
ARQ_PARAMS = f"{_arq['meta']['parametros']:,}".replace(",", ".")
ARQ_RES_MIN = min(c["res"] for c in _arq["capas"] if c["i"] <= 9)
ARQ_TAPS = ", ".join(str(i) for i in (4, 6, 9))
ARQ_SRC_TD = " y ".join(str(_ac[i]["from"][1]) for i in (11, 14))
ARQ_SRC_BU = " y ".join(str(_ac[i]["from"][1]) for i in (17, 20))
ARQ_SALIDAS = ", ".join(str(i) for i in _adet["from"])

_dme = pd.read_csv(os.path.join(MR, "detecciones_metodos_escena.csv"), dtype={"escena": str})
# Cuatro escenas elegidas por una regla declarada que incluye el caso ADVERSO a la propuesta,
# y diez entradas: las nueve del benchmark mas la metodologia de la referencia, que es su
# operador de disco con el (r, m) que su propio PSO halla y NO el comparativo «Top-Hat
# clasico», que corre con la parametrizacion manual r = 5, m = 1.
DME_ESCENAS = list(dict.fromkeys(_dme.escena))
DME_N_ESC = len(DME_ESCENAS)
DME_N_ENT = _dme.entrada.nunique()
DME_CRITERIO = {e: _dme[_dme.escena == e].criterio.iloc[0] for e in DME_ESCENAS}
DME_GT = {e: (int(_dme[_dme.escena == e].people_gt.iloc[0]),
              int(_dme[_dme.escena == e].lamp_gt.iloc[0])) for e in DME_ESCENAS}
_ORD_DME = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
            "TopHat_Clasico", "Ref_PSO", "Propuesta_Novedosa"]
_ET_DME = {k: _dme[_dme.entrada == k].etiqueta.iloc[0] for k in _ORD_DME if (_dme.entrada == k).any()}
_fil_dme = ""
for _k in _ORD_DME:
    _g = _dme[_dme.entrada == _k]
    if not len(_g):
        continue
    _dest = _k in ("Ref_PSO", "Propuesta_Novedosa")
    _tds = ""
    for _e in DME_ESCENAS:
        _r = _g[_g.escena == _e]
        _tds += (f"<td>{int(_r.people_detectadas.iloc[0])} · {int(_r.lamp_detectadas.iloc[0])}</td>"
                 if len(_r) else "<td>—</td>")
    _nom = _ET_DME[_k].split(" (")[0]
    _fil_dme += (f"<tr><td class='l'>{'<b>' if _dest else ''}{_nom}{'</b>' if _dest else ''}</td>"
                 f"{_tds}</tr>")
_cab_dme = "".join(f"<th>{_e}<br>({DME_GT[_e][0]} · {DME_GT[_e][1]})</th>" for _e in DME_ESCENAS)
TAB_DME = ('<table class="chica"><thead><tr><th class="l">Entrada</th>' + _cab_dme
           + '</tr></thead><tbody>' + _fil_dme + '</tbody></table>')
# cuantas entradas sobredetectan luces, por escena
_sobre = {_e: _dme[(_dme.escena == _e) & (_dme.lamp_detectadas > _dme.lamp_gt)]
          for _e in DME_ESCENAS}
DME_SOBRE_TXT = "; ".join(
    f"escena {_e}: " + (", ".join(f"{_r.etiqueta.split(' (')[0]} ({int(_r.lamp_detectadas)})"
                                  for _r in _sobre[_e].itertuples()) or "ninguna")
    for _e in DME_ESCENAS if len(_sobre[_e]))
# la escena publicada, que la seccion 14 tambien cita
DME_ESCENA = DME_ESCENAS[0]
DME_GT_P, DME_GT_L = DME_GT[DME_ESCENA]
_dme_pub = _dme[_dme.escena == DME_ESCENA]
DME_AMBAS = int(_dme_pub.detecta_ambas.sum())
DME_N = len(_dme_pub)
_dme_sobre = _dme_pub[_dme_pub.lamp_detectadas > _dme_pub.lamp_gt]
DME_SOBRE = ", ".join(f"{r.etiqueta.split(' (')[0]} ({int(r.lamp_detectadas)})"
                      for r in _dme_sobre.itertuples())
DME_N_SOBRE = len(_dme_sobre)

# ------------------------------------ estabilidad del barrido PSO: 20 repeticiones x 25
# Pedido del orientador. Hace falta un estudio aparte porque la aptitud es determinista y en
# el barrido publicado las semillas estaban fijadas por (n, T) y por el numero de iteracion:
# repetir una celda devolvia el mismo resultado bit a bit.
_rep = pd.read_csv(os.path.join(MR, "pso_repeticiones_propuesta.csv"))
REP_N = f"{len(_rep):,}".replace(",", ".")
REP_REPS = _rep.repeticion.nunique()
REP_EVALS = f"{int(_rep.evaluaciones.sum()):,}".replace(",", ".")
_rp = (_rep.m_opt - 0.30).abs() < 5e-4
REP_PISO = int(_rp.sum())
REP_PISO_PCT = f"{100 * _rp.mean():.1f}".replace(".", ",")
REP_R1_PCT = f"{100 * (_rep.r_opt == 1).mean():.1f}".replace(".", ",")
REP_R25_PCT = f"{100 * (_rep.r_opt == 25).mean():.1f}".replace(".", ",")
REP_OTROS_PCT = f"{100 * (~_rep.r_opt.isin([1, 25])).mean():.1f}".replace(".", ",")
_pn = _rep.groupby("n").apply(lambda g: 100 * (g.r_opt == 1).mean(), include_groups=False)
_pt = _rep.groupby("Tmax").apply(lambda g: 100 * (g.r_opt == 1).mean(), include_groups=False)
REP_PORN_MIN, REP_PORN_MAX = f"{_pn.min():.0f}", f"{_pn.max():.0f}"
REP_PORT_MIN, REP_PORT_MAX = f"{_pt.min():.0f}", f"{_pt.max():.0f}"
# El radio que la busqueda encuentra con MAS frecuencia no es el que maximiza la aptitud:
# r = 25 es un optimo local ancho que atrae mas inicializaciones, y r = 1 esta en el borde.
_gr = _rep.groupby("r_opt").agg(k=("Fo_opt", "size"), fo=("Fo_opt", "mean"))
_r_frec = int(_gr.k.idxmax())
_r_mejor = int(_rep.loc[_rep.Fo_opt.idxmax(), "r_opt"])
REP_R_FREC, REP_R_MEJOR = _r_frec, _r_mejor
REP_FO_FREC = f"{_gr.loc[_r_frec, 'fo']:.4f}".replace(".", ",")
REP_FO_MEJOR = f"{_gr.loc[_r_mejor, 'fo']:.4f}".replace(".", ",")
REP_DISOCIA = (_r_frec != _r_mejor)
# ------------------------------------------------ la errata de la ecuacion (29) del PSNR
# Su PSNR = 10 log10((M x N)^2 / MSE) lleva el numero de pixeles al cuadrado donde va la
# intensidad maxima al cuadrado. Esta tesis usa la definicion estandar, y eso hace que los
# valores de Fo no sean comparables con los publicados alli: hay que declararlo donde se
# define la aptitud, no solo en un comentario del codigo.
import math as _math

_ERR_M, _ERR_N, _ERR_MAX = 620, 450, 255.0
ERRATA_OFFSET = f"{10 * _math.log10((_ERR_M * _ERR_N) ** 2 / _ERR_MAX ** 2):.1f}".replace(".", ",")
ERRATA_PSNR_LO = f"{_ref.PSNR_n.min() * 100:.0f}"
ERRATA_PSNR_HI = f"{_ref.PSNR_n.max() * 100:.0f}"
ERRATA_SSIM = f"{_ref.SSIM_avg.median():.4f}".replace(".", ",")
ERRATA_FO_SUYO = (f"[{_ref.Fo.min():.4f}; {_ref.Fo.max():.4f}]".replace(".", ","))

# ------------------------------------------ por que sus corridas dispersan y las nuestras no
# El termino que debia penalizar la distorsion queda inerte —recorre 0,048 contra 0,400 del
# SSIM—, de modo que su criterio efectivo es SSIM + entropia. Los dos tienen tendencias
# opuestas en m, y por lo tanto un maximo INTERIOR: de ahi la dispersion. En la nuestra el
# optimo cae en el borde del intervalo y el borde actua como atractor.
_rec = {'SSIM_avg': _ref.SSIM_avg.max() - _ref.SSIM_avg.min(),
        'E_n': _ref.E_n.max() - _ref.E_n.min(),
        'PSNR_n': _ref.PSNR_n.max() - _ref.PSNR_n.min()}
_rtot = sum(_rec.values())
REF_REC = {k: (f"{v:.4f}".replace(".", ","), f"{100 * v / _rtot:.1f}".replace(".", ","))
           for k, v in _rec.items()}
_fil_rec = "".join(
    f"<tr><td class='l'>{_nom}</td><td>{REF_REC[_k][0]}</td><td>{REF_REC[_k][1]} %</td></tr>"
    for _k, _nom in (('SSIM_avg', 'SSIM<sub>avg</sub> (fidelidad)'),
                     ('E_n', 'E<sub>n</sub> (información)'),
                     ('PSNR_n', 'PSNR<sub>n</sub> (distorsión)')))
TAB_REF_RECORRIDO = ('<table class="chica"><thead><tr><th class="l">Término de su aptitud</th>'
                     '<th>Recorrido en sus 125 corridas</th><th>Aporte a la variación</th>'
                     '</tr></thead><tbody>' + _fil_rec + '</tbody></table>')

# --------------------------------------------------- el optimo exacto, por enumeracion
_oe = pd.read_csv(os.path.join(MR, "optimo_exacto_fo.csv"))
_oe_pub = _oe[_oe.m >= 0.30 - 1e-9]
_glob = _oe.loc[_oe.Fo.idxmax()]
_mpub = _oe_pub.loc[_oe_pub.Fo.idxmax()]
_mejor_libre = _oe.loc[_oe.groupby("r").Fo.idxmax()].sort_values("Fo", ascending=False)
_mejor_pub = _oe_pub.loc[_oe_pub.groupby("r").Fo.idxmax()].sort_values("Fo", ascending=False)
OE_N = f"{len(_oe):,}".replace(",", ".")
OE_PASOS = _oe.m.nunique()
OE_R_LIBRE, OE_M_LIBRE = int(_glob.r), f"{_glob.m:.3f}".replace(".", ",")
OE_FO_LIBRE = f"{_glob.Fo:.4f}".replace(".", ",")
OE_R_PUB, OE_M_PUB = int(_mpub.r), f"{_mpub.m:.2f}".replace(".", ",")
OE_FO_PUB = f"{_mpub.Fo:.4f}".replace(".", ",")
OE_COSTO = f"{_glob.Fo - _mpub.Fo:.4f}".replace(".", ",")
OE_PEOR_LIBRE = int(_mejor_libre.iloc[-1].r)
OE_FO_PEOR_LIBRE = f"{_mejor_libre.iloc[-1].Fo:.4f}".replace(".", ",")
OE_PISO_SIEMPRE = bool((_mejor_pub.m <= 0.30 + 1e-9).all())
_hall = (_rep.Fo_opt - _mpub.Fo).abs() < 5e-4
OE_HALLADO = int(_hall.sum())
OE_HALLADO_PCT = f"{100 * _hall.mean():.1f}".replace(".", ",")
OE_SUPERAN = int((_rep.Fo_opt > _mpub.Fo + 5e-4).sum())
# el rango de NUESTRA aptitud dentro del intervalo publicado, para el contraste de la errata
ERRATA_FO_NUESTRO = (f"[{_oe_pub.Fo.min():.4f}; {_oe_pub.Fo.max():.4f}]".replace(".", ","))

# ---------------------------- el mismo barrido con el peso libre, para contrastar los rangos
# El barrido determinista dice donde esta el optimo; esto comprueba si la busqueda lo
# encuentra cuando el rango no lo empuja contra la pared. Unico cambio: el piso del peso.
_lib = pd.read_csv(os.path.join(MR, "pso_repeticiones_propuesta_libre.csv"))
LIB_N = f"{len(_lib):,}".replace(",", ".")
LIB_REPS = _lib.repeticion.nunique()
LIB_PISO = f"{_lib.m_opt.min():.2f}".replace(".", ",")
_lp = (_lib.m_opt - _lib.m_opt.min()).abs() < 5e-4
LIB_PISO_N = int(_lp.sum())
LIB_PISO_PCT = f"{100 * _lp.mean():.1f}".replace(".", ",")
LIB_M_MED = f"{_lib.m_opt.median():.4f}".replace(".", ",")
LIB_R25_PCT = f"{100 * (_lib.r_opt == 25).mean():.1f}".replace(".", ",")
LIB_R1_PCT = f"{100 * (_lib.r_opt == 1).mean():.1f}".replace(".", ",")
_lib_hall = (_lib.Fo_opt - _glob.Fo).abs() < 5e-4
# el contraste tiene que ser cierto para que el parrafo se sostenga
assert (_lib.r_opt == 25).mean() > (_rep.r_opt == 25).mean(), \
    "con el peso libre la busqueda ya no se concentra mas en r = 25: revisar el parrafo"
_FILAS_DOS = [
    ("Piso del peso m", "0,30 (rango publicado)", f"{LIB_PISO} (libre)"),
    ("Mediana de m*", f"{_rep.m_opt.median():.4f}".replace(".", ","), LIB_M_MED),
    ("Corridas en el piso del peso", f"{REP_PISO_PCT} %", f"{LIB_PISO_PCT} %"),
    ("Corridas con r* = 25", f"{REP_R25_PCT} %", f"{LIB_R25_PCT} %"),
    ("Corridas con r* = 1", f"{REP_R1_PCT} %", f"{LIB_R1_PCT} %"),
    ("Radios distintos hallados", f"{_rep.r_opt.nunique()} de 25", f"{_lib.r_opt.nunique()} de 25"),
    ("Que alcanzan su propio óptimo", f"{OE_HALLADO_PCT} %",
     f"{100 * _lib_hall.mean():.1f}".replace(".", ",") + " %"),
    ("F<sub>o</sub> máxima alcanzada", f"{_rep.Fo_opt.max():.4f}".replace(".", ","),
     f"{_lib.Fo_opt.max():.4f}".replace(".", ",")),
]
TAB_DOS_RANGOS = ('<table class="chica"><thead><tr><th class="l">Criterio</th>'
                  '<th>m &isin; [0,30; 2,00]</th><th>m libre</th></tr></thead><tbody>'
                  + "".join(f"<tr><td class='l'>{a}</td><td>{b}</td><td>{c}</td></tr>"
                            for a, b, c in _FILAS_DOS) + '</tbody></table>')


# ------------------- el mismo experimento IMAGEN POR IMAGEN, comparable con el de la referencia
# El estudio de estabilidad de arriba optimiza sobre las tres imagenes de list_pairs()[::7] y
# repite la semilla veinte veces, de modo que mide dispersion ENTRE SEMILLAS. La referencia hace
# otra cosa: una corrida independiente POR ESCENA, 5 escenas x 25 configuraciones de enjambre. Para
# contrastar los dos trabajos sin comparar peras con manzanas hace falta el barrido por imagen, que
# tiene la misma estructura: 20 imagenes x 25 configuraciones.
#
# Lo que la tabla muestra es que con el MISMO rango el disco unico encuentra pesos interiores y el
# banco de cinco se clava en el piso; y que al bajar el piso el banco se comporta como el disco.
# O sea que la diferencia de comportamiento no esta en la busqueda sino en donde cae el optimo de
# cada operador respecto del intervalo heredado.
_ppi = pd.read_csv(os.path.join(MR, "pso_por_imagen.csv"))
_ppl = pd.read_csv(os.path.join(MR, "pso_por_imagen_libre.csv"))

# La tabla compara los dos barridos columna contra columna, de modo que TIENEN que correrse sobre
# el mismo corpus. Cuando se escribio este apartado no era asi: al barrido del piso bajado le
# faltaba Triclobs_Kaptein_1123 —el par que sustituyo al corrupto Athena_heather_IR_hei_vis— porque
# se habia corrido antes de la sustitucion, sobre el corpus de 19 pares. Publicar una comparacion
# con una columna de otro corpus es exactamente el defecto que este proyecto viene persiguiendo, y
# desde el texto no se ve: las dos columnas parecen homologas. El assert lo hace visible.
_falta = sorted(set(_ppi.imagen) - set(_ppl.imagen))
_sobra = sorted(set(_ppl.imagen) - set(_ppi.imagen))
assert not _falta and not _sobra, (
    "los dos barridos por imagen no cubren el mismo corpus, asi que la Tabla 3f compararia "
    f"columnas de corpus distintos. Falta(n) en el de piso bajado: {_falta}. Sobra(n): {_sobra}. "
    "Correr:  .venv\\Scripts\\python.exe -X utf8 experiments/pso_por_imagen.py "
    "--m-min 0.01 --salida pso_por_imagen_libre.csv")


def _perfil(tab, col_unidad, col_r, col_m, piso):
    """Resume un barrido por unidad: cuanto dispersa el peso y donde cae el radio."""
    en_piso = (tab[col_m] - piso).abs() < 5e-4
    return {
        'corridas': len(tab),
        'unidades': tab[col_unidad].nunique(),
        'piso': f"{piso:.2f}".replace(".", ","),
        'm_med': f"{tab[col_m].median():.4f}".replace(".", ","),
        'm_rango': (f"[{tab[col_m].min():.3f}; {tab[col_m].max():.3f}]".replace(".", ",")),
        'piso_pct': f"{100 * en_piso.mean():.1f}".replace(".", ","),
        'r_moda': int(tab[col_r].mode().iloc[0]),
        'r25_pct': f"{100 * (tab[col_r] == 25).mean():.1f}".replace(".", ","),
    }


_P_REF = _perfil(_ref, 'escena', 'r', 'm', 0.30)
_P_NUE = _perfil(_ppi, 'imagen', 'r', 'm', 0.30)
_P_LIB = _perfil(_ppl, 'imagen', 'r', 'm', float(_ppl.m.min()))

# El argumento del apartado solo se sostiene si el banco se clava en el piso mucho mas que el
# disco, y si al liberar el piso el radio modal pasa a r = 25 como en la referencia.
assert float(_P_NUE['piso_pct'].replace(",", ".")) > float(_P_REF['piso_pct'].replace(",", ".")), \
    "el banco no se ancla al piso mas que el disco: el apartado de la comparacion por imagen cae"
assert _P_LIB['r_moda'] == _P_REF['r_moda'] == 25, \
    "con el peso libre el radio modal ya no coincide con el de la referencia: revisar el apartado"

_FILAS_IMG = [
    ("Operador", "Disco único", "Banco de 5 elementos", "Banco de 5 elementos"),
    ("Unidad optimizada", f"{_P_REF['unidades']} escenas", f"{_P_NUE['unidades']} imágenes",
     f"{_P_LIB['unidades']} imágenes"),
    ("Corridas", f"{_P_REF['corridas']}", f"{_P_NUE['corridas']}", f"{_P_LIB['corridas']}"),
    ("Piso del rango de m", "0,30", "0,30", f"<b>{_P_LIB['piso']}</b>"),
    ("Mediana de m*", _P_REF['m_med'], f"<b>{_P_NUE['m_med']}</b>", _P_LIB['m_med']),
    ("Recorrido de m*", _P_REF['m_rango'], _P_NUE['m_rango'], _P_LIB['m_rango']),
    ("Corridas en el piso", f"{_P_REF['piso_pct']} %", f"<b>{_P_NUE['piso_pct']} %</b>",
     f"{_P_LIB['piso_pct']} %"),
    ("Radio modal", f"r = {_P_REF['r_moda']}", f"r = {_P_NUE['r_moda']}",
     f"<b>r = {_P_LIB['r_moda']}</b>"),
    ("Corridas con r* = 25", f"{_P_REF['r25_pct']} %", f"{_P_NUE['r25_pct']} %",
     f"<b>{_P_LIB['r25_pct']} %</b>"),
]
TAB_POR_IMAGEN = (
    '<table class="chica"><thead><tr><th class="l">Criterio</th>'
    '<th>Referencia<br>(su rango)</th><th>Esta tesis<br>(su rango)</th>'
    '<th>Esta tesis<br>(piso bajado)</th></tr></thead><tbody>'
    + "".join(f"<tr><td class='l'>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>"
              for a, b, c, d in _FILAS_IMG) + '</tbody></table>')

# La razon fisica: cuanta energia de detalle extrae cada operador, y por tanto que peso necesita
# cada uno para inyectar el mismo realce.
_GAN = float(_en.loc['Propuesta · W_opt = líneas + disco (r=25)', 'ganancia_vs_clasico'])
GANANCIA_BANCO = f"{_GAN:.2f}".replace(".", ",")
REF_M_EQUIV = f"{_ref.m.median() / _GAN:.3f}".replace(".", ",")


# --------------------------------- las 500 corridas, una por una, en una sola matriz
# El trabajo de referencia publica sus 125 corridas en anexos; este publica las 500 en una
# matriz de 25 configuraciones x 20 repeticiones, de modo que cada celda es una corrida y el
# lector puede contarlas. Se muestra el radio hallado, que es lo que varia; el peso es 0,30
# en todas menos una, que se identifica al pie.
def _matriz_corridas(tab, campo, fmt=lambda v: f'{int(v)}'):
    reps = sorted(tab.repeticion.unique())
    piv = tab.pivot_table(index=['n', 'Tmax'], columns='repeticion', values=campo,
                          aggfunc='first')
    cab = ('<tr><th>n</th><th>T</th>'
           + "".join(f'<th>{r + 1}</th>' for r in reps) + '</tr>')
    filas = ""
    for (n_, t_), fila in piv.iterrows():
        celdas = "".join(f'<td>{fmt(fila[r])}</td>' for r in reps)
        filas += f'<tr><td>{int(n_)}</td><td>{int(t_)}</td>{celdas}</tr>'
    return (f'<table class="anexo"><thead>{cab}</thead><tbody>{filas}</tbody></table>')


TAB_500_RADIO = _matriz_corridas(_rep, 'r_opt')
_fuera_piso = _rep[(_rep.m_opt - 0.30).abs() >= 5e-4]
CORRIDAS_EXCEPCION = ("; ".join(
    f"repetición {int(r.repeticion) + 1}, n = {int(r.n)}, T = {int(r.Tmax)} "
    f"(m* = {r.m_opt:.4f}".replace(".", ",") + ")"
    for r in _fuera_piso.itertuples()) or "ninguna")
CORRIDAS_TOTAL = f"{len(_rep):,}".replace(",", ".")
CORRIDAS_EVALS = f"{int(_rep.evaluaciones.sum()):,}".replace(",", ".")
CORRIDAS_HORAS = f"{_rep.segundos.sum() / 3600:.2f}".replace(".", ",")
_fil_oe = "".join(
    f"<tr><td>{int(_r.r)}</td>"
    + f"<td>{_mejor_libre[_mejor_libre.r == _r.r].m.iloc[0]:.2f}".replace(".", ",") + "</td>"
    + f"<td>{_mejor_libre[_mejor_libre.r == _r.r].Fo.iloc[0]:.4f}".replace(".", ",") + "</td>"
    + f"<td>{_mejor_pub[_mejor_pub.r == _r.r].Fo.iloc[0]:.4f}".replace(".", ",") + "</td></tr>"
    for _r in _mejor_libre.head(4).itertuples())
_fil_oe += "<tr><td colspan='4'>…</td></tr>"
_fil_oe += "".join(
    f"<tr><td>{int(_r.r)}</td>"
    + f"<td>{_mejor_libre[_mejor_libre.r == _r.r].m.iloc[0]:.2f}".replace(".", ",") + "</td>"
    + f"<td>{_mejor_libre[_mejor_libre.r == _r.r].Fo.iloc[0]:.4f}".replace(".", ",") + "</td>"
    + f"<td>{_mejor_pub[_mejor_pub.r == _r.r].Fo.iloc[0]:.4f}".replace(".", ",") + "</td></tr>"
    for _r in _mejor_libre.tail(3).itertuples())
TAB_OPTIMO_EXACTO = ('<table class="chica"><thead><tr><th>Radio r</th>'
                     '<th>Mejor m sin restringir</th><th>F<sub>o</sub> con m libre</th>'
                     '<th>F<sub>o</sub> con m &isin; [0,30; 2,00]</th>'
                     '</tr></thead><tbody>' + _fil_oe + '</tbody></table>')

# la dispersion por configuracion de las 500 corridas, para mostrarlas en el informe
_disp = _rep.groupby(["n", "Tmax"]).agg(
    med=("Fo_opt", "mean"), mn=("Fo_opt", "min"), mx=("Fo_opt", "max"),
    r1=("r_opt", lambda s: 100 * (s == 1).mean()),
    piso=("m_opt", lambda s: 100 * ((s - 0.30).abs() < 5e-4).mean())).reset_index()
_fil_disp = "".join(
    f"<tr><td>{int(_r.n)}</td><td>{int(_r.Tmax)}</td>"
    + f"<td>{_r.med:.4f}".replace(".", ",") + "</td>"
    + f"<td>{_r.mn:.4f}".replace(".", ",") + "</td>"
    + f"<td>{_r.mx:.4f}".replace(".", ",") + "</td>"
    + f"<td>{_r.r1:.0f} %</td><td>{_r.piso:.0f} %</td></tr>"
    for _r in _disp.itertuples())
TAB_DISPERSION = ('<table class="chica"><thead><tr><th>Partículas</th><th>Iteraciones</th>'
                  '<th>F<sub>o</sub> media</th><th>F<sub>o</sub> mínima</th>'
                  '<th>F<sub>o</sub> máxima</th><th>Con r* = 1</th><th>Con m* = 0,30</th>'
                  '</tr></thead><tbody>' + _fil_disp + '</tbody></table>')

_bm = _rep.groupby(["n", "Tmax"]).Fo_opt.mean()
REP_BANDA = f"{_bm.max() - _bm.min():.4f}".replace(".", ",")
# El veredicto sobre el peso se DERIVA del dato en lugar de estar escrito: si algun dia
# alguna corrida deja de anclarse en el piso, el informe lo dice en lugar de publicar la
# afirmacion al reves.
if _rp.all():
    REP_VEREDICTO_PESO = ("y es el único valor observado en todo el estudio. El anclaje al piso "
                          "del rango <b>no depende de la semilla</b>")
else:
    _f = _rep[~_rp].sort_values("Fo_opt")
    _n_f = len(_f)
    _peor = _f.iloc[0]
    _fallan_abajo = bool((_f.Fo_opt < _rep.Fo_opt.max()).all())
    _cual = ("la corrida restante" if _n_f == 1 else f"las {_n_f} corridas restantes")
    _v = ("no lo alcanza" if _n_f == 1 else "no lo alcanzan")
    REP_VEREDICTO_PESO = (
        f"y {_cual} {_v}: " + ("es" if _n_f == 1 else "son") + " de las configuraciones más "
        f"pobres del barrido —la peor, {int(_peor.n)} partículas por {int(_peor.Tmax)} iteraciones, "
        f"apenas {int(_peor.evaluaciones)} evaluaciones— y su aptitud ("
        + f"{_peor.Fo_opt:.4f}".replace(".", ",") + ") es la más baja de todo el estudio"
        + (", de modo que se trata de una <b>falla de convergencia</b> del enjambre y no de un óptimo "
           "alternativo: el piso sigue siendo el máximo que la monotonía de la aptitud determina"
           if _fallan_abajo else ""))
    print(f"AVISO: {_n_f} corridas con m* fuera del piso (la peor Fo = {_peor.Fo_opt:.4f})")
_fil_rr = "".join(
    f"<tr><td>{int(_r)}</td><td>{int(_k)}</td>"
    + f"<td>{100 * _k / len(_rep):.1f}".replace(".", ",") + " %</td>"
    + f"<td>{_rep[_rep.r_opt == _r].Fo_opt.mean():.4f}".replace(".", ",") + "</td></tr>"
    for _r, _k in _rep.r_opt.value_counts().sort_index().items())
TAB_REP_RADIO = ('<table class="chica"><thead><tr><th>Radio óptimo r*</th><th>Corridas</th>'
                 '<th>% del total</th><th>F<sub>o</sub> media</th></tr></thead><tbody>'
                 + _fil_rr + '</tbody></table>')

_sat = pd.read_csv(os.path.join(MR, "saturacion_vs_m.csv"))
def _satm(m):
    f = _sat[_np.isclose(_sat.m, m)]
    return float(f.pct_saturado_medio.iloc[0]) if len(f) else float("nan")
SAT_030, SAT_100, SAT_200 = _satm(0.30), _satm(1.00), _satm(2.00)
SAT_VECES = SAT_100 / SAT_030

# Se muestran los pesos representativos, no los once medidos: la tabla completa esta en
# saturacion_vs_m.csv y una tabla mas larga desborda la pagina.
_SAT_MOSTRAR = [0.10, 0.30, 0.50, 1.00, 1.50, 2.00]
_sat_v = _sat[_sat.m.isin(_SAT_MOSTRAR)]
_fil_sat = "".join(
    f"<tr><td>{r.m:.2f}".replace(".", ",") + "</td>"
    f"<td>{('<b>' if _np.isclose(r.m, 0.30) else '')}"
    + f"{r.pct_saturado_medio:.2f}".replace(".", ",") + " %"
    + f"{('</b>' if _np.isclose(r.m, 0.30) else '')}</td>"
    f"<td>{r.pct_bajo_cero:.2f}".replace(".", ",") + " %</td>"
    f"<td>{r.pct_sobre_uno:.2f}".replace(".", ",") + " %</td></tr>"
    for r in _sat_v.itertuples())
TAB_SATURACION = ('<table class="chica"><thead><tr><th>Peso m</th>'
                  '<th>Píxeles saturados</th><th>Por debajo de 0</th><th>Por encima de 1</th>'
                  '</tr></thead><tbody>' + _fil_sat + '</tbody></table>')

_fil_ten = "".join(
    f"<tr><td>{r.m:.2f}".replace(".", ",") + "</td>"
    + "".join(f"<td>{v}</td>" for v in (
        f"{r.F_o:.4f}".replace(".", ","), f"{r.F_nueve:.3f}".replace(".", ","),
        f"{r.SSIM:.4f}".replace(".", ","), f"{r.SF:.2f}".replace(".", ",")))
    + "</tr>"
    for r in _bm30[_bm30.m.isin([0.30, 0.50, 0.75, 1.00, 1.50, 2.00])].itertuples())
TAB_TENSION = ('<table class="chica"><thead><tr><th>Peso m</th><th>F<sub>o</sub> (aptitud)</th>'
               '<th>Suma de las nueve</th><th>SSIM</th><th>SF</th>'
               '</tr></thead><tbody>' + _fil_ten + '</tbody></table>')

# ------------------------------------------- complementariedad por escena (objetivo declarado)
# El mAP promediado no mide el objetivo del trabajo: lo mide el conteo por escena de cuantas
# veces la imagen fusionada recupera las DOS clases complementarias a la vez.
_cp = pd.read_csv(os.path.join(MR, "complementariedad_por_escena.csv"))
_cr = pd.read_csv(os.path.join(MR, "complementariedad_resumen.csv")).set_index("entrada")
_cpv = _cp.pivot(index="escena", columns="entrada", values="recupera_ambas")
CP_N = len(_cpv)
CP_CRIT = int(_cr["criticas"].iloc[0])
_CP_ORDEN = _cr.sort_values("recupera_ambas", ascending=False).index.tolist()
_CP_LBL = {**LBL, "VIS": "VIS solo", "IR": "IR solo",
           "TopHat_Clasico": "Top-Hat clásico", PROP: "PROPUESTA"}

from scipy.stats import binomtest as _bt
def _mcnemar(f, mod):
    b = int(((_cpv[f] == 1) & (_cpv[mod] == 0)).sum())
    c = int(((_cpv[f] == 0) & (_cpv[mod] == 1)).sum())
    p = _bt(b, b + c, 0.5).pvalue if (b + c) else 1.0
    return b, c, p

_fil_cp = []
for _k in _CP_ORDEN:
    _r = _cr.loc[_k]
    _es = (_k == PROP)
    _pct = f"{_r.pct_ambas:.1f}".replace(".", ",")
    if _k in ("VIS", "IR"):
        _cmp = "<td>—</td><td>—</td>"
    else:
        _b, _c, _p = _mcnemar(_k, "VIS")
        _cmp = (f"<td>{_b} / {_c}</td>"
                f"<td>{('<b>' if _p < 0.05 else '')}{f'{_p:.3f}'.replace('.', ',')}"
                f"{('</b>' if _p < 0.05 else '')}</td>")
    _nom = _CP_LBL.get(_k, _k).split(" (")[0]
    _fil_cp.append(
        f"<tr><td class='l'>{'<b>' if _es else ''}{_nom}{'</b>' if _es else ''}</td>"
        f"<td>{int(_r.recupera_ambas)}</td><td>{_pct} %</td>"
        f"<td>{int(_r.resuelve_criticas)}</td>{_cmp}</tr>")
TAB_COMPL = ('<table class="chica"><thead><tr><th class="l">Entrada del detector</th>'
             f'<th>Recupera ambas<br>(de {CP_N})</th><th>%</th>'
             f'<th>Críticas resueltas<br>(de {CP_CRIT})</th>'
             '<th>vs VIS<br>gana / pierde</th><th>McNemar p</th>'
             '</tr></thead><tbody>' + "".join(_fil_cp) + '</tbody></table>')

CP_PROP = float(_cr.loc[PROP, "pct_ambas"])
CP_VIS = float(_cr.loc["VIS", "pct_ambas"])
CP_MEJOR = _CP_ORDEN[0]
CP_MEJOR_PCT = float(_cr.loc[CP_MEJOR, "pct_ambas"])
CP_PB, CP_PC, CP_PP = _mcnemar(PROP, "VIS")
CP_PROP_CRIT = int(_cr.loc[PROP, "resuelve_criticas"])
CP_MEJOR_CRIT = int(_cr.loc[CP_MEJOR, "resuelve_criticas"])

# --------------------------------------------------------- robustez: ajuste y ablacion
# Cifras del ajuste simetrico de los comparativos (run_ajuste_comparativos.py) y de la
# ablacion del banco (run_ablacion_banco.py). Se derivan del CSV: si se rehacen los
# experimentos, la seccion se actualiza sola.
_ajr = pd.read_csv(os.path.join(MR, "ajuste_comparativos_ranking.csv"), index_col=0)
_ajm = pd.read_csv(os.path.join(MR, "ajuste_comparativos_mejores.csv"))
_abl = pd.read_csv(os.path.join(MR, "ablacion_banco_resumen.csv"), index_col=0)

# Control negativo. El informe citaba «el segundo puesto entre ocho entradas» en dos lugares, a
# mano y de una corrida anterior: el control tiene hoy 14 entradas —los 7 metodos, la imagen base,
# 4 fusiones de ruido y 2 desenfoques— y el ruido de sigma = 0,20 queda TERCERO. Se deriva del CSV
# para que no vuelva a envejecer.
_cneg = pd.read_csv(os.path.join(MR, "control_negativo_ranking.csv")).set_index("brazo")
CN_ENTRADAS = len(_cneg)
_cn9 = _cneg["rango_9"].sort_values()          # menor rango = mejor
_RUIDO_ALTO = "ruido_0.20"
CN_POS_RUIDO = list(_cn9.index).index(_RUIDO_ALTO) + 1
CN_RANGO_RUIDO = f"{_cn9[_RUIDO_ALTO]:.3f}".replace(".", ",")
# cuantos de los seis comparativos quedan POR DETRAS del ruido (rango mayor)
_COMPAR = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet", "TopHat_Clasico"]
CN_COMPAR_DETRAS = int((_cneg.loc[_COMPAR, "rango_9"] > _cn9[_RUIDO_ALTO]).sum())
# y el ordinal en femenino que usa el texto («la 3.ª»)
CN_ORD_RUIDO = f"{CN_POS_RUIDO}.º"

_ESC = {"A_todos_por_defecto": "A. Cada método en su configuración estándar",
        "B_comparativos_ajustados": "B. Comparativos ajustados; propuesta fija en r = 25",
        "C_todos_ajustados": "C. Todos ajustados, incluida la propuesta",
        "D_comparativos_ajustados_17": "D. Como B, pero rankeando con las 17 métricas"}


def _pos(col):
    s_ = _ajr[col].sort_values()
    return list(s_.index).index(PROP) + 1, s_[PROP], s_.index[0], s_.iloc[0]


POS_A, VAL_A, LID_A, VLID_A = _pos("A_todos_por_defecto")
POS_B, VAL_B, LID_B, VLID_B = _pos("B_comparativos_ajustados")
POS_D, VAL_D, LID_D, VLID_D = _pos("D_comparativos_ajustados_17")
# los cinco del estado del arte, ya ajustados
_SOTA = ["RatioPiramide", "PiramideLaplace", "DWT", "DTCWT", "Curvelet"]
_sota_b = _ajr.loc[_SOTA, "B_comparativos_ajustados"].sort_values()
SOTA_MEJOR, SOTA_MEJOR_VAL = _sota_b.index[0], _sota_b.iloc[0]
# parametro elegido para cada metodo
_elg = _ajm[_ajm.elegida].set_index("metodo")["valor"].to_dict()
_dfl = _ajm[_ajm.por_defecto].set_index("metodo")["valor"].to_dict()
# control de peso igualado
_ctrl = pd.read_csv(os.path.join(MR, "control_tophat_igual_peso.csv"))

# Control de peso igualado, tal como lo calcula el libro (§5.8.4): dentro del benchmark de
# siete metodos se SUSTITUYE al Top-Hat clasico por su version con r = 25 y m = 0,30 —el
# mismo peso de la propuesta— y se recalculan los rangos intra-bloque con la formula de
# run_stats_analysis.py. Asi las cifras no quedan escritas a mano.
#
# La version anterior hacia dos cosas mal a la vez: partia del escenario B (comparativos
# ajustados) en lugar del benchmark, y AGREGABA el clasico a peso igualado como octavo brazo
# dejando tambien al clasico con m = 1 dentro del pool. El operador clasico competia asi dos
# veces y los siete rangos se diluian: de ahi salian el 3,961 y el 4,711, que no coinciden
# con ninguna tabla de este informe ni con el libro, el deck y el README, y un margen de
# 0,683 en lugar de 0,166.
_ctrl = pd.read_csv(os.path.join(MR, "control_tophat_igual_peso.csv"))
_NUEVE = ["EN", "SD", "FE", "MG", "MI_vis", "MI_ir", "SF", "SSIM", "PSNR"]
_am_ct = pd.read_csv(os.path.join(MR, "all_metrics.csv"))
_base_ct = (_am_ct[_am_ct.method != "TopHat_Clasico"][["image", "method"] + _NUEVE]
            .rename(columns={"image": "imagen", "method": "clave"}))
_comb = pd.concat([_base_ct, _ctrl[["imagen", "clave"] + _NUEVE]], ignore_index=True)
_rr = {}
for _m in _NUEVE:
    _p = _comb.pivot(index="imagen", columns="clave", values=_m)
    _rr[_m] = _p.rank(axis=1, ascending=(DIRECTION[_m] == "min") if isinstance(DIRECTION.get(_m), str)
                      else False, method="average").mean(axis=0)
_rc = pd.DataFrame(_rr).mean(axis=1)
assert "TopHat_Clasico" not in _rc.index, "el clasico quedo compitiendo dos veces"
assert len(_rc) == 7, f"el pool del control tiene {len(_rc)} brazos y deben ser siete"
CTRL_TH_M030 = _rc["TopHat_r25_m030"]
CTRL_PROP = _rc[PROP]
# El margen se calcula sobre los valores REDONDEADOS que se publican, para que la resta le
# cierre a quien la haga: 3,694 - 3,528 = 0,166. Sobre los rangos sin redondear da 0,167 y el
# lector encontraria una diferencia de un milesimo que no puede reproducir.
CTRL_VENTAJA = round(CTRL_TH_M030, 3) - round(CTRL_PROP, 3)
# el parrafo afirma que a peso igualado la propuesta conserva el primer lugar: si algun dia
# deja de ser cierto, el informe tiene que fallar y no publicarlo al reves
assert CTRL_PROP == _rc.min(), \
    f"a peso igualado la propuesta ya no encabeza el pool: {_rc.sort_values().to_dict()}"

# tabla de los cuatro escenarios
_fil = []
_ord_b = _ajr["A_todos_por_defecto"].sort_values().index
for _k in _ord_b:
    _nom = LBL.get(_k, _k).split(" (")[0]
    _tds = ""
    for _c in _ESC:
        _v = _ajr.loc[_k, _c]
        _es_lider = (_v == _ajr[_c].min())
        _txt = f"{_v:.3f}".replace(".", ",")
        _tds += f"<td>{'<b>' if _es_lider or _k == PROP else ''}{_txt}"                 f"{'</b>' if _es_lider or _k == PROP else ''}</td>"
    _par = f"{_elg.get(_k, '-')}" if _k in _elg else "-"
    _fil.append(f"<tr><td class='l'>{'<b>' if _k == PROP else ''}{_nom}"
                f"{'</b>' if _k == PROP else ''}</td><td>{_dfl.get(_k, '-')}</td>"
                f"<td>{_par}</td>{_tds}</tr>")
TAB_ESCENARIOS = ('<table class="chica"><thead><tr><th class="l">Método</th>'
                  '<th>Par. estándar</th><th>Par. ajustado</th>'
                  + "".join(f"<th>{c[0]}</th>" for c in _ESC)
                  + '</tr></thead><tbody>' + "".join(_fil) + '</tbody></table>')

# tabla de la ablacion
_ABL_LBL = {"base": "Sin operador — la imagen (VIS+IR)/2",
            "disco": "Solo el disco B_r (operador clásico, mismo r y m)",
            "lineas": "Solo el promedio de las cuatro líneas",
            "suma": "Disco + promedio de líneas (la propuesta)",
            "promedio": "Media de disco y líneas", "maximo": "Máximo entre disco y líneas"}
_fa = []
for _k in _abl.sort_values("rango_9").index:
    _es = (_k == "suma")
    _tds = "".join(f"<td>{('<b>' if _abl[c].min() == _abl.loc[_k, c] else '')}"
                   f"{_abl.loc[_k, c]:.3f}".replace(".", ",")
                   + f"{('</b>' if _abl[c].min() == _abl.loc[_k, c] else '')}</td>"
                   for c in ("rango_9", "rango_9_sin_FE", "rango_17"))
    _fa.append(f"<tr><td class='l'>{'<b>' if _es else ''}{_ABL_LBL.get(_k, _k)}"
               f"{'</b>' if _es else ''}</td>{_tds}</tr>")
TAB_ABLACION = ('<table class="chica"><thead><tr><th class="l">Brazo del operador</th>'
                '<th>9 métricas</th><th>8 sin FE</th><th>17 métricas</th>'
                '</tr></thead><tbody>' + "".join(_fa) + '</tbody></table>')

# ------------------------------------------------------------------ aptitud del barrido
# Los dos valores de F_o que se citan en la lectura del barrido se derivan del CSV y no se
# escriben a mano: al sustituir un par del corpus cambian las escenas sobre las que se
# optimiza (list_pairs()[::7]) y con ellas la aptitud.
_g = grid.copy()
_col_fo = "F_opt" if "F_opt" in _g.columns else "Fo_opt"
FO_MEJOR = f"{_g[_col_fo].max():.4f}".replace(".", ",")
_r_mejor = int(_g.loc[_g[_col_fo].idxmax(), "r_opt"])
_fo25 = _g.loc[_g["r_opt"] == 25, _col_fo]
FO_R25 = f"{_fo25.max():.4f}".replace(".", ",") if len(_fo25) else "-"
R_PREFERIDO = _r_mejor
N_R1 = int((_g["r_opt"] == 1).sum())
N_M_PISO = int((_g["m_opt"] == _g["m_opt"].min()).sum())

if LIBRE:
    LECTURA_PSO = (
        "Lectura: con el límite inferior del peso ampliado, el óptimo de F<sub>o</sub> deja de estar "
        "sobre el borde del intervalo y el barrido devuelve pesos bajos, del orden de "
        f"<b>m = {V['m']}</b>. El radio adoptado sigue siendo r = 25.")
    PARRAFO_RADIO = (
        "El radio se fija en r = 25 (elementos estructurantes de 51 píxeles), de modo que el operador "
        "aprovecha un vecindario amplio para capturar los objetivos térmicos completos. El peso bajo "
        f"({V['m']}) mantiene el realce suave: el producto del peso por la energía del operador es "
        "comparable al que el trabajo de referencia obtiene con m = 0,30 sobre un disco único, porque "
        "el banco de cinco respuestas inyecta unas 4,3 veces más energía de detalle. Estos "
        "hiperparámetros definen la configuración de la propuesta usada en todo el benchmark de esta "
        "variante.")
else:
    # Se acorta a proposito: las paginas siguientes desarrollan el peso, el barrido
    # determinista y el estudio de estabilidad, de modo que repetirlo aca desbordaba la pagina
    # y derramaba el parrafo entero a la siguiente.
    LECTURA_PSO = (
        "Lectura: las <b>25 configuraciones convergen al mismo peso, m* = 0,30</b>, el piso del rango "
        "publicado, porque los dos términos de fidelidad de F<sub>o</sub> dominan sobre la entropía y "
        "decrecen al aumentar el realce. <b>El radio, en cambio, no lo fija el PSO:</b> dentro de este "
        f"rango la aptitud prefiere r = {R_PREFERIDO} ({FO_MEJOR} frente a {FO_R25} en r = 25), de modo "
        "que <b>r = 25 es una decisión de diseño</b> tomada sobre las métricas de evaluación —cinco de "
        "las nueve la favorecen y las cuatro de fidelidad favorecen r = 1— y no el resultado de la "
        "optimización. Las páginas que siguen desarrollan las dos cosas: la justificación del peso, y "
        "con un barrido determinista y 500 corridas repetidas, el alcance exacto de esa preferencia.")
    PARRAFO_RADIO = (
        "El radio r = 25 (elementos estructurantes de 51 píxeles) permite que el operador aproveche un "
        "vecindario amplio para capturar los objetivos térmicos completos, y a igual peso supera a "
        "r = 1 en entropía, contraste, ganancia de entropía sobre las fuentes, gradiente medio y "
        "frecuencia espacial; cede, en cambio, en las cuatro métricas de fidelidad. Conviene precisar "
        "que r = 1 <b>no</b> desactiva el banco de elementos estructurantes: con r = 1 el disco es la "
        "cruz de 3×3 y las cuatro líneas orientadas son cuatro máscaras 3×3 distintas, de modo que el "
        "banco sigue operativo sobre un vecindario mínimo. El peso m = 0,30 es el que produce el "
        "barrido con la metodología de referencia y mantiene la saturación por debajo del 2 % de los "
        "píxeles. Estos hiperparámetros definen la configuración de la propuesta usada en todo el "
        "benchmark de esta variante.")

# ------------------------------------------------------------------ posicion por metrica
_NOM_MET = {"EN": "la entropía", "SD": "el contraste", "FE": "la ganancia de entropía sobre las fuentes",
            "MG": "el gradiente medio", "MI_vis": "la información mutua con el visible",
            "MI_ir": "la información mutua con el infrarrojo", "SF": "la frecuencia espacial",
            "SSIM": "la similitud estructural", "PSNR": "la relación señal-ruido"}
_POS = {k: int(means[k].rank(ascending=False)[PROP]) for k in METS}
_LID = [k for k in METS if _POS[k] == 1]
_SEG = [k for k in METS if _POS[k] == 2]
_CEDE = [k for k in METS if _POS[k] >= 5]

def _enum(ks, con_valor=True):
    """Enumera metricas en prosa, opcionalmente con su valor."""
    if not ks:
        return ""
    fmt = {"SF": ".2f", "PSNR": ".2f"}
    ps = [(f"{_NOM_MET[k]} ({k} {means.loc[PROP, k]:{fmt.get(k, '.3f')}})"
           if con_valor else _NOM_MET[k]) for k in ks]
    return ps[0] if len(ps) == 1 else ", ".join(ps[:-1]) + " y " + ps[-1]

# metricas donde la propuesta supera al Top-Hat clasico
_VS_TH = [k for k in METS if means.loc[PROP, k] > means.loc["TopHat_Clasico", k]]
_VS_TH_NO = [k for k in METS if means.loc[PROP, k] < means.loc["TopHat_Clasico", k]]

if _LID:
    LECTURA_BENCH = (f"Lectura: la propuesta <b>lidera {_enum(_LID)}</b> del benchmark"
                     + (f", y es segunda en {_enum(_SEG, False)}" if _SEG else "") + ". ")
else:
    LECTURA_BENCH = ("Lectura: en esta configuración la propuesta <b>no lidera ninguna de las nueve "
                     f"métricas</b>; su mejor posición es {min(_POS.values())}.ª "
                     f"({_enum([k for k in METS if _POS[k] == min(_POS.values())], False)}). ")
LECTURA_BENCH += (f"Cede, en cambio, en {_enum(_CEDE, False)}. " if _CEDE else "")
LECTURA_BENCH += (f"Frente al Top-Hat clásico —la referencia morfológica directa— mejora "
                  f"<b>{len(_VS_TH)} de las nueve métricas</b> y cede en {len(_VS_TH_NO)} "
                  f"({_enum(_VS_TH_NO, False)}). Advertencia metodológica: los dos operadores no "
                  "comparten (r, m) —el clásico usa r = 5, m = 1—, de modo que la diferencia refleja "
                  "conjuntamente el cambio de operador y el de hiperparámetros.")

# ------------------------------------------------------------------ graficas
charts = {}
AZUL = "#4472c4"; GRIS = "#a6a6a6"

# mejor aptitud F_o alcanzada segun el numero de particulas (Tmax=50)
fig, ax = plt.subplots(figsize=(7.2, 3.2))
_ns = [2, 4, 6, 8, 10]
_yb = [grid[(grid.n == n) & (grid.Tmax == 50)]["F_opt"].values[0] for n in _ns]
ax.plot(_ns, _yb, "-o", color=AZUL, lw=2, ms=7, mfc=AZUL, mec="white")
_im = int(np.argmax(_yb))
ax.scatter([_ns[_im]], [_yb[_im]], s=150, facecolor="none", edgecolor=AZUL, lw=1.6, zorder=4)
ax.set_xlabel("Número de partículas del enjambre (n)"); ax.set_ylabel("Mejor aptitud $F_o$")
ax.set_title("Mejor aptitud $F_o$ según el tamaño del enjambre (Tmax = 50)", fontsize=11)
ax.set_xticks(_ns)
charts["pso"] = fig_to_b64(fig)

# tabla 5x5 del barrido (F* por configuracion)
gbest_F = grid["F_opt"].max()
piv = grid.pivot(index="n", columns="Tmax", values="F_opt")
filas_grid = []
for n in [2, 4, 6, 8, 10]:
    tds = []
    for T in [10, 20, 30, 40, 50]:
        v = piv.loc[n, T]
        b = "<b>" if abs(v - gbest_F) < 5e-4 else ""
        tds.append(f"<td>{b}{v:.4f}{'</b>' if b else ''}</td>")
    filas_grid.append(f'<tr><td class="l"><b>n = {n}</b></td>{"".join(tds)}</tr>')
tabla_grid = ('<table class="chica"><tr><th class="l">Partículas \\ Iteraciones</th>'
              + "".join(f"<th>T = {T}</th>" for T in [10, 20, 30, 40, 50])
              + f'</tr>{"".join(filas_grid)}</table>')

key = ["EN", "FE", "SF", "SSIM"]
fig, axes = plt.subplots(1, 4, figsize=(12.0, 2.9))
for ax, mk in zip(axes, key):
    vals = [means.loc[m, mk] for m in ORDEN]
    cols = [AZUL if m == PROP else GRIS for m in ORDEN]
    ax.bar(range(len(ORDEN)), vals, color=cols, width=0.62)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=6.3)
    ax.set_title(f'{mk} (mayor mejor)', fontsize=9)
    ax.set_xticks(range(len(ORDEN)))
    ax.set_xticklabels([SHORT[m] for m in ORDEN], fontsize=6.5, rotation=30, ha="right")
    ax.margins(y=0.18)
fig.tight_layout()
charts["quality"] = fig_to_b64(fig)

rk = rankm["avg_rank"].sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6.6, 2.9))
cols = [AZUL if n == PROP else GRIS for n in rk.index]
ax.barh(range(len(rk)), rk.values, color=cols, height=0.62)
ax.set_yticks(range(len(rk)))
ax.set_yticklabels([LBL.get(n, n) for n in rk.index], fontsize=8)
for i, v in enumerate(rk.values):
    ax.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=7.5)
ax.set_xlabel("Ranking promedio en 9 métricas (menor = mejor)", fontsize=9)
ax.margins(x=0.12)
charts["ranking"] = fig_to_b64(fig)

# --- detección LLVIP: barras mAP por método ---
_dord = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
         "TopHat_Clasico", "Propuesta_Novedosa"]
_dshort = {"VIS": "VIS", "IR": "IR", "PiramideLaplace": "LP", "RatioPiramide": "RP",
           "DWT": "DWT", "DTCWT": "DTCWT", "Curvelet": "CVT", "TopHat_Clasico": "TH clás.",
           "Propuesta_Novedosa": "Propuesta"}
dd = det.loc[_dord]
fig, ax = plt.subplots(figsize=(7.4, 3.0))
x = np.arange(len(_dord)); w = 0.4
ax.bar(x - w/2, dd["mAP50"], w, label="mAP@0,5", color=AZUL)
ax.bar(x + w/2, dd["mAP50_95"], w, label="mAP@0,5:0,95", color=GRIS)
for xi, (a, b) in enumerate(zip(dd["mAP50"], dd["mAP50_95"])):
    ax.text(xi - w/2, a, f"{a:.2f}".replace(".", ","), ha="center", va="bottom", fontsize=6)
ax.set_xticks(x); ax.set_xticklabels([_dshort[m] for m in _dord], fontsize=7.5, rotation=25, ha="right")
ax.set_ylim(0, 1.05); ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.set_ylabel("mAP", fontsize=9)
charts["det"] = fig_to_b64(fig)

# wilcoxon: propuesta vs cada rival (tabla resumen)
wp = wilc[wilc["tophat"] == PROP].copy()
rivales_w = [m for m in ORDEN if m != PROP and m in set(wp["baseline"])]
wtab = {}
for _, r in wp.iterrows():
    d = DIRECTION[r["metric"]]
    sig = r["p_holm"] < 0.05
    mejor = (r["mean_tophat"] - r["mean_baseline"]) * d > 0
    wtab[(r["metric"], r["baseline"])] = "≈" if not sig else ("mejor" if mejor else "peor")
rows = []
for mk in METS:
    tds = "".join(f'<td>{wtab.get((mk, rv), "—")}</td>' for rv in rivales_w)
    rows.append(f'<tr><td class="l">{mk}</td>{tds}</tr>')
tabla_wilcoxon = ('<table class="chica"><tr><th class="l">Métrica</th>'
                  + "".join(f"<th>vs. {SHORT[r]}</th>" for r in rivales_w)
                  + f'</tr>{"".join(rows)}</table>')
w_mejor = sum(1 for v in wtab.values() if v == "mejor")
w_peor = sum(1 for v in wtab.values() if v == "peor")
w_emp = sum(1 for v in wtab.values() if v == "≈")
print("charts ok | propuesta mejor columnas:", n_best_prop,
      f"| wilcoxon {w_mejor}m/{w_peor}p/{w_emp}e")

# ------------------------------------------------------------------ formulas
F = {
 "dil_ero": r"\delta(f,b)(x,y)=\max_{(s,t)\in b} f(x+s,\,y+t) \qquad \varepsilon(f,b)(x,y)=\min_{(s,t)\in b} f(x+s,\,y+t)",
 "open_close": r"\gamma(f,b)=\delta(\varepsilon(f,b),\,b) \qquad \varphi(f,b)=\varepsilon(\delta(f,b),\,b)",
 "tophat": r"WTH(f,b)=f-\gamma(f,b) \qquad BTH(f,b)=\varphi(f,b)-f",
 "se_disco": r"B_r=\left\{(x,y)\in\mathbb{Z}^2 \,:\, x^2+y^2\leq r^2\right\}",
 "se_lineas": r"L_{r,\theta}\subset\mathbb{Z}^2,\quad \left|L_{r,\theta}\right|=2r+1,\qquad \theta\in\left\{0^\circ,\,45^\circ,\,90^\circ,\,135^\circ\right\}",
 "wth_theta": r"WTH_{\theta}(f)=f-\gamma\!\left(f,\,L_{r,\theta}\right),\qquad \theta\in\left\{0^\circ,45^\circ,90^\circ,135^\circ\right\}",
 "wth_lin4": r"WTH_{lin}(f)=\frac{1}{4}\left[\,WTH_{0^\circ}(f)+WTH_{45^\circ}(f)+WTH_{90^\circ}(f)+WTH_{135^\circ}(f)\,\right]",
 "bth_theta": r"BTH_{\theta}(f)=\varphi\!\left(f,\,L_{r,\theta}\right)-f,\qquad \theta\in\left\{0^\circ,45^\circ,90^\circ,135^\circ\right\}",
 "bth_lin4": r"BTH_{lin}(f)=\frac{1}{4}\left[\,BTH_{0^\circ}(f)+BTH_{45^\circ}(f)+BTH_{90^\circ}(f)+BTH_{135^\circ}(f)\,\right]",
 "wth_disc": r"WTH_{disco}(f)=f-\gamma\!\left(f,\,B_r\right) \qquad BTH_{disco}(f)=\varphi\!\left(f,\,B_r\right)-f",
 "wth_sum": r"WTH(f)=WTH_{lin}(f)+WTH_{disco}(f)",
 "bth_sum": r"BTH(f)=BTH_{lin}(f)+BTH_{disco}(f)",
 "fuse_src": r"WTH^{F}(x,y)=\max\!\left(WTH^{VIS}(x,y),\;WTH^{IR}(x,y)\right) \qquad BTH^{F}(x,y)=\max\!\left(BTH^{VIS}(x,y),\;BTH^{IR}(x,y)\right)",
 "recon": r"F = I_{base} + m\cdot WTH^{F} - m\cdot BTH^{F}\,,\qquad I_{base}=\frac{VIS+IR}{2}\,,\qquad m>0",
 "pso_v": r"v_k^{t+1}=\omega\, v_k^{t}+c_1 r_1\left(p_k-x_k^{t}\right)+c_2 r_2\left(g-x_k^{t}\right) \qquad x_k^{t+1}=x_k^{t}+v_k^{t+1}",
 "pso_fit": r"F_{o}(r,m)= SSIM_{avg} + E_{n} + PSNR_{n} \;\longrightarrow\; \max",
 "psnr": r"PSNR=10\,\log_{10}\frac{1}{MSE}\,,\qquad MSE=\frac{1}{2}\left[MSE(F,VIS)+MSE(F,IR)\right]",
 "th_clasico": r"F_{TH}=\frac{VIS+IR}{2}+\max\!\left(WTH^{VIS}_{B_5},WTH^{IR}_{B_5}\right)-\max\!\left(BTH^{VIS}_{B_5},BTH^{IR}_{B_5}\right)",
 "en": r"EN=-\sum_{l=0}^{255} p_l\,\log_2 p_l \qquad SD=\sqrt{\frac{1}{MN}\sum_{i,j}\left(F(i,j)-\mu\right)^2}",
 "mg_sf": r"MG=\frac{1}{MN}\sum_{i,j}\sqrt{\frac{(\nabla_x F)^2+(\nabla_y F)^2}{2}} \qquad SF=\sqrt{RF^2+CF^2}",
 "mi": r"MI_{X}=\sum_{f,x} p_{F,X}(f,x)\,\log_2\frac{p_{F,X}(f,x)}{p_F(f)\,p_X(x)}\,,\quad X\in\{VIS, IR\}",
 "qabf": r"Q^{AB/F}=\frac{\sum_{i,j}\left(Q^{AF}w^{A}+Q^{BF}w^{B}\right)}{\sum_{i,j}\left(w^{A}+w^{B}\right)}",
 "ssim": r"SSIM(x,y)=\frac{\left(2\mu_x\mu_y+C_1\right)\left(2\sigma_{xy}+C_2\right)}{\left(\mu_x^2+\mu_y^2+C_1\right)\left(\sigma_x^2+\sigma_y^2+C_2\right)}",
 "scd": r"SCD=r\!\left(F-IR,\;VIS\right)+r\!\left(F-VIS,\;IR\right)",
 "friedman": r"\chi^2_F=\frac{12N}{k(k+1)}\left[\sum_{j=1}^{k}R_j^2-\frac{k(k+1)^2}{4}\right]",
 "rb": r"r_{rb}=1-\frac{2W}{n(n+1)/2}",
}
FORM = {k: formula_b64(v) for k, v in F.items()}
print("formulas ok")

# ------------------------------------------------------------------ imagenes
VIS_D = os.path.join(ROOT, "data", "raw", "VIS"); IR_D = os.path.join(ROOT, "data", "raw", "IR")
# La galeria se construye desde list_pairs(), NO desde os.listdir(): leyendo el directorio se
# ignoraba PARES_EXCLUIDOS y el par corrupto Athena_heather_IR_hei_vis_g aparecia como "Par 09"
# dos paginas despues de que el propio informe declarara que se excluye; ademas, con 21 archivos
# en el directorio el recorte fijo de bloques descartaba el ultimo par valido.
import sys as _sys
_sys.path.insert(0, ROOT)
from src.datasets import list_pairs as _list_pairs
pairs_html = []
for idx, nm in enumerate([p[0].name for p in _list_pairs()], 1):
    v = Image.open(os.path.join(VIS_D, nm)).convert("L")
    r = Image.open(os.path.join(IR_D, nm)).convert("L")
    Hh = 220
    v = v.resize((int(v.width * Hh / v.height), Hh), Image.LANCZOS)
    r = r.resize((int(r.width * Hh / r.height), Hh), Image.LANCZOS)
    canvas = Image.new("RGB", (v.width + r.width + 8, Hh), (255, 255, 255))
    canvas.paste(v.convert("RGB"), (0, 0)); canvas.paste(r.convert("RGB"), (v.width + 8, 0))
    buf = io.BytesIO(); canvas.save(buf, "JPEG", quality=84)
    pairs_html.append(
        f'<div class="par"><img src="{b64(buf.getvalue(), "image/jpeg")}">'
        f'<div class="cap">Par {idx:02d}: {nm.rsplit(".", 1)[0]} (izq. VIS, der. IR)</div></div>')
def fig_file(name, max_w=1350):
    p = os.path.join(FIG, name)
    return file_img_b64(p, max_w=max_w) if os.path.exists(p) else None
EXIST = {n: fig_file(n) for n in [
    "fig_morfologia_tophat.png", "fig_cinco_se.png", "fig_pso_diagrama.png",
    "ejemplo_modalidades.png", "fig_aptitud_vs_m.png", "fig_m3fd_detecciones.png",
    "comparacion_aptitudes.png", "fig_arquitectura_yolo.png"]
    + [f"fig_m3fd_detecciones_{_e}.png" for _e in DME_ESCENAS]}
print("imagenes ok")

def tabla_friedman():
    rows = "".join(f'<tr><td class="l">{r.metric}</td><td>{r.chi2:.1f}</td>'
                   f'<td>{r.p_value:.1e}</td><td>{"Sí" if r.significant_05 else "No"}</td></tr>'
                   for r in fried.itertuples())
    return ('<table class="chica"><tr><th class="l">Métrica</th><th>χ² de Friedman</th>'
            f'<th>p-valor</th><th>Significativa (α = 0,05)</th></tr>{rows}</table>')

# ------------------------------------------------------------------ tabla por imagen
# Mismo formato que el Cuadro 2 del trabajo de referencia: una fila por metodo dentro de
# cada escena, con SSIM_avg, E, SF, SD y PSNR, y en negrita el mejor valor de cada columna.
allm = pd.read_csv(os.path.join(MR, "all_metrics.csv"))
import sys as _sys2
_sys2.path.insert(0, ROOT)
from src.metrics.evaluators import METRIC_DIRECTION as DIRECTION_TODAS

# ------------------------------------------------- bloques de actividad y fidelidad, y 17 metricas
# Cifras del encuadre: el recuento por bloques que sostiene H1, y la posicion con el conjunto
# ampliado que sostiene H2. Se derivan del dato.
_ACT = ["EN", "SD", "FE", "MG", "SF"]
_FID = ["MI_vis", "MI_ir", "SSIM", "PSNR"]
_wb = wilc[(wilc.tophat == PROP) & (wilc.baseline != "TopHat_Clasico")].copy()
_wb["d"] = _wb["diff"]
_sg = _wb.p_holm < 0.05
_sa = _wb[_wb.metric.isin(_ACT)]
_sf = _wb[_wb.metric.isin(_FID)]
_H1_ACT_FAV = int(((_sa.p_holm < 0.05) & (_sa.d > 0)).sum())
_H1_ACT_TOT = len(_sa)
_H1_FID_ADV = int(((_sf.p_holm < 0.05) & (_sf.d < 0)).sum())
_H1_FID_TOT = len(_sf)

_TODAS = [c for c in allm.columns if c in DIRECTION_TODAS]
def _rk17(mets):
    _o = {}
    for _m in mets:
        _p = allm.pivot(index="image", columns="method", values=_m)
        _o[_m] = _p.rank(axis=1, ascending=(DIRECTION_TODAS[_m] == "min"),
                         method="average").mean(axis=0)
    return pd.DataFrame(_o).mean(axis=1).sort_values()
_r17 = _rk17(_TODAS)
_POS_17 = list(_r17.index).index(PROP) + 1

# Tamano del corpus tomado del dato, no fijado a mano: el par Athena_heather_IR_hei_vis_g
# quedo excluido por tener el slot VIS duplicado del IR (ver src/datasets.PARES_EXCLUIDOS).
N_ESC = int(allm["image"].nunique())

# La galeria cualitativa se arma aqui, despues de conocer N_ESC: antes tenia el 20
# fijo en el codigo y habria quedado desalineada si cambiaba el tamano del corpus.
# Se afirma que existe un montaje por escena para que la falta no pase inadvertida.
mont_html = []
for i in range(1, N_ESC + 1):
    ruta = os.path.join(CUAL, f"montaje_{i:02d}.png")
    assert os.path.exists(ruta), (
        f"falta {ruta}: corre experiments/make_montajes_cualitativos.py")
    mont_html.append(f'<div class="mont"><img src="{file_img_b64(ruta, 1350, 84)}"></div>')

COLS_IMG = [("SSIM", "SSIM_avg"), ("EN", "E"), ("SF", "SF"), ("SD", "SD"), ("PSNR", "PSNR")]
ORDEN_IMG = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
             "TopHat_Clasico", PROP]
CORTO = {"PiramideLaplace": "LP", "RatioPiramide": "RP", "DWT": "DWT", "DTCWT": "DTCWT",
         "Curvelet": "CVT", "TopHat_Clasico": "Top-Hat clás.", PROP: "Propuesta"}
ESCENA = {
    "APC_1_view_1_fk_06_005": "APC 1 · vista 1",
    "APC_1_view_2_fk_ref_01_005": "APC 1 · vista 2",
    "APC_1_view_3_fk_ref_02_005": "APC 1 · vista 3",
    "APC_3_view_1_fk_bar_06_005": "APC 3 · vista 1",
    "APC_3_view_2_fk_NL_01_005": "APC 3 · vista 2",
    "APC_3_view_3_fk_NL_05_005": "APC 3 · vista 3",
    "Athena_2_men_in_front_of_house_meting003": "2 men in front of house",
    "Athena_APC_4_fennek01_005": "APC 4 (fennek)",
    "Athena_heather_IR_hei_vis_g": "heather (IR/vis g)",
    "Athena_heather_hei_vis": "heather (hei vis)",
    "Athena_helicopter_helib_011": "helicopter",
    "Athena_lake_lake": "lake",
    "Athena_man_in_doorway_maninhuis": "man in doorway",
    "Athena_soldier_behind_smoke_1_meting012-1200": "soldier behind smoke 1",
    "Athena_soldier_behind_smoke_2_meting012-1500": "soldier behind smoke 2",
    "Athena_soldier_behind_smoke_3_meting012-1700": "soldier behind smoke 3",
    "Athena_soldier_in_trench_1_meting016": "soldier in trench 1",
    "Athena_soldier_in_trench_2_meting055": "soldier in trench 2",
    "Triclobs_Bosnia_R": "Bosnia",
    "Triclobs_jeep_in_smoke_R": "jeep in smoke",
}
IMAGENES = list(dict.fromkeys(allm["image"]))

def tabla_por_imagen(imgs):
    filas = []
    for img in imgs:
        sub = allm[allm["image"] == img].set_index("method")
        mejor = {k: sub.loc[ORDEN_IMG, k].idxmax() for k, _ in COLS_IMG}
        for j, m in enumerate(ORDEN_IMG):
            tds = []
            for k, _ in COLS_IMG:
                v = float(sub.loc[m, k])
                b = mejor[k] == m
                s = f"{v:.5f}".replace(".", ",")
                tds.append(f'<td>{"<b>" if b else ""}{s}{"</b>" if b else ""}</td>')
            nom = CORTO[m]
            if m == PROP:
                nom = f"<b>{nom}</b>"
            cls = ' class="ini"' if j == 0 else ""
            esc = (f'<td class="l esc" rowspan="{len(ORDEN_IMG)}">{ESCENA.get(img, img)}</td>'
                   if j == 0 else "")
            filas.append(f'<tr{cls}>{esc}<td class="l">{nom}</td>{"".join(tds)}</tr>')
    head = "".join(f"<th>{lbl}&nbsp;&uarr;</th>" for _, lbl in COLS_IMG)
    return ('<table class="porimg"><tr><th class="l">Escena</th><th class="l">Método</th>'
            f'{head}</tr>{"".join(filas)}</table>')

# cuantas escenas lidera la propuesta en cada columna (para la lectura)
_lidera = {}
for k, lbl in COLS_IMG:
    _lidera[lbl] = sum(1 for img in IMAGENES
                       if allm[allm["image"] == img].set_index("method").loc[ORDEN_IMG, k].idxmax() == PROP)
print(f"propuesta lidera por columna (de {N_ESC} escenas):", _lidera)

DET_ORDEN = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT",
             "Curvelet", "TopHat_Clasico", PROP]
DET_LBL = {**LBL, "VIS": "VIS (solo)", "IR": "IR (solo)",
           "Propuesta_Novedosa": f"Propuesta Novedosa (r=25, m={V['m']})"}
def tabla_det():
    best50 = det["mAP50"].idxmax(); best5095 = det["mAP50_95"].idxmax()
    bestp = det["precision"].idxmax(); bestr = det["recall"].idxmax()
    rows = []
    for m in DET_ORDEN:
        r = det.loc[m]
        nm = DET_LBL.get(m, m)
        if m == PROP:
            nm = f"<b>{nm}</b>"
        def c(v, isbest):
            s = f"{v:.3f}".replace(".", ",")
            return f"<b>{s}</b>" if isbest else s
        rows.append(f'<tr><td class="l">{nm}</td><td>{c(r.mAP50, m==best50)}</td>'
                    f'<td>{c(r.mAP50_95, m==best5095)}</td><td>{c(r.precision, m==bestp)}</td>'
                    f'<td>{c(r.recall, m==bestr)}</td></tr>')
    return ('<table class="chica"><tr><th class="l">Entrada</th><th>mAP@0,5 ↑</th>'
            '<th>mAP@0,5:0,95 ↑</th><th>Precisión ↑</th><th>Recall ↑</th></tr>'
            f'{"".join(rows)}</table>')

# ------------------------------------------------------------------ anexos: PSO por escena
_pso_img = pd.read_csv(os.path.join(MR, "pso_por_imagen.csv"))
COLS_ANEXO = [("particulas", "Part.", 0), ("iteraciones", "Iter.", 0), ("r", "r", 0),
              ("m", "m", 2), ("SSIM_avg", "SSIM_avg", 6), ("E", "E", 6),
              ("SF", "SF", 6), ("SD", "SD", 6), ("PSNR", "PSNR", 6), ("FO", "FO", 6)]

def tabla_anexo(img):
    sub = _pso_img[_pso_img["imagen"] == img]
    idx_mejor = sub["FO"].idxmax()
    filas = []
    for i, r in sub.iterrows():
        neg = (i == idx_mejor)
        tds = []
        for col, _, dec in COLS_ANEXO:
            v = r[col]
            txt = f"{int(v)}" if dec == 0 else f"{float(v):.{dec}f}".replace(".", ",")
            tds.append(f'<td>{"<b>" if neg else ""}{txt}{"</b>" if neg else ""}</td>')
        filas.append(f'<tr>{"".join(tds)}</tr>')
    head = "".join(f"<th>{lbl}</th>" for _, lbl, _ in COLS_ANEXO)
    return f'<table class="anexo"><tr>{head}</tr>{"".join(filas)}</table>'

_mej = _pso_img.loc[_pso_img.groupby("imagen")["FO"].idxmax()]
_r1 = int((_mej["r"] == 1).sum())
_m_moda_val = float(_mej["m"].mode().iloc[0])
_m_moda = f"{_m_moda_val:.4f}".replace(".", ",").rstrip("0").rstrip(",")
_m30 = int((_mej["m"] == _m_moda_val).sum())
_n_no_borde = int((_pso_img["m"] != _m_moda_val).sum())
# Cuantos radios distintos aparecen en los anexos y cuantos por par. Estaban escritos a mano —«18
# radios distintos y entre 2 y 6»— y describian el corpus anterior a la sustitucion del par
# corrupto: el CSV vigente da 17 y de 2 a 5. Los otros cuatro numeros de esa misma nota si se
# derivaban, asi que la frase quedaba mezclando cifras vivas con cifras muertas, y la muerta es
# refutable contando en los veinte anexos que vienen a continuacion en el propio documento.
_R_DISTINTOS = int(_pso_img["r"].nunique())
_r_por_par = _pso_img.groupby("imagen")["r"].nunique()
_R_POR_PAR_LO, _R_POR_PAR_HI = int(_r_por_par.min()), int(_r_por_par.max())

# ------------------------------------------------------------------ HTML
def formula(key, num):
    return (f'<div class="formula"><img src="{FORM[key]}"><span class="eq">({num})</span></div>')

def figura(src, cap, w=88, n=[0]):
    if src is None:
        return ""
    n[0] += 1
    return (f'<div class="figc" style="width:{w}%"><img src="{src}">'
            f'<div class="cap">Figura {n[0]}. {cap}</div></div>')

css = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Times New Roman', Times, serif; color: #000; font-size: 11pt; line-height: 1.45; }
.page { width: 210mm; min-height: 297mm; padding: 20mm 20mm 18mm 20mm; page-break-after: always;
        position: relative; background: #fff; }
h1 { font-size: 16pt; text-align: center; margin-bottom: 4mm; }
h2 { font-size: 13pt; margin: 0 0 3mm 0; border-bottom: 1px solid #000; padding-bottom: 1mm; }
h3 { font-size: 11.5pt; margin: 4mm 0 1.5mm 0; }
p { text-align: justify; margin-bottom: 2.5mm; }
/* Encuadre: cuando una pagina se pasa de alto, lo que sobra cae en la siguiente. Sin estas
   reglas el corte ocurre en cualquier renglon y deja una o dos lineas huerfanas sueltas.
   Con ellas el corte respeta los bloques: se mueve el parrafo, la tabla o la figura entera. */
p, .lectura, li { orphans: 3; widows: 3; break-inside: avoid; page-break-inside: avoid; }
table, .figc, .formula, .par { break-inside: avoid; page-break-inside: avoid; }
h2, h3 { break-after: avoid; page-break-after: avoid; }
.formula { text-align: center; margin: 3mm 0; position: relative; }
.formula img { max-height: 12mm; max-width: 90%; vertical-align: middle; }
.eq { position: absolute; right: 0; top: 50%; transform: translateY(-50%); font-size: 10pt; }
.figc { margin: 3mm auto; text-align: center; }
.figc img { max-width: 100%; }
.cap { font-size: 9pt; margin-top: 1mm; text-align: center; }
table { border-collapse: collapse; width: 100%; margin: 2.5mm 0; font-size: 8pt; }
table.chica { width: 78%; margin-left: auto; margin-right: auto; font-size: 9pt; }
table.porimg { font-size: 7.6pt; }
table.anexo { font-size: 7.8pt; width: 96%; margin-left: auto; margin-right: auto; }
table.anexo td, table.anexo th { padding: 0.75mm 0.6mm; }
table.porimg td, table.porimg th { padding: 0.7mm 0.8mm; }
table.porimg td.esc { font-weight: bold; vertical-align: middle; font-size: 7.4pt; }
table.porimg tr.ini td { border-top: 1.2pt solid #000; }
th, td { border: 1px solid #000; padding: 1.2mm 1mm; text-align: center; }
th { background: #e8e8e8; font-weight: bold; }
th.l, td.l { text-align: left; padding-left: 2mm; }
.lectura { font-size: 9.5pt; font-style: italic; margin: 1.5mm 0 3mm 0; text-align: justify; }
.grid2 { display: flex; flex-wrap: wrap; gap: 3mm 4mm; justify-content: space-between; }
.par { width: calc(50% - 2.5mm); margin-bottom: 2mm; }
.par img { width: 100%; border: 1px solid #999; }
.mont { margin-bottom: 4mm; text-align: center; }
.mont img { width: 88%; border: 1px solid #999; }
/* El montaje de la pagina de apertura de la seccion 11 va solo —los dos parrafos que lo preceden
   no dejan lugar para el segundo—, asi que se lo deja ocupar todo el ancho en lugar de dejar el
   pie de la pagina en blanco. */
.mont.solo img { width: 100%; }
.pie { position: absolute; bottom: 8mm; left: 20mm; right: 20mm; text-align: center; font-size: 9pt; }
ul, ol { margin: 1.5mm 0 2.5mm 7mm; }
li { margin-bottom: 1mm; text-align: justify; }
.portada { display: flex; flex-direction: column; justify-content: center; text-align: center; }
.portada .t1 { font-size: 12pt; margin-bottom: 18mm; }
.portada h1 { font-size: 18pt; margin-bottom: 8mm; }
.portada .t2 { font-size: 12pt; margin-bottom: 22mm; }
.portada .datos { font-size: 11.5pt; line-height: 2.1; }
"""

def pie(n):
    return f'<div class="pie">{n}</div>'

H = []
H.append(f"""
<div class="page portada">
  <div class="t1">Universidad Comunera (UCOM)<br>Maestría en Ciencias de Datos</div>
  <h1>Fusión de imágenes infrarrojas y visibles<br>mediante morfología matemática</h1>
  <div class="t2">Presentación de avances<br>Propuesta Top-Hat de una escala (suma de ramas) frente al estado del arte</div>
  <div style="font-size:12.5pt; margin-top:-14mm; margin-bottom:14mm;">
    <b>{V['etiqueta']}</b><br>
    <span style="font-size:11pt;">r = 25 · m = {V['m']} · rango de búsqueda del peso: m &isin; {V['rango']}</span></div>
  <div class="datos">
    Autores: Lic. Juan Pablo Bazán — Ing. Yan Bajac<br>
    Director: D.Sc. Julio César Mello<br>
    {FECHA}
  </div>
</div>
""")

H.append(f"""
<div class="page">
  <h2>1. Introducción y esquema general</h2>
  <p>Este informe documenta el planteamiento vigente del proyecto. La propuesta central es un método de
  fusión VIS+IR basado en la transformada Top-Hat que, sobre una única escala definida por el radio r,
  combina por <b>suma</b> la respuesta promediada de cuatro elementos estructurantes lineales con la de
  un disco, y reconstruye con el esquema aditivo-sustractivo con peso de contraste m. Los
  hiperparámetros (r, m) se optimizan por enjambre de partículas (PSO).</p>
  <p>La evaluación compara la propuesta contra <b>seis métodos</b>: cinco representativos del estado del
  arte en fusión multiescala —Pirámide de Laplace (LP), Ratio of low-pass Pyramid (RP), Wavelet discreta
  (DWT), Dual-Tree Complex Wavelet (DTCWT) y wavelet db4 (rotulada CVT)— más la <b>metodología clásica de la
  transformada Top-Hat</b>, sobre los {N_ESC} pares del TNO Image Fusion Dataset con nueve métricas sin
  referencia y análisis estadístico no paramétrico.</p>
  <p>El orden del documento:</p>
  <ol>
    <li>Datos de entrada: {N_ESC} pares VIS/IR del dataset TNO (sección 2).</li>
    <li>Fundamentos: operadores morfológicos y transformada Top-Hat (sección 3).</li>
    <li>Propuesta novedosa: formulación completa, ecuaciones 4–15 (sección 4).</li>
    <li>Optimización de (r, m) por PSO (sección 5).</li>
    <li>Métodos comparativos del benchmark (sección 6).</li>
    <li>Métricas de evaluación con sus fórmulas (sección 7).</li>
    <li>Resultados cuantitativos: tabla general y gráficas (sección 8).</li>
    <li>Análisis estadístico: Friedman, Wilcoxon-Holm y ranking (sección 9).</li>
    <li>Robustez: ajuste simétrico de los comparativos y ablación del operador (sección 10).</li>
    <li>Resultados cualitativos de los {N_ESC} pares (sección 11).</li>
    <li>El detector: arquitectura, ejecución y los dos diseños experimentales (sección 12).</li>
    <li>Evaluación orientada a tarea: detección en LLVIP (sección 13) y clases complementarias en
        M3FD (sección 14).</li>
    <li>Cuadro comparativo de las metodologías en la prueba de detección y comparativa cualitativa
        sobre una escena (sección 15), y conclusiones (sección 16).</li>
    <li>Anexos 1-{N_ESC}: las 25 configuraciones del PSO en cada uno de los {N_ESC} pares.</li>
  </ol>
  {pie(2)}
</div>
""")

# Bloques calculados sobre el largo real, no recortados a 20 a mano.
# 6 + 7 + 7 y no 8 + 8 + 4: la primera pagina lleva ademas el texto de la seccion y las
# dos notas del corpus, de modo que con ocho pares los dos ultimos se derramaban y
# desperdiciaban tres cuartos de la pagina siguiente.
_c1 = 6
_resto = len(pairs_html) - _c1
chunks = [pairs_html[:_c1], pairs_html[_c1:_c1 + (_resto + 1) // 2],
          pairs_html[_c1 + (_resto + 1) // 2:]]
H.append(f"""
<div class="page">
  <h2>1. Objetivos e hipótesis, y dónde se contrasta cada una</h2>
  <p><b>Objetivo general</b>, en sus dos mitades. Primera: diseñar, implementar y caracterizar un
  operador de fusión VIS/IR por Top-Hat de una sola escala con banco de cinco elementos
  estructurantes, <b>determinando en qué dirección desplaza el punto de operación</b> frente a la
  metodología clásica y a cinco configuraciones de referencia. Segunda: <b>auditar, con ese mismo
  desarrollo como caso de estudio, la validez discriminativa del protocolo con que se lo
  evalúa</b> —métricas «mayor es mejor», hiperparámetros elegidos sobre esas mismas métricas, y
  contraste con una tarea posterior—, estableciendo qué conclusiones autoriza el orden de mérito
  que ese protocolo produce.</p>

  <p><b>Objetivos específicos.</b> <b>OE1</b>, formular e implementar el operador tal como se lo
  evalúa. <b>OE2</b>, delimitar el alcance real del PSO: qué hiperparámetro determina la aptitud y
  cuál es decisión de diseño. <b>OE3</b>, comparar contra la metodología clásica y cinco
  configuraciones del estado del arte, con pruebas no paramétricas. <b>OE4</b>, evaluar si esa
  batería discrimina calidad —control negativo, redundancia interna y sensibilidad a la
  composición—. <b>OE5</b>, medir el efecto sobre la detección y contrastar el orden de calidad
  con el de utilidad.</p>

  <p><b>Tabla 1a.</b> Las siete hipótesis, su familia y dónde se contrastan <b>en este informe</b>.
  Las siete <b>se sostienen</b>; el desarrollo completo está en el capítulo 5 del libro.</p>
  {TAB_HIPOTESIS}

  <p class="lectura">Dos advertencias, para que la tabla no prometa más de lo que este documento
  entrega. El control negativo de <b>H3</b> se resume acá pero no se desarrolla: está en el libro,
  §5.8.2. Y la correlación de rangos con que se contrasta <b>H6</b> tampoco se reproduce en estas
  páginas; lo que sí está es el conteo por escena de la sección 14, con su análisis de potencia.
  Cinco de las siete hipótesis son sobre el <b>criterio</b> y solo dos sobre el <b>operador</b>:
  ése es el reparto que justifica hablar de dos aportes y no de uno.</p>
  {pie(3)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>2. Datos de entrada: {N_ESC} pares VIS/IR (TNO)</h2>
  <p>Se trabaja con los {N_ESC} pares registrados del TNO Image Fusion Dataset (escenas de vigilancia
  nocturna: vehículos, personas, humo). Cada par tiene una imagen visible (VIS), que aporta textura y
  contexto, y una infrarroja (IR), que registra la radiación térmica. Ambas comparten nombre de archivo
  para el emparejado automático. Sobre estos {N_ESC} pares se calculan todas las métricas del informe.</p>
  <p class="lectura">Nota sobre el corpus: el conjunto original contiene 21 archivos emparejables, pero
  el par <i>Athena_heather_IR_hei_vis_g</i> se <b>excluye</b> porque su archivo del canal visible es una
  copia byte a byte del infrarrojo (mismo md5), de modo que no es un par VIS/IR sino la misma imagen
  repetida. Con VIS = IR el error cuadrático medio es nulo y todo método que devuelva la entrada sin
  modificarla obtiene SSIM = 1 y un PSNR que desborda la escala, lo que inflaba artificialmente los
  promedios de fidelidad de los métodos multiescala. El corpus efectivo es de <b>{N_ESC} pares</b>.</p>
  <p class="lectura">Composición del corpus: los {N_ESC} pares corresponden a <b>{N_SUJETOS} escenas
  distintas</b>, porque cuatro de ellas aportan varias tomas del mismo sujeto ({SUJETOS_MULTI}). En
  consecuencia los bloques del test de Friedman y de los contrastes de Wilcoxon <b>no son plenamente
  independientes</b> y el tamaño de muestra efectivo es menor que {N_ESC}; los resultados de las
  secciones 8 y 9 deben leerse con ese alcance. El libro lo declara también entre las limitaciones.</p>
  <div class="grid2">{"".join(chunks[0])}</div>
  {pie(4)}
</div>
<div class="page">
  <h2>2. Datos de entrada (continuación)</h2>
  <div class="grid2">{"".join(chunks[1])}</div>
  {pie(5)}
</div>
<div class="page">
  <h2>2. Datos de entrada (continuación)</h2>
  <div class="grid2">{"".join(chunks[2])}</div>
  {pie(6)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>3. Fundamentos: morfología matemática y Top-Hat</h2>
  <p>Dado un elemento estructurante (SE) <i>b</i>, la dilatación toma el máximo local y la erosión el mínimo:</p>
  {formula("dil_ero", 1)}
  <p>Su composición define la apertura γ, que elimina objetos claros menores que el SE, y el cierre φ, que
  rellena huecos oscuros menores que el SE:</p>
  {formula("open_close", 2)}
  <p>La transformada Top-Hat conserva exactamente lo que la apertura o el cierre eliminan: la White Top-Hat
  (WTH) extrae el detalle brillante fino y la Black Top-Hat (BTH) el detalle oscuro fino:</p>
  {formula("tophat", 3)}
  {figura(EXIST.get("fig_morfologia_tophat.png"), "Efecto de las operaciones morfológicas y de las transformadas WTH/BTH sobre una señal del dataset.", 80)}
  {pie(7)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>4. Propuesta novedosa: una escala, disco + líneas, suma de ramas</h2>
  <h3>4.1 Elementos estructurantes</h3>
  <p>En la escala de radio r se emplean cinco elementos estructurantes: un <b>disco</b> B<sub>r</sub>,
  isótropo (ecuación 4), y cuatro <b>segmentos lineales</b> L<sub>r,θ</sub> de longitud 2r+1 píxeles,
  orientados a 0°, 45°, 90° y 135° (ecuación 5):</p>
  {formula("se_disco", 4)}
  {formula("se_lineas", 5)}
  {figura(EXIST.get("fig_cinco_se.png"), "Banco de cinco elementos estructurantes (un disco y cuatro líneas) de la escala de radio r.", 62)}
  <h3>4.2 Respuestas White Top-Hat direccionales y su promedio</h3>
  <p>Para cada orientación θ, la White Top-Hat con el segmento L<sub>r,θ</sub> extrae las estructuras
  <b>brillantes</b> finas alineadas con esa dirección:</p>
  {formula("wth_theta", 6)}
  <p>Las cuatro respuestas direccionales se <b>promedian</b>, de modo que ninguna orientación queda
  privilegiada y el ruido direccional se atenúa:</p>
  {formula("wth_lin4", 7)}
  {pie(8)}
</div>
<div class="page">
  <h2>4. Propuesta novedosa (continuación)</h2>
  <h3>4.3 Respuestas Black Top-Hat direccionales y su promedio</h3>
  <p>El mismo desglose se aplica al detalle <b>oscuro</b> con el cierre φ:</p>
  {formula("bth_theta", 8)}
  {formula("bth_lin4", 9)}
  <h3>4.4 Respuesta del disco</h3>
  <p>En paralelo, el disco B<sub>r</sub> captura las estructuras brillantes y oscuras sin orientación
  predominante (manchas, objetivos térmicos compactos):</p>
  {formula("wth_disc", 10)}
  <h3>4.5 Operador combinado por suma</h3>
  <p>El operador de la propuesta <b>suma</b> la respuesta lineal promediada y la del disco, de modo que el
  realce acumula la evidencia de ambas ramas: donde una estructura es a la vez direccional e isótropa,
  ambas contribuyen (esquema de Bala et al., 2024):</p>
  {formula("wth_sum", 11)}
  {formula("bth_sum", 12)}
  <h3>4.6 Combinación entre fuentes y reconstrucción</h3>
  <p>Entre fuentes se conserva, píxel a píxel, el detalle <b>dominante</b>, y la imagen fusionada suma el
  detalle brillante y resta el oscuro sobre la base, ponderados por el peso de contraste m:</p>
  {formula("fuse_src", 13)}
  {formula("recon", 14)}
  {pie(9)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización de (r, m) por PSO: barrido de configuraciones</h2>
  <p>Cada partícula k es un candidato (r, m) que se mueve atraído por su mejor posición personal
  p<sub>k</sub> y por la mejor global g, con inercia ω decreciente linealmente de 0,9 a 0,4 y
  c1 = c2 = 1,5:</p>
  {formula("pso_v", 15)}
  <p>La función de aptitud es la del trabajo de referencia (Ortega y Espinoza, 2025), orientada a la
  calidad de fusión: premia la fidelidad estructural con las fuentes (SSIM<sub>avg</sub>), el contenido
  informativo (entropía normalizada E<sub>n</sub>) y la reducción de la distorsión (PSNR
  normalizado), sin pesos arbitrarios:</p>
  {formula("pso_fit", 16)}
  <p class="lectura"><b>Una precisión de implementación que conviene declarar.</b> La ecuación (29) del
  trabajo de referencia define el PSNR como 10·log<sub>10</sub>((M × N)² / MSE), con el <b>número de
  píxeles</b> al cuadrado en el numerador, donde la definición estándar lleva la <b>intensidad
  máxima</b> al cuadrado. Para una imagen de 620 × 450 eso desplaza el resultado en
  {ERRATA_OFFSET} dB, y explica que los valores publicados en sus anexos vayan de
  {ERRATA_PSNR_LO} a {ERRATA_PSNR_HI} dB —cifras incompatibles con una fusión, porque implicarían que
  la imagen fusionada es casi idéntica a las dos fuentes a la vez, mientras su propio SSIM<sub>avg</sub>
  mediano es {ERRATA_SSIM}—. Esta tesis usa la <b>definición estándar</b>,
  10·log<sub>10</sub>(MAX²/MSE), de modo que sus valores de F<sub>o</sub> no son directamente
  comparables con los publicados allí: los de este informe se mueven en
  {ERRATA_FO_NUESTRO} y los suyos en {ERRATA_FO_SUYO}. La diferencia está enteramente en ese término.</p>
  <p>Para elegir la configuración del enjambre se replicó el diseño experimental de Ortega y
  Espinoza (2025): se evaluaron sistemáticamente combinaciones con número de partículas variando de
  2 a 10 en incrementos de 2 y número de iteraciones de 10 a 50 en incrementos de 10, es decir,
  <b>25 configuraciones</b>. El espacio de búsqueda adopta el rango del mismo trabajo para el radio,
  r ∈ [1, 25]; para el peso se usa m &isin; {V['rango']}. Cada configuración se ejecutó con semilla
  propia sobre las escenas representativas del TNO.</p>
  <p><b>Tabla 1.</b> Resultado del barrido: mejor aptitud F<sub>o</sub> alcanzada por cada configuración
  con el rango m &isin; {V['rango']}.</p>
  {tabla_grid}
  <p class="lectura">{LECTURA_PSO}</p>
  {pie(10)}
</div>
<div class="page">
  <h2>5. Optimización por PSO (continuación): convergencia y óptimo</h2>
  {figura(charts["pso"], f"Mejor aptitud Fo alcanzada según el número de partículas (Tmax = 50), con el rango m ∈ {V['rango']}.", 84)}
  <p>{PARRAFO_RADIO}</p>
  <p>La comparación con el trabajo de referencia es directa: con el mismo diseño experimental
  y el mismo rango de radio, aquel operador (disco único, aptitud de fidelidad) convergía a un
  realce conservador; el operador propuesto (disco + líneas por suma, aptitud orientada a
  fusión) aprovecha el radio máximo disponible con un peso un orden de magnitud menor, reflejo
  de que la suma de cinco respuestas concentra más energía de detalle por unidad de peso.</p>
  {pie(11)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): justificación del peso adoptado</h2>
  <p>El peso <b>m = 0,30</b> merece una justificación explícita, porque es el límite inferior del
  rango publicado y a primera vista podría parecer una elección discrecional o un valor
  artificialmente bajo. No lo es: cuatro criterios <b>independientes entre sí</b> convergen en él.</p>

  <p><b>Primero, el óptimo está forzado por la forma de la aptitud, no elegido.</b> Un barrido
  determinista muestra que F<sub>o</sub> <b>decrece de forma estrictamente monótona</b> al aumentar m
  dentro del rango publicado: {M_CRECIENTES} tramos crecientes de {M_TRAMOS}, desde
  {f"{FO_M030:.4f}".replace(".", ",")} en m = 0,30 hasta {f"{FO_M200:.4f}".replace(".", ",")} en
  m = 2,00. En consecuencia m* = 0,30 es el <b>único máximo posible</b> dentro del intervalo, y
  cualquier optimizador converge a él: no depende de la semilla ni de la suerte de la búsqueda. Eso
  explica que las 25 configuraciones del enjambre coincidan, y convierte el resultado en
  reproducible por construcción.</p>

  <p><b>Segundo, el rango proviene del trabajo de referencia, pero el valor no.</b> El intervalo
  m &isin; [0,30; 2,00] es el espacio de búsqueda publicado por Ortega y Espinoza (2025) —lo acotan
  para «evitar estos extremos», el escaso realce por un lado y el sobrecontraste con artefactos por
  el otro— y adoptarlo es lo que hace comparable este trabajo con aquel. Conviene precisar a quién
  corresponde cada cosa, porque es un punto donde es fácil atribuir de más: <b>con el disco único de
  la referencia, su PSO no elige el piso del rango sino valores interiores</b>. Sobre las
  {REF_N} corridas de sus cinco escenas —sus anexos publican las 25 configuraciones de cada una— la
  mediana del peso es <b>{REF_M_MED}</b>, con recorrido [{REF_M_MIN}; {REF_M_MAX}], y solo una escena
  ({REF_ESC_PISO}) se ancla en el piso, en {REF_PISO} de sus 25 configuraciones. El anclaje que este
  trabajo observa en las {N_CFG} configuraciones es, por tanto, <b>una propiedad del operador</b> y no
  de la función de aptitud ni del rango: la misma aptitud y el mismo intervalo dan óptimo interior
  sobre un disco y óptimo de borde sobre el banco de cinco.</p>

  <p><b>Tabla 2a.</b> Peso óptimo por escena en el trabajo de referencia (disco único, 25
  configuraciones de enjambre por escena; extraído de sus anexos con
  <i>referencia_pso_ortega_espinoza.py</i>).</p>
  {TAB_REFERENCIA}

  {pie(12)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): la equivalencia del realce físico</h2>
  <p><b>Tercero, y es el argumento central: la equivalencia del realce físico.</b> El realce que
  efectivamente se inyecta en la reconstrucción no es m, sino el producto <b>m · |W|</b> del peso por
  la energía de detalle que extrae el operador. El banco de cinco elementos estructurantes extrae
  {f"{W_PROP:.4f}".replace(".", ",")} frente a {f"{W_CLAS:.4f}".replace(".", ",")} del disco único de
  la metodología clásica, es decir <b>{f"{GANANCIA:.2f}".replace(".", ",")} veces más energía</b>. Por
  lo tanto un mismo peso no produce el mismo realce en ambos operadores, y comparar los valores de m
  sin corregir por esa ganancia es comparar unidades distintas. Corrigiendo:</p>
  <ul>
    <li>m = 0,30 sobre el banco propuesto equivale a <b>m = {f"{M_EQUIV:.2f}".replace(".", ",")}</b>
        sobre un disco único: cae <b>dentro</b> del rango publicado [0,30; 2,00], al
        {f"{POS_EN_RANGO:.0f}"} % de su recorrido y a
        {f"{abs(M_EQUIV - 1.0):.2f}".replace(".", ",")} del peso canónico m = 1. A la inversa, ese
        rango traducido a este operador es
        [{f"{RANGO_LO:.4f}".replace(".", ",")}; {f"{RANGO_HI:.4f}".replace(".", ",")}], y m = 0,30
        también cae dentro.</li>
  </ul>
  <p>Es decir que el peso adoptado <b>no es un valor bajo</b>: es el que reproduce el realce físico
  del rango publicado una vez corregida la diferencia de energía entre los dos operadores. Parece bajo
  únicamente si se olvida que el operador cambió.</p>

  {pie(13)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): rango dinámico y tensión de criterios</h2>
  <p><b>Cuarto criterio: el rango dinámico de la reconstrucción.</b> La imagen fusionada se recorta a
  [0, 1] antes de evaluarse, de modo que los píxeles que caen fuera quedan aplastados y su información
  se pierde. Como el operador propuesto inyecta
  {f"{GANANCIA:.2f}".replace(".", ",")} veces más detalle que un disco único, el recorte se vuelve
  restrictivo mucho antes.</p>
  <p><b>Tabla 2.</b> Porcentaje de píxeles saturados por el recorte según el peso, con r = 25 sobre
  los {N_ESC} pares.</p>
  {TAB_SATURACION}
  <p class="lectura">Lectura: con m = 0,30 la saturación es de
  {f"{SAT_030:.2f}".replace(".", ",")} %, es decir por debajo del 1 % de los píxeles. Con el peso
  canónico de la metodología clásica (m = 1) este operador saturaría
  {f"{SAT_100:.2f}".replace(".", ",")} % —{f"{SAT_VECES:.1f}".replace(".", ",")} veces más— y con
  m = 2,00 más de {f"{SAT_200:.0f}"} % de la imagen. El peso adoptado es, por tanto, compatible con el
  rango dinámico del operador, y este criterio es <b>independiente de la función de aptitud</b>.</p>

  <p><b>Por qué el punto es un compromiso y no un máximo de todo.</b> Los dos criterios del trabajo
  empujan m en sentidos opuestos: la aptitud F<sub>o</sub> hacia abajo, porque dos de sus tres términos
  miden fidelidad a las fuentes; y las nueve métricas de evaluación hacia arriba, porque todas son de
  tipo «mayor es mejor» y premian la actividad.</p>
  <p><b>Tabla 3.</b> Comportamiento opuesto de los dos criterios al variar el peso (r = 25).</p>
  {TAB_TENSION}
  <p class="lectura">Lectura: al pasar de m = 0,30 a m = 2,00 la aptitud cae de
  {f"{FO_M030:.4f}".replace(".", ",")} a {f"{FO_M200:.4f}".replace(".", ",")} mientras la suma de las
  nueve métricas sube de {f"{FN_M030:.3f}".replace(".", ",")} a
  {f"{FN_M200:.3f}".replace(".", ",")}: el mismo cambio de peso mejora un criterio y empeora el otro.
  La columna de aptitud es la del enjambre —la misma que reporta la Tabla 1—, y las tres restantes
  provienen del barrido determinista sobre las mismas tres escenas.
  El SSIM se derrumba y la frecuencia espacial se dispara. <b>m = 0,30 es el punto donde esa tensión
  se resuelve</b> del lado de la aptitud publicada, respetando además el rango dinámico. Conviene
  enunciarlo con precisión: el PSO no <i>descubre</i> este valor explorando un espacio con óptimo
  interior, sino que <b>confirma un óptimo que la forma de la aptitud determina</b>; lo que se hereda
  del trabajo de referencia es la elección del rango.</p>

  {pie(14)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): estabilidad del barrido en {REP_N} corridas</h2>
  <p>El barrido publicado tiene una configuración por celda y una sola semilla, de modo que sus 25
  resultados <b>no son 25 confirmaciones independientes</b>. Conviene decirlo con precisión: la aptitud
  es determinista y las semillas estaban fijadas por la configuración y por el número de iteración,
  así que repetir una celda devolvía el mismo resultado. Para medir de verdad la dispersión se repitió
  <b>{REP_REPS} veces cada configuración</b> con la semilla en función de (n, T, repetición):
  <b>{REP_N} corridas</b> y {REP_EVALS} evaluaciones de aptitud. El control de que no cambió nada más
  que la semilla es que la repetición 0 conserva las semillas originales y reproduce el barrido
  publicado celda por celda.</p>

  <p><b>Tabla 3a.</b> Distribución del radio óptimo hallado sobre las {REP_N} corridas.</p>
  {TAB_REP_RADIO}

  <p class="lectura">Lectura, en tres puntos. <b>Primero, el peso es robusto</b>: m* = 0,30 en
  {REP_PISO} de las {REP_N} corridas ({REP_PISO_PCT} %), {REP_VEREDICTO_PESO}. Queda así confirmado
  empíricamente el argumento de la página anterior. <b>Segundo, el radio no lo es</b>:
  la búsqueda se reparte entre los dos bordes del intervalo —r = 1 en el {REP_R1_PCT} % de las
  corridas y r = 25 en el {REP_R25_PCT} %—, con un {REP_OTROS_PCT} % que queda en radios
  intermedios. No es que el argmax sea r = 1: es que <b>la optimización no identifica un radio
  estable</b>, y por lo tanto el r = 25 adoptado no puede atribuirse a ella. Es la evidencia más
  firme de H5 que contiene el trabajo. Y hay un detalle que conviene subrayar, porque cierra el
  argumento: <b>el radio que la búsqueda encuentra con más frecuencia no es el que maximiza la
  aptitud</b>. r = {REP_R_FREC} aparece más veces pero rinde {REP_FO_FREC}, mientras
  r = {REP_R_MEJOR} rinde {REP_FO_MEJOR}. El mejor óptimo está en el borde del intervalo y atrae
  menos inicializaciones, de modo que la frecuencia con que el enjambre devuelve un radio no mide
  su calidad; usar el resultado de la búsqueda como justificación del radio sería, entonces, usar
  el argumento equivocado dos veces. <b>Tercero, agrandar el enjambre no cambia el cuadro</b>: la
  proporción de corridas que terminan en r = 1 va del {REP_PORN_MIN} % al {REP_PORN_MAX} % según el
  número de partículas y del {REP_PORT_MIN} % al {REP_PORT_MAX} % según las iteraciones, sin
  tendencia, y la aptitud media se mueve en una banda de {REP_BANDA}. La rejilla de {N_CFG}
  configuraciones del trabajo de referencia no gana estabilidad con más partículas ni más
  iteraciones.</p>
  {pie(15)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): las {REP_N} corridas, una por una</h2>
  <p>La tabla siguiente abre el estudio de estabilidad por configuración, que es lo que permite ver
  de dónde viene la dispersión. Cada fila resume las {REP_REPS} repeticiones de una celda del
  barrido.</p>
  <p><b>Tabla 3b.</b> Dispersión de las {REP_N} corridas por configuración de enjambre.</p>
  {TAB_DISPERSION}
  <p class="lectura">Lectura: la aptitud mínima y la máxima de casi todas las filas son las mismas
  —{OE_FO_PUB} y el valor de r = 25—, porque la búsqueda termina en uno de los dos bordes del
  intervalo del radio. La excepción es la primera fila, la configuración con menos evaluaciones, que
  es también la única que no llega al piso del peso en el 100 % de sus repeticiones. La columna del
  radio confirma lo que la tabla anterior resume: la proporción que termina en r = 1 no sigue
  ninguna tendencia con el número de partículas ni con las iteraciones.</p>
  {pie(16)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): el óptimo exacto, por enumeración</h2>
  <p>La pregunta de si más corridas mejorarían el resultado no se contesta con más corridas. La
  aptitud es <b>determinista</b> y el radio es <b>entero</b>: el operador lo redondea al intervalo
  [1, 25], de modo que el espacio de búsqueda tiene veinticinco valores en una dimensión y un
  continuo suave en la otra. Se puede entonces dejar de muestrear y <b>enumerarlo</b>:
  {OE_N} evaluaciones —los 25 radios por {OE_PASOS} pesos— dan el máximo sin azar, a una fracción
  del costo de mil corridas de enjambre.</p>

  <p><b>Tabla 3c.</b> Mejor peso y mejor aptitud por radio, con el peso libre y con el peso
  restringido al rango publicado (primeros y últimos radios del orden).</p>
  {TAB_OPTIMO_EXACTO}

  <p class="lectura">Y el resultado corrige el enunciado de H5 en un punto importante. <b>Con el
  peso restringido</b> al rango publicado, el máximo está en r = {OE_R_PUB} con
  F<sub>o</sub> = {OE_FO_PUB}. <b>Con el peso libre</b>, el máximo está en
  r = {OE_R_LIBRE} —el radio que esta tesis adopta— con m = {OE_M_LIBRE} y
  F<sub>o</sub> = {OE_FO_LIBRE}; el rango heredado cuesta {OE_COSTO} de aptitud. Y el orden de los
  radios <b>se invierte</b>: con el peso libre la aptitud decrece al bajar el radio y r =
  {OE_PEOR_LIBRE} pasa a ser el peor ({OE_FO_PEOR_LIBRE}). El mecanismo es directo: con un peso alto
  un radio grande inyecta demasiado detalle y la similitud estructural se derrumba, de modo que gana
  el radio chico; en el óptimo verdadero del peso la inyección es pequeña y el radio grande aporta
  estructura sin costo de fidelidad.</p>

  <p><b>De modo que la discrepancia no está en el radio, sino en el peso.</b> El
  r = 25 adoptado <b>es</b> el óptimo de la aptitud del trabajo de referencia una vez que el peso no
  está atado al piso de un intervalo calibrado para otro operador: el «argmax es r = 1» que se
  observa dentro del rango publicado es un artefacto de esa restricción, y no un desacuerdo entre la
  aptitud y la batería de evaluación. Lo que sí queda en desacuerdo es el peso, y ahí la
  equivalencia de energía cierra el cuadro: el óptimo libre m = {OE_M_LIBRE} equivale a
  m = {f"{float(OE_M_LIBRE.replace(',', '.')) * GANANCIA:.3f}".replace(".", ",")} sobre un disco
  único, esencialmente el piso 0,30 que la referencia publicó <b>para su disco</b>. El intervalo
  estaba calibrado para un operador con {f"{GANANCIA:.2f}".replace(".", ",")} veces menos energía de
  detalle.</p>

  <p class="lectura">Dos consecuencias sobre el estudio de estabilidad. El PSO encontró este óptimo
  en <b>{OE_HALLADO} de las {REP_N} corridas</b> ({OE_HALLADO_PCT} %) y
  <b>{"ninguna lo superó" if OE_SUPERAN == 0 else f"{OE_SUPERAN} lo superaron"}</b>: más corridas no
  pueden mejorarlo, porque el máximo ya está alcanzado. Y el argumento de monotonía del peso, que
  hasta aquí estaba medido con r = 25, se verifica ahora en <b>los veinticinco radios</b>: el mejor
  peso dentro del rango publicado es el piso {"en todos" if OE_PISO_SIEMPRE else "en algunos"}.</p>
  {pie(17)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): por qué el barrido de la referencia dispersa</h2>
  <p>Queda una asimetría por explicar, y explicarla cambia su lectura. El barrido de la referencia
  devuelve pesos muy distintos entre corridas —mediana {REF_M_MED} y recorrido
  [{REF_M_MIN}; {REF_M_MAX}] sobre sus {REF_N} corridas— mientras el de esta tesis devuelve
  {REP_PISO} veces el mismo valor de {REP_N}. Parece una diferencia de calidad de la búsqueda y no lo
  es: es una diferencia en la <b>forma de la superficie</b>, y su causa se puede medir en sus propios
  anexos.</p>

  <p><b>Tabla 3d.</b> Recorrido de cada término de la aptitud en las {REF_N} corridas publicadas por
  el trabajo de referencia.</p>
  {TAB_REF_RECORRIDO}
  <p><b>Y la referencia lo confirma con sus propios datos.</b> El equivalente de esta tesis sobre un
  disco único —m = {f"{M_EQUIV:.2f}".replace(".", ",")}— cae en la banda donde su búsqueda aterrizó:
  sus {REF_N} corridas seleccionan pesos entre {REF_M_MIN} y {REF_M_MAX}, con medianas por escena de
  {REF_M_MED_MIN} a {REF_M_MED_MAX}. Los dos trabajos coinciden en el <b>orden de magnitud del
  realce</b> y difieren solo en el valor de m que lo expresa. Sin exagerar el acuerdo:
  {f"{M_EQUIV:.2f}".replace(".", ",")} queda por encima de cuatro de sus cinco medianas, de modo que el
  realce adoptado aquí es algo <b>mayor</b> que su valor típico, no idéntico.</p>
  <p><b>El fenómeno no es exclusivo de este trabajo.</b> En la referencia lo que se apoya en la cota
  no es el peso sino el radio: <b>r = 25, el límite superior del intervalo, aparece en {REF_R25} de sus
  {REF_N} corridas</b> ({REF_R25_PCT} %) y r = 1 en {REF_R1}. También allí, entonces, uno de los dos
  hiperparámetros lo determina una decisión de acotación —argumentada de forma cualitativa, «evitar el
  sobresuavizado y la pérdida de características térmicas»— y no la búsqueda, mientras su conclusión
  afirma que el PSO «logró determinar de forma autónoma los valores óptimos». La observación no le
  quita mérito a la optimización: delimita qué decide la optimización y qué sigue siendo diseño.</p>

  <p class="lectura">El término que debía penalizar la distorsión aporta el
  {REF_REC['PSNR_n'][1]} % de la variación: con el desplazamiento de la ecuación (29) su PSNR
  normalizado queda entre 0,94 y 0,99, casi saturado, y suma una constante a cada evaluación sin
  discriminar entre candidatos. Su criterio efectivo es entonces <b>SSIM + entropía</b>, y esos dos
  términos tienen tendencias <b>opuestas</b> en el peso: la similitud estructural cae al aumentar el
  realce y la entropía sube. Dos tendencias opuestas dan un máximo <b>interior</b>, y un máximo
  interior sobre una superficie plana significa que cada corrida, con presupuesto finito, se detiene
  en un punto distinto de su vecindad. De ahí la dispersión.</p>

  <p>En esta tesis, con la definición estándar del PSNR, ese término vale alrededor de 0,17 y sí
  varía, de modo que la similitud estructural domina la variación y la superficie resulta
  <b>monótona</b> en el peso: el óptimo cae en el borde del intervalo, y el borde actúa como
  atractor porque el recorte devuelve todas las partículas al mismo valor. <b>La estabilidad de este
  barrido no es, por tanto, una virtud del método: es el síntoma de un óptimo contra la pared.</b> Y
  la dispersión del suyo no es un defecto de su búsqueda: es el comportamiento esperable cuando el
  óptimo es genuinamente interior, que es el caso más difícil. A esto se suma una diferencia de
  diseño que amplifica el contraste: la referencia optimiza <b>por escena</b>, con una corrida
  independiente para cada una, mientras este trabajo promedia la aptitud sobre tres escenas, lo que
  suaviza la superficie y hace que un solo óptimo domine.</p>
  {pie(18)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): el mismo barrido, imagen por imagen</h2>
  <p>El estudio de estabilidad anterior repite la semilla veinte veces sobre las mismas tres
  imágenes, de modo que mide dispersión <b>entre semillas</b>. El trabajo de referencia hace otra
  cosa: una corrida independiente <b>por escena</b>, cinco escenas por veinticinco configuraciones
  de enjambre. Comparar uno con otro directamente sería comparar cosas distintas. Este trabajo tiene
  el barrido con la misma estructura —{_P_NUE['unidades']} imágenes por veinticinco
  configuraciones— y es el que permite el contraste limpio.</p>

  <p><b>Tabla 3f.</b> El mismo experimento, imagen por imagen, en los dos trabajos y con el piso
  del peso bajado.</p>
  {TAB_POR_IMAGEN}

  <p class="lectura">Lectura, en tres pasos. <b>Primero</b>, con el <i>mismo</i> rango los dos
  operadores se comportan al revés: el disco único de la referencia encuentra pesos interiores
  —mediana {_P_REF['m_med']}, solo el {_P_REF['piso_pct']} % de sus corridas en el piso— mientras el
  banco de cinco elementos se clava en el piso en el <b>{_P_NUE['piso_pct']} %</b>.
  <b>Segundo</b>, al bajar el piso el banco deja de pegarse al borde y su radio modal pasa a
  <b>r = {_P_LIB['r_moda']}</b>, con el {_P_LIB['r25_pct']} % de las corridas ahí: el mismo radio
  modal que la referencia obtiene con su propio rango ({_P_REF['r25_pct']} % de sus corridas).
  <b>Tercero</b>, y es la conclusión: la diferencia de comportamiento no está en la calidad de la
  búsqueda sino en <b>dónde cae el óptimo de cada operador respecto del intervalo heredado</b>.</p>

  <p>La razón es física y está medida. El banco de cinco elementos extrae
  <b>{GANANCIA_BANCO} veces</b> la energía de detalle del disco clásico, de modo que para inyectar
  el mismo realce necesita un peso {GANANCIA_BANCO} veces menor. La mediana
  {_P_REF['m_med']} que selecciona la referencia sobre su disco equivale a
  <b>m = {REF_M_EQUIV}</b> sobre este operador, y ese valor queda <b>por debajo del piso 0,30</b>
  del intervalo que ambos trabajos heredan. El piso no es entonces un piso para este operador: está
  ya pasado el óptimo. El optimizador no falla —está detenido contra una pared colocada donde su
  óptimo no está—, y la prueba es que al retirarla se comporta como el de la referencia. Los dos
  trabajos coinciden en el orden de magnitud del realce físico y difieren en el número que lo
  expresa.</p>
  {pie(19)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): el mismo barrido con el peso libre</h2>
  <p>El barrido determinista dice <i>dónde</i> está el óptimo; queda comprobar si la búsqueda lo
  <i>encuentra</i> cuando el rango no lo empuja contra la pared. Se repitió por tanto el estudio
  completo —{LIB_REPS} repeticiones de las 25 configuraciones, {LIB_N} corridas— con el único cambio
  de bajar el piso del peso de 0,30 a {LIB_PISO}. Todo lo demás es idéntico: mismas escenas, mismas
  semillas, mismo operador.</p>

  <p><b>Tabla 3e.</b> El mismo barrido bajo los dos rangos de búsqueda.</p>
  {TAB_DOS_RANGOS}

  <p class="lectura">Lectura, y es la confirmación del apartado anterior. <b>El peso</b>: con el rango
  libre la búsqueda ya no se pega a un borde sino que converge al óptimo interior, con mediana
  {LIB_M_MED} frente al {OE_M_LIBRE} que la enumeración señala como exacto. No es perfecta:
  {LIB_PISO_N} corridas ({LIB_PISO_PCT} %) quedan atascadas en el piso nuevo, de modo que un óptimo
  interior es efectivamente más difícil de alcanzar que un borde. <b>El radio</b>: y acá está el
  dato que importa. Con el peso libre la búsqueda se concentra en <b>r = 25 en el
  {LIB_R25_PCT} %</b> de las corridas, contra el {REP_R25_PCT} % del rango publicado, y r = 1 cae del
  {REP_R1_PCT} % al {LIB_R1_PCT} %. <b>La indefinición del radio era, también, un artefacto del
  rango.</b></p>

  <p>De modo que el cuadro completo de H5 es el siguiente. El radio r = 25 que esta tesis adopta es
  el óptimo exacto de la aptitud con el peso libre, y es además la respuesta modal de la búsqueda en
  esas condiciones: no es una decisión que haya que defender contra la optimización, sino la que la
  optimización elige cuando no está restringida por un intervalo ajeno. Lo que el intervalo heredado
  determina es el <b>peso</b>, y lo determina por completo: fija m = 0,30 en el
  {REP_PISO_PCT} % de las corridas cuando el óptimo real de la aptitud está cuatro veces más abajo.
  El aporte de la tesis en este punto no es entonces que el PSO falle, sino que <b>el rango de
  búsqueda heredado, y no el optimizador, es lo que fija uno de los dos hiperparámetros</b>. Es una
  afirmación sobre el protocolo, y ahora está medida en las dos direcciones.</p>
  {pie(20)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización por PSO (continuación): el registro de las {CORRIDAS_TOTAL} corridas</h2>
  <p>El trabajo de referencia publica sus 125 corridas en anexos, una por fila. Este publica las
  {CORRIDAS_TOTAL} en la matriz siguiente: <b>cada celda es una corrida</b>, las filas son las 25
  configuraciones de enjambre y las columnas las {REP_REPS} repeticiones independientes de cada una.
  El valor de la celda es el <b>radio</b> que esa corrida devolvió, que es lo que varía; el peso
  resultó m* = 0,30 en todas menos {"una" if len(_fuera_piso) == 1 else str(len(_fuera_piso))}, que se
  identifica al pie. El total son {CORRIDAS_EVALS} evaluaciones de aptitud y {CORRIDAS_HORAS} horas de
  cálculo.</p>

  <p><b>Tabla 3f.</b> Radio óptimo devuelto por cada una de las {CORRIDAS_TOTAL} corridas. Filas:
  partículas (n) e iteraciones (T). Columnas: número de repetición.</p>
  {TAB_500_RADIO}

  <p class="lectura">La matriz hace visible de un vistazo lo que las tablas anteriores resumen: las
  celdas alternan entre 1 y 25 sin patrón por fila ni por columna —ni el número de partículas ni el
  de iteraciones concentran un valor— y los radios intermedios aparecen de forma aislada. La
  repetición 1 es la que conserva las semillas del barrido publicado, y su columna reproduce ese
  barrido celda por celda, lo que permite verificar que el estudio no cambió nada más que la semilla.
  Excepción en el peso: {CORRIDAS_EXCEPCION}. El registro completo, con el peso, la aptitud y el
  tiempo de cada corrida, está en <i>pso_repeticiones_propuesta.csv</i>; el del barrido con el peso
  libre, en <i>pso_repeticiones_propuesta_libre.csv</i>.</p>
  {pie(21)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>6. Métodos comparativos del benchmark</h2>
  <p>La propuesta se contrasta con cinco configuraciones de referencia del estado del arte en fusión de
  imágenes visibles e infrarrojas, más la metodología clásica de la transformada Top-Hat:</p>
  <ul>
    <li><b>Pirámide de Laplace (LP)</b> — Burt y Adelson: separa frecuencias mediante filtros gaussianos
        y laplacianos (4 niveles); el detalle se combina por máxima actividad local.</li>
    <li><b>Ratio of low-pass Pyramid (RP)</b> — Toet (1989): utiliza razones entre niveles gaussianos
        consecutivos, R = G<sub>l</sub>/expand(G<sub>l+1</sub>); se conserva en cada píxel la razón que
        más se aparta de 1 (mayor contraste local) y se reconstruye multiplicativamente.</li>
    <li><b>Wavelet discreta (DWT)</b>: descompone en subbandas de detalle y aproximación (Haar, 3
        niveles); detalle por máxima magnitud de coeficiente, aproximación por promedio.</li>
    <li><b>Dual-Tree Complex Wavelet (DTCWT)</b> — Kingsbury: mejora la DWT con invariancia al
        desplazamiento y seis subbandas direccionales complejas por nivel (4 niveles); fusión por máxima
        magnitud compleja.</li>
    <li><b>Wavelet Daubechies db4 (rotulada CVT)</b>: descomposición wavelet 2D con base db4 y 3
        niveles, con la misma regla de fusión que la DWT. Corresponde señalar con precisión qué es y
        qué no es este comparativo: la implementación empleada <b>no es la transformada curvelet</b> de
        Candès et al. (2006) —que utiliza elementos base anisótropos y direccionales que una wavelet
        separable no posee— sino una aproximación por wavelet 2D, y comparte algoritmo con la DWT
        difiriendo únicamente en la base (db4 frente a Haar). Igualando la base, ambas producen
        resultados idénticos. Se conserva en el banco por comparabilidad con la literatura que emplea
        esta aproximación, pero <b>no debe leerse como una cuarta familia independiente</b>: los cinco
        métodos de referencia cubren en rigor cuatro familias (pirámides, wavelets separables, wavelets
        complejas y morfología).</li>
    <li><b>Top-Hat clásico</b>: la fusión morfológica básica con un único disco B<sub>5</sub>, detalle
        entre fuentes por máximo y reconstrucción sin ponderación (m = 1):</li>
  </ul>
  {formula("th_clasico", 17)}
  <p>Todos los métodos se ejecutan sobre los mismos {N_ESC} pares, con la misma implementación de métricas
  (<i>src/metrics/evaluators.py</i>), de modo que la comparación es directa.</p>
  {pie(22)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>7. Métricas de evaluación</h2>
  <p>Se emplean <b>nueve métricas</b> alineadas con la metodología de referencia (Ortega y Espinoza,
  2025), todas de tipo «mayor es mejor» y calculadas a partir de la imagen fusionada y sus fuentes:
  entropía (EN), desviación estándar (SD), ganancia de entropía sobre las fuentes (FE), gradiente medio (MG),
  información mutua con el visible y el infrarrojo (MI_vis, MI_ir), frecuencia espacial (SF),
  similitud estructural promedio (SSIM) y relación señal-ruido de pico (PSNR).</p>
  <p>Entropía y desviación estándar (información y contraste):</p>
  {formula("en", 18)}
  <p>Gradiente medio y frecuencia espacial (nitidez y actividad):</p>
  {formula("mg_sf", 19)}
  <p>Información mutua con cada fuente:</p>
  {formula("mi", 20)}
  <p>Similitud estructural promedio con las fuentes:</p>
  {formula("ssim", 21)}
  <p>Relación señal-ruido de pico frente a ambas fuentes (MAX = 1):</p>
  {formula("psnr", 22)}
  <p class="lectura">Alcance del conjunto y su limitación, declarados. El evaluador implementado
  calcula además <b>ocho métricas que no se incorporan al análisis</b> —Qabf, Nabf, SCD, VIF, FMI y
  los tres índices de Piella (Q0, QW, QE)—, y sus valores están disponibles en
  <i>all_metrics.csv</i> junto a los de las nueve reportadas. La decisión de restringir el análisis a
  estas nueve responde a la <b>fidelidad metodológica</b> con el trabajo de referencia, no a una
  selección de resultados: con las diecisiete la propuesta cede el primer puesto del ranking agregado
  y pasa al tercero, aunque lidera dos de las ocho excluidas (SCD y VIF). La limitación que importa
  es otra y conviene enunciarla con precisión: las nueve son <b>todas de tipo «mayor es mejor»</b>, de
  modo que ninguna penaliza el ruido ni los artefactos —la única métrica implementada con dirección
  inversa, Nabf, queda fuera del conjunto—. En consecuencia el criterio premia la magnitud del realce:
  se verificó con un control negativo en el que una fusión artificial de ruido gaussiano con
  σ = 0,20 alcanza el <b>{CN_ORD_RUIDO} puesto entre {CN_ENTRADAS} entradas</b> (rango
  {CN_RANGO_RUIDO}), por delante de {CN_COMPAR_DETRAS} de los seis métodos comparativos, y
  cuyo rango mejora de forma monótona al aumentar la varianza. Los resultados de las secciones
  siguientes deben leerse con ese alcance.</p>
  {pie(23)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>8. Resultados cuantitativos</h2>
  <p><b>Tabla 4.</b> Benchmark completo: los 7 métodos con las nueve métricas (promedio de los {N_ESC} pares
  TNO; en negrita el mejor valor de cada columna).</p>
  {tabla_metodos(ORDEN, resaltar=PROP)}
  <p class="lectura">{LECTURA_BENCH}</p>
  {figura(charts["quality"], "Cuatro métricas representativas (EN, FE, SF, SSIM); la barra azul es la propuesta.", 96)}
  {pie(24)}
</div>
""")

# ---------- 8 (continuación): resultados escena por escena, formato del Cuadro 2 ----------
_bloques = [IMAGENES[i:i + 4] for i in range(0, len(IMAGENES), 4)]   # 4 escenas por pagina
for _b, _imgs in enumerate(_bloques, 1):
    _cab = ("8. Resultados por par (formato del Cuadro 2 del trabajo de referencia)"
            if _b == 1 else f"8. Resultados por par (continuación {_b} de 5)")
    _intro = ("" if _b > 1 else f"""
  <p>Además de los promedios, se detallan los resultados <b>par por par</b> sobre los {N_ESC} pares
  del TNO, con la misma disposición del Cuadro 2 del trabajo de referencia: una fila por método dentro
  de cada par y, en <b>negrita</b>, el mejor valor de cada columna en ese par. Se incluye también
  la metodología clásica Top-Hat, que es la referencia morfológica directa de la propuesta.</p>
  <p class="lectura">Unidades: SSIM<sub>avg</sub> y SD en [0, 1]; E en bits (0–8); SF adimensional;
  PSNR en dB. La correspondencia con el Cuadro 2 de referencia es directa —allí E y PSNR se reportan
  normalizados (E/8 y PSNR/100) y SD en la escala 0–255—, de modo que el orden entre métodos es
  comparable columna por columna.</p>""")
    _lect = ("" if _b < 5 else f"""
  <p class="lectura">Lectura del conjunto de los {N_ESC} pares: la propuesta obtiene el mejor valor en
  <b>{_lidera['E']} de {N_ESC}</b> pares en entropía (E) y en <b>{_lidera['SD']} de {N_ESC}</b> en desviación
  estándar (SD), frente a <b>{_lidera['SF']} de {N_ESC}</b> en frecuencia espacial (SF, donde domina el
  Top-Hat clásico), <b>{_lidera['SSIM_avg']} de {N_ESC}</b> en SSIM<sub>avg</sub> y
  <b>{_lidera['PSNR']} de {N_ESC}</b> en PSNR. El patrón por par confirma el de los promedios: la
  propuesta lidera de forma sistemática las métricas de información y contraste, y cede las de
  fidelidad a las fuentes.</p>""")
    H.append(f"""
<div class="page">
  <h2>{_cab}</h2>{_intro}
  <p><b>Tabla 4{chr(96 + _b)}.</b> Resultados por par — pares {(_b - 1) * 4 + 1} a
  {(_b - 1) * 4 + len(_imgs)} de {N_ESC}.</p>
  {tabla_por_imagen(_imgs)}{_lect}
  {pie(24 + _b)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>9. Análisis estadístico</h2>
  <p>Primero, el test de Friedman (7 métodos × {N_ESC} imágenes, por rangos) para cada métrica:</p>
  {formula("friedman", 23)}
  <p><b>Tabla 5.</b> Resultados del test de Friedman.</p>
  {tabla_friedman()}
  {pie(30)}
</div>
<div class="page">
  <h2>9. Análisis estadístico (continuación): Wilcoxon y ranking</h2>
  <p>Wilcoxon pareado de la propuesta contra cada rival ({N_ESC} imágenes), con corrección de Holm y tamaño
  de efecto rank-biserial:</p>
  {formula("rb", 24)}
  <p><b>Tabla 6.</b> Resumen de los {len(wtab)} contrastes de la propuesta: mejor / peor / sin
  diferencia significativa (≈), α = 0,05.</p>
  {tabla_wilcoxon}
  <p class="lectura">Lectura: la propuesta resulta significativamente mejor en {w_mejor} contrastes,
  peor en {w_peor} y sin diferencia en {w_emp}; su ventaja más consistente es en las
  métricas de actividad e información (EN, FE, MG, SF), mejor que los cinco métodos del estado del arte.</p>
  {figura(charts["ranking"], "Ranking promedio global de los 7 métodos (9 métricas, dirección respetada); la barra azul es la propuesta.", 78)}
  {pie(31)}
</div>
""")

pg = 32

# El informe afirmaba que el primer puesto se obtiene «con separacion estadisticamente
# significativa». No habia ningun test que respaldara eso: Friedman y Wilcoxon corren por metrica
# sobre los valores, no sobre el rango promedio. Y ranking_methods.csv trae TRES columnas de
# agregacion de las que el informe leia solo una, la que mas favorece a la propuesta. Publicar las
# tres —con el empate a la vista— es mejor que dejar que la mesa abra el CSV: el orden de merito
# dependiendo de como se agrega es exactamente lo que sostiene H2.
H.append(f"""
<div class="page">
  <h2>9. Análisis estadístico (continuación): el orden depende de cómo se agrega</h2>
  <p>El primer puesto del apartado anterior se obtiene promediando, para cada método, su rango
  dentro de cada imagen. Es una decisión de agregación entre varias posibles, y conviene mostrar
  qué pasa con las otras dos que este mismo trabajo calcula, porque están las tres en
  <span class="mono">ranking_methods.csv</span> y cualquiera que abra el archivo las ve juntas.</p>

  <p><b>Tabla 6a.</b> El mismo benchmark bajo tres formas de agregar las {N_METRICAS_RK} métricas.</p>
  {TAB_AGREGACIONES}

  <p class="lectura">Lectura. La propuesta encabeza con las dos agregaciones por rangos, y
  sostiene el primer puesto incluso al retirar FE, que es la métrica redundante: eso responde la
  objeción de que su ventaja viniera de contar dos veces la entropía. Pero con la tercera
  —promediar primero los valores y rankear después— hay <b>empate</b> con la pirámide de Laplace,
  en {_coma(AG_FILAS[2][3], 3)}. No cambió ninguna imagen ni ninguna métrica: cambió el orden de
  dos operaciones. <b>No se reclama aquí una separación estadísticamente significativa</b>, y
  conviene ser explícito sobre por qué: los contrastes de Friedman y Wilcoxon del apartado
  anterior corren <b>por métrica y sobre los valores</b>, de modo que no autorizan a afirmar nada
  sobre la diferencia entre dos rangos promedio. Un test sobre esa diferencia no se hizo.</p>

  <p>Lejos de debilitar el resultado, esto es una instancia más del segundo aporte y de H2: el
  orden de mérito no es una propiedad del operador sino del criterio con que se lo evalúa, y
  «criterio» incluye la aritmética con que se resumen las métricas, no solo cuáles se eligen. La
  sección 10 lleva el mismo examen a la composición del conjunto y al ajuste de los comparativos.
  Lo que se sostiene es lo verificable: <b>con el criterio del trabajo de referencia, y con esa
  agregación declarada, la propuesta encabeza el benchmark</b>.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>10. Robustez del resultado: ajuste simétrico y ablación del operador</h2>
  <p>El resultado del apartado anterior se obtiene con cada método comparativo en su
  <b>configuración estándar</b>, que es el protocolo habitual de la literatura. Cabe sin embargo una
  objeción legítima: el radio de la propuesta (r = 25) se eligió observando las nueve métricas de
  evaluación, mientras los seis comparativos corrieron con su parámetro por defecto. Para responderla
  se barrió el parámetro principal de cada método —número de niveles en los multiescala, radio en el
  Top-Hat clásico— y se seleccionó su mejor valor con <b>el mismo criterio</b> aplicado a la propuesta:
  el promedio de rangos intra-bloque sobre las nueve métricas, calculado entre las configuraciones del
  propio método. Son {len(_ajm)} configuraciones evaluadas sobre los {N_ESC} pares.</p>
  <p><b>Tabla 7.</b> Ranking en cuatro escenarios de ajuste (promedio de rangos intra-bloque; menor es
  mejor; en negrita el líder de cada columna y la fila de la propuesta).</p>
  {TAB_ESCENARIOS}
  <p class="lectura">Lectura, en cuatro puntos. <b>Primero</b>, en la configuración estándar la
  propuesta es <b>{POS_A}.ª de {len(_ajr)}</b> ({f"{VAL_A:.3f}".replace(".", ",")}).
  <b>Segundo</b>, el criterio de ajuste elige para la propuesta <b>r = {_elg.get(PROP, 25)}</b>, es
  decir el mismo valor publicado entre los once candidatos evaluados: no es un valor arbitrario, y por
  eso los escenarios B y C coinciden. <b>Tercero</b>, y es el punto central,
  <b>ninguno de los cinco métodos del estado del arte alcanza a la propuesta ni siquiera ajustado</b>:
  el mejor de ellos es {LBL.get(SOTA_MEJOR, SOTA_MEJOR).split(" (")[0]} con
  {f"{SOTA_MEJOR_VAL:.3f}".replace(".", ",")} frente a
  {f"{VAL_B:.3f}".replace(".", ",")} de la propuesta. <b>Cuarto</b>, el único método que la supera
  es el <b>Top-Hat clásico</b> —que no pertenece al estado del arte sino a la misma familia
  morfológica— por {f"{VAL_B - VLID_B:.3f}".replace(".", ",")}, y el párrafo siguiente muestra que
  esa diferencia no proviene del operador.</p>
  <p>Con las diecisiete métricas disponibles (escenario D) la propuesta pasa al
  {POS_D}.º puesto ({f"{VAL_D:.3f}".replace(".", ",")}), detrás de
  {LBL.get(LID_D, LID_D).split(" (")[0]}. La composición del conjunto de métricas, y no solo el
  método, determina el orden: es el hallazgo que se discute en el apartado 14.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>10. Robustez (continuación): el peso de realce y el aporte del banco</h2>
  <p><b>El origen de la ventaja del Top-Hat clásico en el escenario B.</b> Ese método se ejecuta con
  <b>m = 1</b> por definición de la metodología clásica, frente a <b>m = 0,30</b> de la propuesta: no
  compiten dos operadores, compiten dos pesos de realce, con el clásico inyectando <b>3,3 veces más</b>.
  Igualando el peso —Top-Hat clásico con r = 25 y m = 0,30, los mismos valores de la propuesta— y
  <b>sustituyéndolo</b> por esa versión dentro del benchmark de siete métodos, la propuesta conserva el
  primer lugar del ranking de nueve métricas: {f"{CTRL_PROP:.3f}".replace(".", ",")} frente a
  {f"{CTRL_TH_M030:.3f}".replace(".", ",")} del clásico, es decir <b>gana por
  {f"{CTRL_VENTAJA:.3f}".replace(".", ",")}</b>. La ventaja de
  {f"{abs(VAL_B - VLID_B):.3f}".replace(".", ",")} del escenario B proviene, entonces, de su peso
  m = 1 —más del triple del de la propuesta— y no del operador: la diferencia del escenario B mide el
  peso, no el operador.</p>
  <p><b>Aporte del banco de cinco elementos estructurantes.</b> La comparación contra el Top-Hat
  clásico no lo aísla, porque los dos operadores no comparten hiperparámetros. La ablación fija
  (r, m) = (25; 0,30) y varía únicamente la regla de combinación de las respuestas.</p>
  <p><b>Tabla 8.</b> Ablación del operador con (r, m) fijos (promedio de rangos intra-bloque entre los
  seis brazos; menor es mejor).</p>
  {TAB_ABLACION}
  <p class="lectura">Lectura: con las nueve métricas del trabajo, <b>la suma de ramas —la propuesta— es
  el mejor brazo</b> ({f"{_abl.loc['suma','rango_9']:.3f}".replace(".", ",")} frente a
  {f"{_abl.loc['disco','rango_9']:.3f}".replace(".", ",")} del disco único con idénticos r y m), de
  modo que el banco <b>sí</b> aporta sobre el disco. Con las diecisiete el orden se invierte y el mejor
  brazo es el máximo entre ramas. El contraste directo suma frente a disco es significativo a favor de
  la propuesta en seis métricas (EN, SD, FE, MG, SF y VIF) y en contra en nueve, todas de fidelidad o
  de artefactos: el banco <b>desplaza el punto de operación</b> hacia la actividad espacial en lugar de
  dominar en todo el espectro. Un dato en favor del operador: la imagen base (VIS+IR)/2 <b>sin
  operador</b> queda última de los seis brazos con las diecisiete métricas
  ({f"{_abl.loc['base','rango_17']:.3f}".replace(".", ",")}), de modo que el mérito no proviene de
  la imagen de partida.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>11. Resultados cualitativos: los {N_ESC} pares</h2>
  <p>Para cada escena se muestran diez entradas: las fuentes VIS e IR, los seis comparativos, la
  <b>metodología de la referencia</b> (recuadro azul) y la propuesta (recuadro rojo). Se sugiere
  observar: la visibilidad del objetivo térmico, la conservación de la textura del fondo visible y
  la ausencia de halos en los bordes.</p>
  <p class="lectura">Por qué la metodología de la referencia es una entrada aparte del comparativo
  «Top-Hat clásico». Aquel corre con la parametrización manual r = 5 y m = 1. La metodología de
  Ortega y Espinoza es el <b>mismo operador de disco único</b> pero con el (r, m) que halla su PSO,
  y sobre este corpus ese barrido devuelve <b>r = 25 y m = 0,30</b> —la celda de mejor aptitud de
  su rejilla, F<sub>o</sub> = 1,7544 frente a 1,7507 en r = 1—. Son los <b>mismos</b>
  hiperparámetros que adopta la propuesta, de modo que los dos últimos paneles de cada montaje se
  diferencian únicamente en el operador: disco único contra banco de cinco elementos. Es la
  ablación del operador, vista a ojo, y por eso van uno al lado del otro en la última fila.</p>
  {mont_html[0].replace('class="mont"', 'class="mont solo"')}
  {pie(pg)}
</div>
""")
pg += 1
# Un solo montaje en la pagina de apertura: con los dos parrafos de arriba, dos montajes
# desbordaban la pagina y el bloque 8b lo marcaba. Los pares arrancan entonces en el segundo.
for i in range(1, N_ESC, 2):
    solo = i + 1 >= N_ESC
    blk = mont_html[i] + ("" if solo else mont_html[i + 1])
    rot = (f'par {i+1} de {N_ESC}' if solo else f'pares {i+1} y {i+2} de {N_ESC}')
    H.append(f'<div class="page"><h2>11. Resultados cualitativos ({rot})</h2>'
             f'{blk}{pie(pg)}</div>')
    pg += 1

H.append(f"""
<div class="page">
  <h2>12. El detector: arquitectura, ejecución y protocolo de entrenamiento</h2>
  <p>Las dos pruebas de detección usan el mismo detector, de modo que conviene precisar qué es,
  cómo está formado y cómo se lo ejecutó, antes de leer sus resultados. Se eligió un detector
  <b>de una sola etapa</b>: a diferencia de las arquitecturas de dos etapas —que primero proponen
  regiones y después las clasifican—, YOLO plantea la detección como una única regresión sobre la
  imagen completa, lo que le da el costo por imagen necesario para evaluar nueve entradas sobre
  varios miles de imágenes (Redmon et al., 2016). Se usó la versión <b>YOLOv8n</b>, la variante
  <i>nano</i> de la familia (Jocher et al., 2023; la cita acredita la publicación del modelo, y la
  versión exacta de la biblioteca con la que se corrió se declara más abajo).</p>

  <p><b>Cómo está formado.</b> Los datos que siguen no se citan de la documentación: se midieron
  sobre los propios pesos entrenados de este trabajo. La red tiene
  <b>{YOLO_PARAMS} parámetros</b> y <b>{YOLO_GFLOPS} GFLOPs</b> a una entrada de {YOLO_IMGSZ}×{YOLO_IMGSZ},
  repartidos en {YOLO_MODULOS} módulos con esta composición: {YOLO_COMPOSICION}. Los tres bloques
  cumplen funciones distintas:</p>
  <ul>
    <li><b>Columna (backbone).</b> Convoluciones con paso 2 que reducen la resolución en cinco
        niveles, intercaladas con bloques <i>C2f</i> —conexiones parciales cruzadas, que dividen el
        canal en dos ramas y concatenan los residuos— y cerradas por un <i>SPPF</i>, que agrupa
        contexto con ventanas de varios tamaños. Es lo que extrae los rasgos.</li>
    <li><b>Cuello (neck).</b> Una pirámide con camino descendente y ascendente: los
        {YOLO_UPSAMPLE} sobremuestreos y las {YOLO_CONCAT} concatenaciones fusionan rasgos de tres
        escalas, de modo que la red detecta objetos grandes y pequeños con el mismo paso.</li>
    <li><b>Cabezal (head).</b> Desacoplado y <b>sin cajas ancla</b>: predice el centro y la extensión
        de cada objeto con una rama de clasificación y otra de regresión, y modela la caja como una
        distribución discreta sobre las distancias al borde (módulo <i>DFL</i>), más estable que una
        regresión directa.</li>
  </ul>

  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>12. El detector (continuación): el grafo del modelo</h2>
  <p>El diagrama siguiente no se copia de la documentación de la biblioteca: se leyó el grafo del
  <b>modelo entrenado de este trabajo</b> —los {ARQ_CAPAS} módulos con sus índices de origen,
  canales, núcleos y pasos— y se dibujó eso. Las resoluciones de cada nivel tampoco son un supuesto:
  salen de acumular los pasos declarados desde la entrada de {ARQ_IMGSZ}×{ARQ_IMGSZ}.</p>
  {figura(EXIST.get("fig_arquitectura_yolo.png"),
          f"Arquitectura del detector leída del checkpoint {ARQ_CKPT}. En gris oscuro, las capas "
          f"cuya salida alimenta otra escala; en línea azul punteada, los atajos que forman la "
          f"pirámide; en granate, los tres niveles de detección. {ARQ_PARAMS} parámetros.", 100)}
  <p class="lectura">Se lee en tres tramos. La <b>columna</b> reduce la resolución cinco veces con
  convoluciones de paso 2, de {ARQ_IMGSZ}² a {ARQ_RES_MIN}², y deja tres derivaciones —las capas
  {ARQ_TAPS}— que son los tres niveles de escala. El <b>cuello</b> las combina en dos pasadas: la
  descendente sube la resolución con dos sobremuestreos y concatena hacia atrás con las capas
  {ARQ_SRC_TD}; la ascendente vuelve a bajar con dos convoluciones de paso 2 y concatena con las
  capas {ARQ_SRC_BU}. Esas cuatro concatenaciones son lo que permite que un objeto grande y uno
  pequeño se detecten con el mismo paso de la red. El <b>cabezal</b> toma las salidas
  {ARQ_SALIDAS} y predice en los tres niveles a la vez, con ramas separadas de clasificación y de
  caja.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>12. El detector (continuación): con qué se ejecutó</h2>
  <p>La configuración es la misma en las dos pruebas y quedó registrada en los <i>args.yaml</i> de
  cada corrida: <b>{YOLO_ENTORNO}</b>. Los valores se transcriben <b>literales</b> del archivo de
  configuración —con punto decimal— para que puedan copiarse tal cual.</p>
  <p><b>Tabla 10.</b> Configuración de entrenamiento e inferencia del detector, común a las dos
  pruebas.</p>
  {TAB_YOLO_HIPER}
  <p class="lectura">Nota: se parte del modelo preentrenado en COCO y se reentrena por completo, sin
  congelar capas; el aumento de datos es el estándar de la biblioteca y se mantuvo igual entre
  entradas para no introducir una variable más. El mosaico se desactiva en las últimas
  {YOLO_CLOSE_MOSAIC} épocas, que es la práctica recomendada para que el modelo cierre sobre imágenes
  sin composición artificial.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>12. El detector (continuación): los dos diseños experimentales</h2>
  <p>Las dos pruebas responden preguntas distintas y por eso <b>no comparten diseño</b>. Confundirlas
  sería el error más fácil de cometer al leer las tablas que siguen.</p>

  <p><b>LLVIP — un detector por entrada.</b> {LLVIP_TRAIN} imágenes de entrenamiento y
  {LLVIP_VAL} de validación, una sola clase (<i>person</i>). Se entrena un YOLOv8n <b>independiente
  sobre cada entrada</b> —las dos modalidades y los siete métodos de fusión— con idéntica
  configuración y semilla. Como los pares VIS/IR están registrados, las anotaciones valen para toda
  versión fusionada: lo único que cambia entre corridas son los píxeles, de modo que la diferencia de
  mAP es atribuible al método de fusión. La pregunta que responde es <i>¿cuánto ayuda esta imagen a
  un detector entrenado sobre ella?</i></p>
  <p><b>M3FD — un único detector, inferencia por entrada.</b> {M3FD_TRAIN} imágenes de
  entrenamiento y {M3FD_VAL} de validación con VIS e IR <b>mezcladas</b> y sus seis clases
  ({M3FD_CLASES}). Se entrena <b>un solo</b> modelo y se lo evalúa por inferencia sobre la validación
  de cada entrada ({M3FD_TEST} imágenes), y el conteo por escena del objetivo declarado sobre el
  subconjunto de escenas que contienen las dos clases complementarias ({M3FD_COMP} escenas). La
  pregunta es otra: <i>¿qué entrada le permite a un mismo detector recuperar las dos clases a la
  vez?</i></p>

  <p><b>El punto de control, que no es un detalle menor.</b> En LLVIP se reporta <b>last.pt</b>, los
  pesos de la última época, y no <b>best.pt</b>. La razón es que LLVIP no tiene partición de prueba
  separada: la validación cumple los dos roles, y elegir la mejor época <i>medida en el mismo conjunto
  que se reporta</i> introduce un sesgo optimista del orden de las diferencias entre métodos, que es
  justamente lo que se quiere medir. En M3FD sí se usa <b>best.pt</b>, porque allí la época se elige
  sobre la validación mixta y se reporta sobre conjuntos distintos. Las {YOLO_EPOCAS} épocas se
  completaron en todos los casos: con paciencia {YOLO_PATIENCE} no hubo corte temprano.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>13. Evaluación orientada a tarea: detección en LLVIP</h2>
  <p>Para medir el efecto práctico de la fusión se reentrenó el mismo detector <b>YOLOv8n</b> (40 épocas,
  misma configuración y semilla) sobre cada versión fusionada del dataset etiquetado <b>LLVIP</b>
  (peatones nocturnos; subconjunto de 2.000 imágenes de entrenamiento y 500 de validación). Como los
  pares VIS/IR están registrados, las anotaciones valen para toda versión fusionada: la diferencia de
  mAP aísla el efecto del método de fusión.</p>
  <p><b>Tabla 9.</b> Detección de peatones en LLVIP — mAP por entrada del detector.</p>
  {tabla_det()}
  <p class="lectura">Lectura: toda fusión supera con claridad al visible solo (mAP@0,5 de {LLVIP_VIS} a la banda
  {LLVIP_LO}–{LLVIP_HI}); el infrarrojo solo es la modalidad más fuerte ({LLVIP_IR}) y ninguna
  fusión lo supera, coherente con que el peatón nocturno es esencialmente térmico; y entre las fusiones,
  la propuesta alcanza <b>{LLVIP_PROP}</b>. Conclusión honesta: la ventaja de la propuesta en las
  métricas de imagen no se traslada automáticamente a la detección, de modo que ambos criterios deben
  reportarse por separado.</p>
  {figura(charts["det"], "mAP por entrada del detector (YOLOv8n reentrenado por método sobre LLVIP).", 88)}
  {pie(pg)}
</div>
""")
pg += 1

_M3_ORDEN = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT",
             "Curvelet", "TopHat_Clasico", PROP]
_M3_LBL = {**LBL, "VIS": "VIS (solo)", "IR": "IR (solo)",
           "TopHat_Clasico": "Top-Hat clásico (r=5; m=1)"}
_m3_best = {c: _m3.loc[[k for k in _M3_ORDEN if k in _m3.index], c].idxmax()
            for c in ("AP50_People", "AP50_Lamp", "par", "mAP50")}
_m3_filas = []
for _k in _M3_ORDEN:
    if _k not in _m3.index:
        continue
    _r = _m3.loc[_k]
    _tds = ""
    for _c in ("AP50_People", "AP50_Lamp", "par", "mAP50"):
        _v = f"{_r[_c]:.3f}".replace(".", ",")
        _tds += f"<td>{'<b>' if _m3_best[_c] == _k else ''}{_v}{'</b>' if _m3_best[_c] == _k else ''}</td>"
    _nom = _M3_LBL.get(_k, _k)
    if _k == PROP:
        _nom = f"<b>{_nom}</b>"
    _m3_filas.append(f"<tr><td>{_nom}</td>{_tds}</tr>")
TAB_M3FD = ('<table><thead><tr><th>Entrada del detector</th><th>AP People &uarr;</th>'
            '<th>AP Lamp &uarr;</th><th>Promedio del par &uarr;</th><th>mAP@0,5 &uarr;</th>'
            f'</tr></thead><tbody>{"".join(_m3_filas)}</tbody></table>')


H.append(f"""
<div class="page">
  <h2>14. Detección con clases complementarias (M3FD)</h2>
  <p>Experimento diseñado para aislar el escenario donde la fusión es insustituible: el dataset
  <b>M3FD</b> (Liu et al., 2022) anota seis clases, dos de ellas de <b>visibilidad opuesta</b>: las
  personas dominan en el infrarrojo (firma térmica) y las luces (Lamp) son esencialmente visibles solo
  en el canal visible. Un <b>único detector YOLOv8n</b> se entrenó con las imágenes de ambas modalidades
  mezcladas (etiquetas compartidas, 40 épocas) y se evaluó <b>por inferencia</b> sobre cada modalidad y
  cada método de fusión.</p>
  <p>El corpus se reparte en <b>tres particiones disjuntas</b> obtenidas por muestreo aleatorio
  <b>estratificado</b> según la presencia de las dos clases complementarias: 2.000 pares de
  entrenamiento, 500 de <b>selección del modelo</b> y {M3_N} de <b>prueba</b>. La separación entre las
  dos últimas es necesaria: si el checkpoint se elige midiendo en el mismo conjunto que luego se
  reporta, el resultado hereda un sesgo optimista que no es comparable entre métodos. La
  estratificación evita además que las particiones tengan proporciones de clase distintas, lo que
  desplazaría el criterio de selección.</p>
  <p><b>Tabla 11.</b> AP@0,5 por clase y mAP global (medias sobre las {M3_N} imágenes de la partición
  de prueba, disjunta de la de entrenamiento y de la de selección del modelo).</p>
  {TAB_M3FD}
  <p class="lectura">{LECTURA_M3FD}</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>14. Clases complementarias (continuación): la prueba visual</h2>
  <p>{PARRAFO_DETECCIONES}</p>
  {figura(EXIST.get("fig_m3fd_detecciones.png"), PIE_DETECCIONES, 92)}
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>14. Clases complementarias (continuación): el objetivo medido por escena</h2>
  <p>El promedio de precisión (mAP) de la tabla anterior no mide el objetivo declarado, que
  afirma que la fusión permita <b>detectar objetos que no se detectan en el visible ni en el
  infrarrojo por separado</b>: eso es un enunciado <b>por escena</b>, no un promedio. Lo que
  corresponde contar es en cuántas escenas cada entrada recupera <b>simultáneamente</b> al menos
  un objeto de la clase dominante en infrarrojo (personas) y uno de la dominante en visible
  (luces), con la caja anotada emparejada con IoU &ge; 0,5 y confianza &ge; 0,25. Para dar
  potencia a la prueba, la evaluación se concentró en las <b>{CP_N} escenas</b> del corpus que
  tienen anotadas ambas clases y que no participaron del entrenamiento ni de la selección del
  modelo; las particiones de ajuste y selección quedaron idénticas, de modo que el modelo es el
  mismo y la única variable que cambia es el tamaño de la muestra.</p>
  <p><b>Tabla 12.</b> Recuperación de ambas clases complementarias por escena. Las
  <b>{CP_CRIT} escenas críticas</b> son aquellas en las que ni el visible ni el infrarrojo lo
  logran por separado: son las que la hipótesis reclama para la fusión.</p>
  {TAB_COMPL}
  <p class="lectura">Lectura: la mejor entrada es
  <b>{_CP_LBL.get(CP_MEJOR, CP_MEJOR).split(" (")[0]}</b> con
  {f"{CP_MEJOR_PCT:.1f}".replace(".", ",")} %, y resuelve {CP_MEJOR_CRIT} de las {CP_CRIT}
  escenas críticas. La propuesta alcanza <b>{f"{CP_PROP:.1f}".replace(".", ",")} %</b>, es decir
  <b>por debajo del visible solo</b> ({f"{CP_VIS:.1f}".replace(".", ",")} %), con {CP_PB} escenas
  ganadas frente a {CP_PC} perdidas (McNemar exacto p =
  {f"{CP_PP:.4f}".replace(".", ",")}) y {CP_PROP_CRIT} escenas críticas resueltas. Aplicando la
  corrección de Holm a las catorce comparaciones de la familia, el <b>único contraste
  significativo</b> es la Pirámide de Laplace frente al infrarrojo.</p>
  {pie(pg)}
</div>
""")
pg += 1

# La conclusion de H6 va en su propia pagina. Al declarar la potencia el parrafo crecio y la
# pagina anterior —que ya lleva la tabla de las 232 escenas— derramaba; lo marco el bloque 8b.
# Ademas es el remate de una de las siete hipotesis y se lee mejor sin la tabla encima.
H.append(f"""
<div class="page">
  <h2>14. Clases complementarias (continuación): hasta dónde llega el rechazo</h2>
  <p><b>Conclusión sobre el objetivo declarado, y hasta dónde llega.</b> La hipótesis de que una
  mejor calidad de fusión se traduzca en la detección de objetos complementarios <b>se rechaza</b>
  para el método propuesto. Conviene decir con precisión qué alcance tiene ese rechazo, porque el
  contraste <b>no es significativo</b> y una prueba que no rechaza puede querer decir dos cosas
  muy distintas: que no hay efecto, o que no había con qué verlo. El test de McNemar condiciona en
  los pares discordantes, y acá son <b>{POT_ND}</b> ({POT_B} escenas a favor de la propuesta y
  {POT_C} a favor del visible). Con esos {POT_ND} discordantes y &alpha; = 0,05, la prueba alcanza
  una potencia de <b>0,80 recién a partir de {POT_DELTA80} puntos porcentuales</b> de diferencia;
  para la diferencia observada de {POT_DIF_OBS} puntos la potencia es apenas {POT_EN_OBS}. Lo que
  queda descartado es entonces <b>una ventaja de {POT_DELTA80} puntos o más</b>, no una ventaja de
  cualquier tamaño — y la diferencia observada apunta, además, <b>en contra</b> de la propuesta.
  Hay una <b>tendencia</b> a favor de la fusión como técnica —tres comparativos superan al
  visible— pero ninguna diferencia sobrevive la corrección por multiplicidad. El hallazgo acota
  el alcance práctico de la fusión morfológica de realce para esta tarea. El cálculo de potencia
  está en <span class="mono">experiments/potencia_mcnemar.py</span>.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>15. Cuadro comparativo de las metodologías en la prueba de detección</h2>
  <p>Las dos pruebas y el conteo por escena, reunidos por entrada. La tabla es la forma más
  económica de mostrar el resultado central del capítulo: <b>ninguna entrada gana en todo</b>, y el
  orden cambia según la columna que se priorice. En negrita, el mejor valor de cada columna.</p>
  <p><b>Tabla 13.</b> Comparativa de las nueve entradas en la prueba de detección (LLVIP con un
  detector por entrada; M3FD con un único detector e inferencia por entrada; el conteo por escena
  sobre las {M3FD_COMP} escenas que contienen las dos clases complementarias).</p>
  {TAB_DETECCION}
  <p class="lectura">Lectura: los líderes por columna son {DET_LIDERES}. Es decir que la mejor
  entrada depende de la pregunta: si el objetivo es detectar peatones nocturnos, el
  <b>infrarrojo solo</b> es la mejor entrada y ninguna fusión lo alcanza; si el objetivo es sostener
  las dos clases complementarias a la vez, la mejor entrada es una <b>fusión</b>, pero no la
  propuesta. La propuesta queda en la mitad inferior de las fusiones en las dos pruebas, lo que es
  coherente con su perfil: gana en las métricas de actividad de la imagen y cede en las de fidelidad,
  y la tarea posterior no premia la actividad.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>15. Comparativa cualitativa: {DME_N_ESC} escenas en {DME_N_ENT} entradas</h2>
  <p>El cuadro anterior promedia sobre cientos de imágenes y por eso no muestra <i>qué</i> cambia.
  Las figuras que siguen toman escenas concretas y dibujan las detecciones que el <b>mismo</b>
  modelo produce sobre cada entrada, con píxeles idénticos en todo salvo el método de fusión. Dos
  precisiones sobre el diseño de la comparación.</p>

  <p><b>Se agrega la metodología del trabajo de referencia</b>, que no estaba. El comparativo
  «Top-Hat clásico» del benchmark corre con la parametrización manual r = 5 y m = 1; la metodología
  de Ortega y Espinoza (2025) es ese mismo operador de disco único con (r, m) hallados por su PSO, y
  el barrido con su aptitud devuelve r = 25 y m = 0,30 —la misma configuración que la propuesta—, de
  modo que compararlas <b>aísla el banco de cinco elementos frente al disco único</b> a
  hiperparámetros idénticos. Es la ablación del operador, vista sobre la tarea.</p>

  <p><b>Las escenas no se eligen por conveniencia.</b> La regla se declara de antemano y se aplica
  sobre el conteo por escena, e incluye el caso <b>adverso</b> a la propuesta: la escena ya publicada
  —para poder cruzarla con la figura anterior—, la escena con más objetos donde la propuesta recupera
  ambas clases y el visible no, la escena con más objetos donde ocurre lo contrario, y la escena con
  más objetos donde ambas las recuperan.</p>

  <p><b>Tabla 14.</b> Detecciones por entrada y por escena, en el formato <i>personas · luces</i>. En
  el encabezado, la verdad de campo de cada escena. En negrita, los dos operadores morfológicos a
  igual configuración.</p>
  {TAB_DME}
  <p class="lectura">Conviene precisar qué cuentan estos números: son <b>detecciones</b> por encima
  del umbral de confianza, no aciertos emparejados con la verdad de campo. La regla de selección usó
  el conteo de aciertos, de modo que una escena puede aparecer con detecciones de ambas clases sin
  que ambas sean correctas. Un valor de luces <b>mayor</b> que la verdad de campo es, por
  construcción, falso positivo.</p>
  {pie(pg)}
</div>
""")
pg += 1

for _e in DME_ESCENAS:
    _p, _l = DME_GT[_e]
    _g = _dme[_dme.escena == _e]
    _prop = _g[_g.entrada == "Propuesta_Novedosa"].iloc[0]
    _ref = _g[_g.entrada == "Ref_PSO"].iloc[0]
    _vis = _g[_g.entrada == "VIS"].iloc[0]
    _sob = _g[_g.lamp_detectadas > _g.lamp_gt]
    H.append(f"""
<div class="page">
  <h2>15. Comparativa cualitativa (continuación): escena {_e}</h2>
  <p>Criterio de selección: <b>{DME_CRITERIO[_e]}</b>. Verdad de campo: {_p} personas y {_l}
  {'luz' if _l == 1 else 'luces'}.</p>
  {figura(EXIST.get(f"fig_m3fd_detecciones_{_e}.png"),
          f"M3FD, escena {_e}: detecciones del modelo único VIS+IR sobre las {DME_N_ENT} entradas. "
          f"People en granate, Lamp en azul, umbral de confianza 0,30. Verdad de campo: "
          f"{_p} personas y {_l} {'luz' if _l == 1 else 'luces'}.", 100)}
  <p class="lectura">En esta escena el visible solo detecta {int(_vis.people_detectadas)} personas y
  {int(_vis.lamp_detectadas)} luces; la propuesta, {int(_prop.people_detectadas)} y
  {int(_prop.lamp_detectadas)}; y la metodología de la referencia a la misma configuración,
  {int(_ref.people_detectadas)} y {int(_ref.lamp_detectadas)}. La comparación entre estas dos
  últimas es la que aísla el aporte del banco sobre el disco:
  {"el banco detecta más personas" if _prop.people_detectadas > _ref.people_detectadas
   else ("el disco detecta más personas" if _prop.people_detectadas < _ref.people_detectadas
         else "las dos detectan las mismas personas")} y
  {"el banco más luces" if _prop.lamp_detectadas > _ref.lamp_detectadas
   else ("el disco más luces" if _prop.lamp_detectadas < _ref.lamp_detectadas
         else "las mismas luces")}.
  {"Ninguna entrada sobredetecta luces aquí." if not len(_sob) else
   "Sobredetectan luces por encima de la verdad de campo: "
   + ", ".join(f"{r.etiqueta.split(' (')[0]} ({int(r.lamp_detectadas)})" for r in _sob.itertuples())
   + ", lo que es coherente con la tasa de artefactos que Nabf mide sobre la imagen."}</p>
  {pie(pg)}
</div>
""")
    pg += 1

H.append(f"""
<div class="page">
  <h2>16. Conclusiones y encuadre del aporte</h2>
  <p>El trabajo sostiene <b>dos aportes</b>. El primero es el operador y su caracterización; el
  segundo, la auditoría de la validez discriminativa del protocolo con que se lo evalúa, usando el
  propio desarrollo como caso de estudio. Ambos se enuncian a continuación con la evidencia que los
  respalda.</p>

  <h3>Primer aporte: el operador y su punto de operación</h3>
  <ol>
    <li>El operador <b>desplaza el punto de operación de la fusión</b> y no la mejora de manera
        uniforme: contra las cinco configuraciones de referencia gana <b>{_H1_ACT_FAV} de
        {_H1_ACT_TOT}</b> contrastes del bloque de actividad espacial <b>sin ninguno adverso con
        significancia</b>, y
        cede en <b>{_H1_FID_ADV} de {_H1_FID_TOT}</b> del bloque de fidelidad.</li>
    <li>Bajo el criterio del trabajo de referencia <b>encabeza el benchmark</b>: puesto
        {POS_RANK} de 7 con {VAL_RANK}, y conserva el primer puesto al retirar FE, la métrica
        redundante ({_coma(AG_FILAS[1][3], 3)} frente a {_coma(AG_FILAS[1][5], 3)}). El primer
        puesto es sólido <b>dentro</b> de ese criterio, no una propiedad independiente de él: al
        rankear los promedios en lugar de promediar los rangos hay <b>empate</b> con la pirámide
        de Laplace, y con las diecisiete métricas la propuesta pasa a {_POS_17}.ª. Es la
        conclusión 1 vista desde adentro del propio benchmark.</li>
    <li>El resultado es <b>robusto frente al ajuste de los comparativos</b>: dándoles el mismo paso
        de ajuste, <b>ninguna de las cinco configuraciones del estado del arte lo alcanza</b>. El
        Top-Hat clásico lo supera por {f"{abs(VAL_B - VLID_B):.3f}".replace(".", ",")}, pero con m = 1
        frente a m = 0,30: a igual peso, sustituido en el benchmark de siete, la propuesta gana por
        {f"{CTRL_VENTAJA:.3f}".replace(".", ",")}
        ({f"{CTRL_PROP:.3f}".replace(".", ",")} frente a
        {f"{CTRL_TH_M030:.3f}".replace(".", ",")}).</li>
    <li>El <b>banco de cinco elementos aporta sobre el disco único</b> con hiperparámetros
        igualados ({f"{_abl.loc['suma','rango_9']:.3f}".replace(".", ",")} frente a
        {f"{_abl.loc['disco','rango_9']:.3f}".replace(".", ",")}), y el mérito no proviene de la
        imagen base, que queda <b>última</b> de los seis brazos
        ({f"{_abl.loc['base','rango_17']:.3f}".replace(".", ",")}).</li>
    <li>El <b>peso adoptado está justificado por criterios independientes de la aptitud</b>:
        m = 0,30 sobre este operador equivale a m = {f"{M_EQUIV:.2f}".replace(".", ",")} sobre un
        disco único —dentro del rango publicado— y mantiene la saturación en
        {f"{SAT_030:.2f}".replace(".", ",")} % frente al {f"{SAT_100:.2f}".replace(".", ",")} % que
        produciría m = 1.</li>
  </ol>

  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>16. Conclusiones (continuación): el segundo aporte</h2>
  <h3>Segundo aporte: validez discriminativa del protocolo</h3>
  <ol>
    <li>El <b>orden de mérito depende de la composición del conjunto de métricas</b>: con las nueve
        del trabajo la propuesta es {POS_RANK}.ª; con las diecisiete que el mismo evaluador calcula,
        {_POS_17}.ª. No cambia nada del operador ni de las imágenes.</li>
    <li>La batería de nueve <b>no distingue detalle útil de ruido</b>: una fusión artificial de
        ruido gaussiano con σ = 0,20 alcanza el <b>{CN_ORD_RUIDO} puesto entre {CN_ENTRADAS}
        entradas</b>, por delante de {CN_COMPAR_DETRAS} de los seis métodos comparativos, y su
        rango <b>mejora monótonamente</b> al aumentar la varianza. Incorporando Nabf, la única
        métrica con dirección inversa, el control cae como corresponde.</li>
    <li>La batería <b>contiene redundancia</b>: FE es EN reescalada por una constante por escena, de
        modo que produce rangos intra-bloque idénticos y el mismo χ² de Friedman. Las dimensiones
        efectivas son ocho, no nueve.</li>
    <li>La <b>optimización no determina la configuración evaluada</b>, y lo que la determina es el
        <b>rango de búsqueda heredado</b> y no el optimizador: dentro de ese rango el argmax de la
        aptitud es r = {R_PREFERIDO} y el peso queda clavado en su piso, m = 0,30, en el
        {REP_PISO_PCT} % de las corridas. El calificador es necesario: <b>sin la restricción del
        rango el argmax es r = {OE_R_LIBRE}</b> —el radio que esta tesis adopta— con
        m = {OE_M_LIBRE}. Lo que el intervalo ajeno fija por completo es el <b>peso</b>, no el
        radio.</li>
    <li>El <b>orden de calidad no predice el orden de utilidad</b> en la tarea posterior, y
        <b>ninguna fusión supera a la mejor modalidad individual</b>: en el conteo por escena la
        propuesta queda por debajo del visible solo. La hipótesis de que la mejora de calidad se
        traslade a la detección <b>se rechaza</b> para una ventaja de {POT_DELTA80} puntos
        porcentuales o más, que es la resolución que dan los {POT_ND} pares discordantes; la
        diferencia observada es de {POT_DIF_OBS} puntos <b>en contra</b>.</li>
  </ol>
  <p class="lectura">Consecuencia metodológica: un protocolo de evaluación de fusión debería incluir
  al menos una métrica que <b>penalice artefactos</b>, declarar la <b>redundancia</b> entre sus
  componentes, y <b>separar el ajuste de hiperparámetros del criterio de evaluación</b>. Este
  trabajo aporta los tres controles que lo verifican, versionados y reproducibles.</p>

  <h3>Próximos pasos</h3>
  <ul>
    <li>Incorporar al conjunto de evaluación al menos una métrica sensible a artefactos y repetir el
        benchmark con la batería ampliada.</li>
    <li>Aislar el aporte del banco con un ajuste de hiperparámetros simétrico para todos los
        operadores morfológicos.</li>
    <li>Extender la evaluación de detección a otros detectores y a más semillas de entrenamiento.</li>
    <li>Complementar con una validación perceptual por observadores.</li>
  </ul>
  {pie(pg)}
</div>
""")

pg += 1

# ---------- Anexos 1-20: las 25 configuraciones del PSO en cada escena ----------
_nota_anexo = f"""
  <p class="lectura">Nota metodológica sobre el comportamiento de (r, m). Las 25 configuraciones de
  cada escena se ejecutan sobre el mismo espacio de búsqueda r &isin; [1, 25], m &isin; {V['rango_anexo']}.
  El <b>radio sí varía</b> con la configuración del enjambre: en el conjunto de los anexos aparecen
  {_R_DISTINTOS} radios distintos y entre {_R_POR_PAR_LO} y {_R_POR_PAR_HI} valores diferentes por
  par. El <b>peso, en cambio, se fija en
  m = {_m_moda}</b> (en {_m30} de {N_ESC} pares) porque F<sub>o</sub> <b>decrece de forma estrictamente
  monótona</b> al aumentar m en todo el rango publicado —verificado con un barrido de paso 0,05: cero
  tramos crecientes en 34, tanto con r = 1 como con r = 25—, de modo que el máximo se ubica
  necesariamente en el <b>límite inferior del intervalo</b>. No es una limitación de la búsqueda: las
  únicas {_n_no_borde} filas (de 500) con m &ne; {_m_moda} corresponden a configuraciones de pocas partículas o
  iteraciones que no alcanzaron el óptimo. <b>Dentro de este rango de búsqueda</b> el radio que
  maximiza F<sub>o</sub> es r = 1 en {_r1} de {N_ESC} imágenes, coherente con que la aptitud premia la
  fidelidad a las fuentes y por lo tanto el mínimo realce. El calificador importa y la sección 5 lo
  desarrolla: <b>sin la restricción del rango heredado el argmax de F<sub>o</sub> es r = 25</b>, con
  m = {OE_M_LIBRE} y F<sub>o</sub> = {OE_FO_LIBRE}, de modo que r = 1 es el óptimo del intervalo
  ajeno y no de la aptitud. La configuración adoptada (<b>r = 25</b>) no proviene de F<sub>o</sub>
  restringida sino del criterio de
  evaluación de esta tesis —las nueve métricas, todas de tipo «mayor es mejor»—, que a igual peso
  favorece el radio máximo, sin que r = 1 desactive el banco: como se precisa en la sección 5, con
  r = 1 el disco es la cruz de 3×3 y las cuatro líneas orientadas son cuatro máscaras 3×3 distintas,
  de modo que los cinco elementos siguen operativos.</p>"""

for _i, _img in enumerate(IMAGENES, 1):
    _nom = ESCENA.get(_img, _img)
    H.append(f"""
<div class="page">
  <h2>Anexo {_i}: resultados para {_nom}</h2>
  <p><b>Cuadro A{_i}.</b> Resultados experimentales para la imagen <i>{_nom}</i> — las 25
  configuraciones del PSO (partículas × iteraciones, Cuadro 1 de Ortega y Espinoza 2025) con la
  aptitud F<sub>o</sub> sobre el rango publicado r &isin; [1, 25], m &isin; [0,30; 2,00]. En negrita
  la configuración de mayor aptitud.</p>
  {tabla_anexo(_img)}
  {_nota_anexo if _i == 1 else ""}
  {pie(pg)}
</div>
""")
    pg += 1

html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Presentación de avances — Fusión IR/VIS</title><style>{css}</style></head>
<body>{''.join(H)}</body></html>"""
with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("HTML:", HTML_OUT, f"{os.path.getsize(HTML_OUT)/1e6:.1f} MB")

# ------------------------------------------------------------------ HTML -> PDF (Edge headless)
import subprocess
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE):
    EDGE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
if os.path.exists(EDGE):
    subprocess.run([EDGE, "--headless", "--disable-gpu",
                    f"--print-to-pdf={PDF_OUT}", "--no-pdf-header-footer",
                    HTML_OUT], capture_output=True, timeout=300)
    if os.path.exists(PDF_OUT):
        print("PDF:", PDF_OUT, f"{os.path.getsize(PDF_OUT)/1e6:.1f} MB")
    else:
        print("AVISO: Edge no genero el PDF; reintentar o imprimir el HTML con Ctrl+P.")
else:
    print("AVISO: Edge no encontrado; imprimir el HTML a PDF manualmente (Ctrl+P, A4).")
