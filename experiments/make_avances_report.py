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
_fus = det.drop(index=[x for x in ("VIS", "IR") if x in det.index])
LLVIP_PROP = f"{det.loc[PROP, 'mAP50']:.3f}".replace(".", ",")
LLVIP_LO = f"{_fus['mAP50'].min():.3f}".replace(".", ",")
LLVIP_HI = f"{_fus['mAP50'].max():.3f}".replace(".", ",")
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


# Lectura de la Tabla 10 construida desde los datos: cada afirmacion se verifica antes de
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
    LECTURA_PSO = (
        "Lectura: las <b>25 configuraciones convergen al mismo peso óptimo, m* = 0,30</b>, el límite "
        "inferior del rango publicado, porque los dos términos de fidelidad de F<sub>o</sub> "
        "(SSIM<sub>avg</sub> y PSNR<sub>n</sub>) decrecen al aumentar el realce y dominan sobre la "
        "entropía normalizada; se verificó que F<sub>o</sub> decrece de forma estrictamente monótona en "
        "m sobre todo el rango, de manera que el óptimo del peso está forzado por la forma de la "
        "aptitud y no es un artefacto del enjambre. "
        "<b>El radio, en cambio, no lo fija el PSO:</b> dentro de este rango la aptitud F<sub>o</sub> "
        f"prefiere r = {R_PREFERIDO} ({FO_MEJOR} frente a {FO_R25} en r = 25), de modo que r = 25 es una "
        "<b>decisión de diseño</b> tomada sobre las métricas de evaluación y no el resultado de la "
        "optimización. De las nueve métricas, <b>cinco favorecen r = 25</b> (EN, SD, FE, MG y SF) y "
        "las <b>cuatro de fidelidad favorecen r = 1</b> (SSIM, PSNR, MI<sub>vis</sub> y "
        "MI<sub>ir</sub>), todas con p &lt; 10<sup>-5</sup>. Se adopta <b>r = 25, m = 0,30</b> "
        "priorizando la capacidad de realce, y se reconoce que la elección del radio se apoya en parte "
        "del mismo criterio con el que luego se evalúa.")
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
    "comparacion_aptitudes.png"]}
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
    <li>Resultados cualitativos de las {N_ESC} escenas (sección 11).</li>
    <li>Evaluación orientada a tarea: detección en LLVIP (sección 12) y clases complementarias en
        M3FD (sección 13), y conclusiones (sección 14).</li>
    <li>Anexos 1-{N_ESC}: las 25 configuraciones del PSO en cada una de las {N_ESC} escenas.</li>
  </ol>
  {pie(2)}
</div>
""")

# Bloques calculados sobre el largo real, no recortados a 20 a mano.
chunks = [pairs_html[i:i + 8] for i in range(0, len(pairs_html), 8)]
H.append(f"""
<div class="page">
  <h2>2. Datos de entrada: {N_ESC} pares VIS/IR (TNO)</h2>
  <p>Se trabaja con los {N_ESC} pares registrados del TNO Image Fusion Dataset (escenas de vigilancia
  nocturna: vehículos, personas, humo). Cada escena tiene una imagen visible (VIS), que aporta textura y
  contexto, y una infrarroja (IR), que registra la radiación térmica. Ambas comparten nombre de archivo
  para el emparejado automático. Sobre estos {N_ESC} pares se calculan todas las métricas del informe.</p>
  <p class="lectura">Nota sobre el corpus: el conjunto original contiene 21 archivos emparejables, pero
  el par <i>Athena_heather_IR_hei_vis_g</i> se <b>excluye</b> porque su archivo del canal visible es una
  copia byte a byte del infrarrojo (mismo md5), de modo que no es un par VIS/IR sino la misma imagen
  repetida. Con VIS = IR el error cuadrático medio es nulo y todo método que devuelva la entrada sin
  modificarla obtiene SSIM = 1 y un PSNR que desborda la escala, lo que inflaba artificialmente los
  promedios de fidelidad de los métodos multiescala. El corpus efectivo es de <b>{N_ESC} pares</b>.</p>
  <div class="grid2">{"".join(chunks[0])}</div>
  {pie(3)}
</div>
<div class="page">
  <h2>2. Datos de entrada (continuación)</h2>
  <div class="grid2">{"".join(chunks[1])}</div>
  {pie(4)}
</div>
<div class="page">
  <h2>2. Datos de entrada (continuación)</h2>
  <div class="grid2">{"".join(chunks[2])}</div>
  {pie(5)}
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
  {pie(6)}
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
  {pie(7)}
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
  {pie(8)}
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
  {pie(9)}
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
  {pie(10)}
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

  <p><b>Segundo, el rango proviene del trabajo de referencia.</b> El intervalo m &isin; [0,30; 2,00]
  es el espacio de búsqueda publicado por Ortega y Espinoza (2025). Adoptarlo es lo que hace
  comparable este trabajo con aquel: m = 0,30 es el valor que <i>su</i> función de aptitud selecciona
  dentro de <i>su</i> rango.</p>

  <p><b>Tercero, y es el argumento central: la equivalencia del realce físico.</b> El realce que
  efectivamente se inyecta en la reconstrucción no es m, sino el producto <b>m · |W|</b> del peso por
  la energía de detalle que extrae el operador. El banco de cinco elementos estructurantes extrae
  {f"{W_PROP:.4f}".replace(".", ",")} frente a {f"{W_CLAS:.4f}".replace(".", ",")} del disco único de
  la metodología clásica, es decir <b>{f"{GANANCIA:.2f}".replace(".", ",")} veces más energía</b>. Por
  lo tanto un mismo peso no produce el mismo realce en ambos operadores, y comparar los valores de m
  sin corregir por esa ganancia es comparar unidades distintas. Corrigiendo:</p>
  <ul>
    <li>m = 0,30 sobre el banco propuesto equivale a <b>m = {f"{M_EQUIV:.2f}".replace(".", ",")}</b>
        sobre un disco único, valor que cae <b>dentro</b> del rango publicado [0,30; 2,00], al
        {f"{POS_EN_RANGO:.0f}"} % de su recorrido y a
        {f"{abs(M_EQUIV - 1.0):.2f}".replace(".", ",")} del peso canónico m = 1 de la metodología
        clásica.</li>
    <li>A la inversa, el rango publicado <b>traducido</b> a este operador preservando el realce
        físico es [{f"{RANGO_LO:.4f}".replace(".", ",")}; {f"{RANGO_HI:.4f}".replace(".", ",")}], y
        m = 0,30 cae dentro de ese intervalo.</li>
  </ul>
  <p>Es decir que el peso adoptado <b>no es un valor bajo</b>: es el que reproduce el realce físico
  del rango publicado una vez corregida la diferencia de energía entre los dos operadores. Parece bajo
  únicamente si se olvida que el operador cambió.</p>
  {pie(11)}
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
  {pie(12)}
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
  {pie(13)}
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
  se verificó con un control negativo en el que una fusión artificial de ruido gaussiano alcanza el
  segundo puesto entre ocho entradas con σ &ge; 0,10, por delante de los seis métodos comparativos, y
  cuyo rango mejora de forma monótona al aumentar la varianza. Los resultados de las secciones
  siguientes deben leerse con ese alcance.</p>
  {pie(14)}
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
  {pie(15)}
</div>
""")

# ---------- 8 (continuación): resultados escena por escena, formato del Cuadro 2 ----------
_bloques = [IMAGENES[i:i + 4] for i in range(0, len(IMAGENES), 4)]   # 4 escenas por pagina
for _b, _imgs in enumerate(_bloques, 1):
    _cab = ("8. Resultados por escena (formato del Cuadro 2 del trabajo de referencia)"
            if _b == 1 else f"8. Resultados por escena (continuación {_b} de 5)")
    _intro = ("" if _b > 1 else f"""
  <p>Además de los promedios, se detallan los resultados <b>escena por escena</b> sobre los {N_ESC} pares
  del TNO, con la misma disposición del Cuadro 2 del trabajo de referencia: una fila por método dentro
  de cada escena y, en <b>negrita</b>, el mejor valor de cada columna en esa escena. Se incluye también
  la metodología clásica Top-Hat, que es la referencia morfológica directa de la propuesta.</p>
  <p class="lectura">Unidades: SSIM<sub>avg</sub> y SD en [0, 1]; E en bits (0–8); SF adimensional;
  PSNR en dB. La correspondencia con el Cuadro 2 de referencia es directa —allí E y PSNR se reportan
  normalizados (E/8 y PSNR/100) y SD en la escala 0–255—, de modo que el orden entre métodos es
  comparable columna por columna.</p>""")
    _lect = ("" if _b < 5 else f"""
  <p class="lectura">Lectura del conjunto de las {N_ESC} escenas: la propuesta obtiene el mejor valor en
  <b>{_lidera['E']} de {N_ESC}</b> escenas en entropía (E) y en <b>{_lidera['SD']} de {N_ESC}</b> en desviación
  estándar (SD), frente a <b>{_lidera['SF']} de {N_ESC}</b> en frecuencia espacial (SF, donde domina el
  Top-Hat clásico), <b>{_lidera['SSIM_avg']} de {N_ESC}</b> en SSIM<sub>avg</sub> y
  <b>{_lidera['PSNR']} de {N_ESC}</b> en PSNR. El patrón por escena confirma el de los promedios: la
  propuesta lidera de forma sistemática las métricas de información y contraste, y cede las de
  fidelidad a las fuentes.</p>""")
    H.append(f"""
<div class="page">
  <h2>{_cab}</h2>{_intro}
  <p><b>Tabla 4{chr(96 + _b)}.</b> Resultados por escena — escenas {(_b - 1) * 4 + 1} a
  {(_b - 1) * 4 + len(_imgs)} de {N_ESC}.</p>
  {tabla_por_imagen(_imgs)}{_lect}
  {pie(15 + _b)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>9. Análisis estadístico</h2>
  <p>Primero, el test de Friedman (7 métodos × {N_ESC} imágenes, por rangos) para cada métrica:</p>
  {formula("friedman", 23)}
  <p><b>Tabla 5.</b> Resultados del test de Friedman.</p>
  {tabla_friedman()}
  {pie(21)}
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
  {pie(22)}
</div>
""")

pg = 23
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
  <h2>11. Resultados cualitativos: las {N_ESC} escenas</h2>
  <p>Para cada escena se muestran las fuentes VIS e IR, los seis comparativos y la propuesta (recuadro
  rojo). Se sugiere observar: la visibilidad del objetivo térmico, la conservación de la textura del
  fondo visible y la ausencia de halos en los bordes.</p>
  {mont_html[0]}
  {mont_html[1]}
  {pie(pg)}
</div>
""")
pg += 1
for i in range(2, N_ESC, 2):
    blk = mont_html[i] + (mont_html[i + 1] if i + 1 < N_ESC else "")
    H.append(f'<div class="page"><h2>11. Resultados cualitativos (escenas {i+1} y {min(i+2,N_ESC)} de {N_ESC})</h2>'
             f'{blk}{pie(pg)}</div>')
    pg += 1

H.append(f"""
<div class="page">
  <h2>12. Evaluación orientada a tarea: detección en LLVIP</h2>
  <p>Para medir el efecto práctico de la fusión se reentrenó el mismo detector <b>YOLOv8n</b> (40 épocas,
  misma configuración y semilla) sobre cada versión fusionada del dataset etiquetado <b>LLVIP</b>
  (peatones nocturnos; subconjunto de 2.000 imágenes de entrenamiento y 500 de validación). Como los
  pares VIS/IR están registrados, las anotaciones valen para toda versión fusionada: la diferencia de
  mAP aísla el efecto del método de fusión.</p>
  <p><b>Tabla 9.</b> Detección de peatones en LLVIP — mAP por entrada del detector.</p>
  {tabla_det()}
  <p class="lectura">Lectura: toda fusión supera con claridad al visible solo (mAP@0,5 de 0,808 a la banda
  {LLVIP_LO}–{LLVIP_HI}); el infrarrojo solo es la modalidad más fuerte (0,957) y ninguna
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
  <h2>13. Detección con clases complementarias (M3FD)</h2>
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
  <p><b>Tabla 10.</b> AP@0,5 por clase y mAP global (medias sobre las {M3_N} imágenes de la partición
  de prueba, disjunta de la de entrenamiento y de la de selección del modelo).</p>
  {TAB_M3FD}
  <p class="lectura">{LECTURA_M3FD}</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>13. Clases complementarias (continuación): la prueba visual</h2>
  <p>{PARRAFO_DETECCIONES}</p>
  {figura(EXIST.get("fig_m3fd_detecciones.png"), PIE_DETECCIONES, 92)}
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>13. Clases complementarias (continuación): el objetivo medido por escena</h2>
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
  <p><b>Tabla 11.</b> Recuperación de ambas clases complementarias por escena. Las
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
  <p><b>Conclusión sobre el objetivo declarado.</b> La hipótesis de que una mejor calidad de
  fusión se traduzca en la detección de objetos complementarios <b>se rechaza</b> para el método
  propuesto, y con muestra suficiente: no queda como resultado no concluyente por falta de datos.
  Hay una <b>tendencia</b> a favor de la fusión como técnica —tres comparativos superan al
  visible— pero ninguna diferencia sobrevive la corrección por multiplicidad. El hallazgo acota
  el alcance práctico de la fusión morfológica de realce para esta tarea.</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>14. Conclusiones y encuadre del aporte</h2>
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
        {POS_RANK} de 7 con {VAL_RANK}, con separación estadísticamente significativa.</li>
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
  <h2>14. Conclusiones (continuación): el segundo aporte</h2>
  <h3>Segundo aporte: validez discriminativa del protocolo</h3>
  <ol>
    <li>El <b>orden de mérito depende de la composición del conjunto de métricas</b>: con las nueve
        del trabajo la propuesta es {POS_RANK}.ª; con las diecisiete que el mismo evaluador calcula,
        {_POS_17}.ª. No cambia nada del operador ni de las imágenes.</li>
    <li>La batería de nueve <b>no distingue detalle útil de ruido</b>: una fusión artificial de
        ruido gaussiano alcanza el segundo puesto entre ocho entradas con σ &ge; 0,10, por delante de
        los seis métodos comparativos, y su rango <b>mejora monótonamente</b> al aumentar la
        varianza. Incorporando Nabf, la única métrica con dirección inversa, el control cae como
        corresponde.</li>
    <li>La batería <b>contiene redundancia</b>: FE es EN reescalada por una constante por escena, de
        modo que produce rangos intra-bloque idénticos y el mismo χ² de Friedman. Las dimensiones
        efectivas son ocho, no nueve.</li>
    <li>La <b>optimización no determina la configuración evaluada</b>: el argmax de la aptitud es
        r = {R_PREFERIDO} y el peso queda en el piso del rango de búsqueda.</li>
    <li>El <b>orden de calidad no predice el orden de utilidad</b> en la tarea posterior, y
        <b>ninguna fusión supera a la mejor modalidad individual</b>: en el conteo por escena la
        propuesta queda por debajo del visible solo. La hipótesis de que la mejora de calidad se
        traslade a la detección <b>se rechaza</b>, con muestra suficiente.</li>
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
  El <b>radio sí varía</b> con la configuración del enjambre: en el conjunto de los anexos aparecen 18
  radios distintos y entre 2 y 6 valores diferentes por escena. El <b>peso, en cambio, se fija en
  m = {_m_moda}</b> (en {_m30} de {N_ESC} escenas) porque F<sub>o</sub> <b>decrece de forma estrictamente
  monótona</b> al aumentar m en todo el rango publicado —verificado con un barrido de paso 0,05: cero
  tramos crecientes en 34, tanto con r = 1 como con r = 25—, de modo que el máximo se ubica
  necesariamente en el <b>límite inferior del intervalo</b>. No es una limitación de la búsqueda: las
  únicas {_n_no_borde} filas (de 500) con m &ne; {_m_moda} corresponden a configuraciones de pocas partículas o
  iteraciones que no alcanzaron el óptimo. El radio que maximiza F<sub>o</sub> es r = 1 en {_r1} de {N_ESC}
  imágenes, coherente con que la aptitud premia la fidelidad a las fuentes y por lo tanto el mínimo
  realce; la configuración adoptada (<b>r = 25</b>) no proviene de F<sub>o</sub> sino del criterio de
  evaluación de esta tesis —las nueve métricas, todas de tipo «mayor es mejor»—, que a igual peso
  favorece el radio máximo y activa el banco completo de cinco elementos estructurantes.</p>"""

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
