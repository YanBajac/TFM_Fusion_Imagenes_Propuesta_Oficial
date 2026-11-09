# -*- coding: utf-8 -*-
"""Genera las tablas del libro (docs/libro_v4) en LaTeX, directo desde los CSV de resultados.

POR QUE UN GENERADOR. Cada tabla se escribe sola desde el CSV que la respalda, y el capitulo la
trae con \\input. Si un resultado cambia, se vuelve a correr esto y el libro queda al dia sin tocar
el texto.

Salida: docs/libro_v4/tablas/*.tex  (fragmentos, cada uno es un entorno table completo, salvo la tabla
        de los anexos, que ocupa mas de una pagina y es una longtable)

Convenciones de formato que se respetan aca:
  - el rotulo va ARRIBA de la tabla y es un titulo breve, sin punto final: es lo que entra al
    indice de tablas. Las aclaraciones van en la nota de abajo, con \\nota{...} (lo define main.tex);
  - se numeran por capitulo (Tabla 4.1, 4.2, ...), lo hace LaTeX solo;
  - las celdas van en el cuerpo del texto, sin \\small, y el encabezado de columnas en negrita;
  - la negrita marca solo el mejor valor; la fila de la propuesta se senala en la nota;
  - punto decimal, como en el resto del libro, y los intervalos como [a, b];
    los miles, sin separador;
  - reglas horizontales de booktabs, sin lineas verticales.

Uso: .venv\\Scripts\\python.exe -X utf8 tools/generar_tablas_libro.py
"""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
REP = RAIZ / "experiments" / "results" / "metrics_reports"
SAL = RAIZ / "docs" / "libro_v4" / "tablas"

# «Curvelet» es el nombre del metodo en el codigo y en los CSV, pero es una DWT con base de
# Daubechies de orden cuatro, no la transformada curvelet. El libro lo llama por lo que es.
CORTO = {"PiramideLaplace": "Pirámide de Laplace", "RatioPiramide": "Pirámide de razón",
         "DWT": "DWT (Haar)", "DTCWT": "DTCWT", "Curvelet": "DWT (db4)",
         "TopHat_Clasico": "Top-Hat clásico", "Propuesta_Novedosa": "Propuesta",
         "VIS": "Visible sola", "IR": "Infrarroja sola", "Promedio": "Promedio simple"}


def num(v, nd=3):
    """Numero con punto decimal, que es lo que usa el resto del libro."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""  # sin dato: celda vacia, porque el libro no usa rayas
    t = f"{v:.{nd}f}"
    # el signo menos, no el guion: en modo texto «-7.9» se imprime con un guion corto
    return "$-$" + t[1:] if t.startswith("-") else t


def pvalor(p):
    """p-valores legibles. Debajo de 0.001 no se publica el digito, se publica «< 0.001»."""
    if p < 0.001:
        return "$< 0.001$"
    return num(p, 3)


def tabla(nombre, cuerpo):
    destino = SAL / f"{nombre}.tex"
    destino.write_text(cuerpo, encoding="utf-8", newline="\n")
    print(f"  {destino.relative_to(RAIZ)}")


# La fila de la propuesta no va en negrita: la negrita queda para el mejor valor, y la nota dice
# cual es la fila de la propuesta.
PROPUESTA = "Propuesta: el algoritmo de fusión presentado en este trabajo."


def bf(celda):
    """Una celda de encabezado en negrita. Si lleva matematicas, con \\boldmath, para que $p$ o
    $\\chi^2$ salgan en negrita como el resto del encabezado."""
    c = celda.strip()
    if not c:
        return c
    return rf"\textbf{{\boldmath {c}}}" if "$" in c else rf"\textbf{{{c}}}"


def encabezar(*celdas):
    return " & ".join(bf(c) for c in celdas)


def negrita_si(texto, condicion):
    return rf"\textbf{{{texto}}}" if condicion else texto


def envolver(etiqueta, rotulo, columnas, encabezado, filas, nota=None, previo=None):
    assert not rotulo.rstrip().endswith("."), f"el rotulo de tab:{etiqueta} no lleva punto final"
    n = "\n"
    cuerpo = [
        r"\begin{table}[htbp]", r"\centering",
        rf"\caption{{{rotulo}}}", rf"\label{{tab:{etiqueta}}}",
    ]
    # previo: ajustes que valen solo dentro de esta tabla, como una separacion de columnas menor
    cuerpo += list(previo or [])
    cuerpo += [
        rf"\begin{{tabular}}{{{columnas}}}", r"\toprule",
        encabezado + r" \\", r"\midrule",
    ]
    cuerpo += [f + r" \\" for f in filas]
    cuerpo += [r"\bottomrule", r"\end{tabular}"]
    if nota:
        cuerpo += [rf"\nota{{{nota}}}"]
    cuerpo += [r"\end{table}", ""]
    return n.join(cuerpo)


def envolver_larga(etiqueta, rotulo, columnas, encabezado, bloques, nota, previo=None):
    """Una tabla que no entra en una pagina: longtable, que se corta entre paginas y repite el rotulo
    (con «continuación») y el encabezado de columnas en cada una. El \\caption y el \\label van dentro,
    para que entre al indice de tablas con el mismo numero en todas las paginas.

    bloques: lista de grupos de filas que no se separan entre paginas. Dentro de un grupo las filas
    terminan en \\\\* (sin corte de pagina); el corte solo puede caer entre un grupo y el siguiente.

    Va dentro de un grupo de llaves por tres ajustes locales: interlineado simple, que setspace pone
    solo en los flotantes y la longtable no lo es; \\LTpost en cero, para que la nota quede a la misma
    distancia que en las demas tablas; y lo que traiga «previo».
    """
    assert not rotulo.rstrip().endswith("."), f"el rotulo de tab:{etiqueta} no lleva punto final"
    cabeza = [r"\toprule", encabezado + r" \\", r"\midrule"]
    cuerpo = [r"{" + "".join([r"\setstretch{1}", r"\setlength{\LTpost}{0pt}"] + list(previo or [])),
              rf"\begin{{longtable}}{{{columnas}}}",
              rf"\caption{{{rotulo}}}\label{{tab:{etiqueta}}} \\"]
    cuerpo += cabeza + [r"\endfirsthead", rf"\caption[]{{{rotulo} (continuación)}} \\"]
    cuerpo += cabeza + [r"\endhead", r"\bottomrule", r"\endfoot"]
    for i, filas in enumerate(bloques):
        for j, f in enumerate(filas):
            antes = r"\addlinespace " if i > 0 and j == 0 else ""
            cuerpo.append(antes + f + (r" \\*" if j < len(filas) - 1 else r" \\"))
    cuerpo += [r"\end{longtable}", rf"\nota{{{nota}}}", r"}", ""]
    return "\n".join(cuerpo)


# ------------------------------------------------------------------ 1. medias
def medias_seis():
    d = pd.read_csv(REP / "descriptive_means_seis.csv").set_index("method")
    orden = pd.read_csv(REP / "ranking_seis_metricas.csv", index_col=0).index.tolist()
    decimales = {"EN": 4, "SD": 4, "MG": 4, "MI": 4, "SSIM": 4, "PSNR": 2}
    mejor = {m: d[m].idxmax() for m in decimales}
    filas = []
    for k in orden:
        celdas = []
        for m, nd in decimales.items():
            v = num(float(d.loc[k, m]), nd)
            celdas.append(rf"\textbf{{{v}}}" if mejor[m] == k else v)
        filas.append(f"{CORTO[k]} & " + " & ".join(celdas))
    return envolver(
        "medias_seis",
        "Media de las seis métricas por método, sobre los veinte pares del corpus",
        "lcccccc",
        encabezar("Método", "EN", "SD", "MG", "MI", "SSIM", "PSNR"),
        filas,
        nota="Elaboración propia. En las seis métricas, un valor mayor es mejor, y la negrita marca "
             "el mejor valor de cada columna. "
             "Los métodos siguen el orden del rango promedio (Tabla~\\ref{tab:ranking_seis}). "
             "EN: entropía. SD: desviación estándar. MG: gradiente medio. MI: información mutua. "
             "SSIM: similitud estructural. En MI y en SSIM, el valor es el promedio del calculado "
             "contra la imagen visible y del calculado contra la infrarroja. PSNR: relación "
             "señal-ruido de pico, en decibelios, calculada con el promedio de los dos errores "
             "cuadráticos medios. "
             "DWT (Haar) y DWT (db4) son la misma transformada con dos bases distintas "
             "(Sección~\\ref{sec:comparativos}). " + PROPUESTA)


# ----------------------------------------------------------------- 2. ranking
def ranking_seis():
    d = pd.read_csv(REP / "ranking_seis_metricas.csv", index_col=0)
    # el mejor rango global es el menor; se compara la cifra impresa, para marcar los empates
    impresos = {k: num(float(f["rango_6"]), 3) for k, f in d.iterrows()}
    minimo = float(d["rango_6"].min())
    mejor = {k for k, f in d.iterrows() if impresos[k] == num(minimo, 3)}
    filas = []
    for k, f in d.iterrows():
        celdas = [num(float(f[m]), 2) for m in ["EN", "SD", "MG", "MI", "SSIM", "PSNR"]]
        filas.append(f"{int(f['puesto'])} & {CORTO[k]} & " + " & ".join(celdas)
                     + " & " + negrita_si(impresos[k], k in mejor))
    return envolver(
        "ranking_seis",
        "Rango promedio de cada método, por métrica y global",
        "clccccccc",
        encabezar("Puesto", "Método", "EN", "SD", "MG", "MI", "SSIM", "PSNR", "Global"),
        filas,
        nota="Elaboración propia. En cada par y en cada métrica, el rango 1 corresponde al mejor "
             "método. Cada columna de métrica promedia esos rangos sobre los pares, y la columna "
             "Global promedia las seis columnas de métrica. Un valor menor es mejor, y la negrita "
             "marca el mejor rango global. La prueba de Friedman opera sobre estos mismos rangos. "
             + PROPUESTA)


# ---------------------------------------------------------------- 3. Friedman
def friedman_seis():
    d = pd.read_csv(REP / "friedman_seis_metricas.csv")
    filas = [f"{f['metric']} & {num(float(f['chi2']), 1)} & {pvalor(float(f['p_value']))} & "
             + ("sí" if f["significant_05"] else "no") for _, f in d.iterrows()]
    return envolver(
        "friedman_seis",
        "Prueba de Friedman por métrica, con siete métodos y veinte pares",
        "lccc",
        encabezar("Métrica", r"$\chi^2$", "$p$", "¿Difieren?"),
        filas,
        nota="Elaboración propia. La prueba contrasta si los rangos promedio de los métodos difieren "
             "más de lo esperable por azar. Con siete métodos, tiene seis grados de libertad. "
             "La columna ¿Difieren? indica si la diferencia fue significativa, como ocurrió en las "
             "seis métricas. En ese caso, algunos métodos quedan mejor o peor ubicados de forma "
             "sistemática, par tras par.")


# ---------------------------------------------------------------- 4. Wilcoxon
def decision(diff, significativo):
    """La regla de las dos tablas de Wilcoxon, para el primer metodo del contraste: gana o pierde segun
    el signo de la diferencia si el contraste es significativo al 5 % despues de Holm, y empata si no lo
    es. Vale tal cual porque en las seis metricas mayor es mejor."""
    if not significativo:
        return "empata"
    assert diff != 0, "un contraste significativo con diferencia nula"
    return "gana" if diff > 0 else "pierde"


def wilcoxon_resumen():
    d = pd.read_csv(REP / "wilcoxon_seis_metricas.csv")
    prop = d[d["morfologico"] == "Propuesta_Novedosa"]
    sota = prop[prop["comparativo"] != "TopHat_Clasico"]
    th = prop[prop["comparativo"] == "TopHat_Clasico"].set_index("metric")
    filas = []
    for m in ["EN", "SD", "MG", "MI", "SSIM", "PSNR"]:
        b = sota[sota["metric"] == m]
        gana = int(((b["diff"] > 0) & b["sig_holm_05"]).sum())
        pierde = int(((b["diff"] < 0) & b["sig_holm_05"]).sum())
        f = th.loc[m]
        contra = decision(float(f["diff"]), bool(f["sig_holm_05"]))
        filas.append(f"{m} & {gana} & {pierde} & {5 - gana - pierde} & {contra} & "
                     f"{num(float(f['diff']), 4)} & {pvalor(float(f['p_holm']))}")
    return envolver(
        "wilcoxon_resumen",
        "Contrastes de Wilcoxon pareados de la propuesta frente a los demás métodos",
        "lccclcc",
        # encabezado de dos filas: cada grupo de columnas con su nombre, y cada columna con el suyo
        r"& \multicolumn{3}{c}{" + bf("Contra los cinco multiescala") + r"} & \multicolumn{3}{c}{"
        + bf("Contra el Top-Hat clásico") + r"} \\"
        "\n" r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}"
        "\n" + encabezar("Métrica", "Gana", "Pierde", "Empata", "Resultado", "Diferencia",
                         "$p$ corregido"),
        filas,
        nota="Elaboración propia. Gana, Pierde y Empata cuentan los contrastes de la propuesta con "
             "los cinco métodos multiescala. Resultado, Diferencia y $p$ corregido se refieren a su "
             "contraste con el Top-Hat clásico. "
             "Un contraste significativo al 5~\\% después de corregir por comparaciones múltiples, "
             "con Holm sobre los once contrastes de cada métrica, cuenta como victoria o derrota de "
             "la propuesta según el signo de la diferencia de medias. Uno no significativo cuenta "
             "como empate. "
             "Diferencia: media de la propuesta menos media del Top-Hat clásico, en las unidades "
             "de cada métrica (decibelios en PSNR). "
             "El Top-Hat clásico se usó con radio 5 y peso 1.",
        # con la separacion por omision el encabezado agrupado se sale 2.5 pt del margen
        previo=[r"\setlength{\tabcolsep}{5pt}"])


# ------------------------------------------------- 4b. Wilcoxon completo, anexo
METRICA = {"EN": "Entropía", "SD": "Desviación estándar", "MG": "Gradiente medio",
           "MI": "Información mutua", "SSIM": "Similitud estructural",
           "PSNR": "Relación señal-ruido de pico"}
MULTIESCALA = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet"]


def wilcoxon_completa():
    """Los 66 contrastes de Wilcoxon, uno por fila: seis metricas por once contrastes. La tabla resumen
    muestra solo los de la propuesta; esta agrega los del Top-Hat clasico contra los multiescala.

    La ultima columna repite la decision con las trece escenas como bloques, de
    sensibilidad_escenas_wilcoxon.csv (run_sensibilidad_escenas.py), con la misma regla.
    """
    d = pd.read_csv(REP / "wilcoxon_seis_metricas.csv")
    s = pd.read_csv(REP / "sensibilidad_escenas_wilcoxon.csv")
    clave = ["metric", "morfologico", "comparativo"]
    d = d.merge(s[clave + ["diff_20", "sig_20", "diff_13", "sig_13"]], on=clave, how="left",
                validate="one_to_one")
    assert d["sig_13"].notna().all(), "hay contrastes sin su version con trece escenas"
    # la sensibilidad copia los valores de veinte pares: si no coinciden, uno de los dos CSV quedo viejo
    assert (d["diff_20"].round(4) == d["diff"].round(4)).all(), "difieren las diferencias de 20 pares"
    assert (d["sig_20"].astype(bool) == d["sig_holm_05"].astype(bool)).all()
    orden = ([("Propuesta_Novedosa", "TopHat_Clasico")]
             + [("Propuesta_Novedosa", k) for k in MULTIESCALA]
             + [("TopHat_Clasico", k) for k in MULTIESCALA])
    d = d.set_index(clave)
    assert set(d.index) == {(m, a, b) for m in METRICA for a, b in orden}, "no son los 66 contrastes"
    bloques = []
    for m, nombre in METRICA.items():
        filas = [rf"\multicolumn{{6}}{{l}}{{\textit{{{nombre} ({m})}}}}"]
        for a, b in orden:
            f = d.loc[(m, a, b)]
            filas.append(f"{CORTO[a]} & {CORTO[b]} & {num(float(f['diff']), 4)} & "
                         f"{pvalor(float(f['p_holm']))} & "
                         f"{decision(float(f['diff']), bool(f['sig_holm_05']))} & "
                         f"{decision(float(f['diff_13']), bool(f['sig_13']))}")
        bloques.append(filas)
    return envolver_larga(
        "wilcoxon_completa",
        "Contrastes de Wilcoxon pareados de las seis métricas, con corrección de Holm",
        "llcccc",
        # «$p$ corregido» en dos renglones y las decisiones bajo un solo titulo: con los titulos en un
        # renglon la tabla no entra en la caja. Medida con las metricas de LMRoman12 (regular y negrita):
        # el contenido mas ancho de cada columna suma unos 385 pt, y con 5 pt de separacion, unos 445 pt,
        # contra 455 de la caja. Con la separacion de 6 pt por defecto mide unos 457.
        r"& & & " + bf("$p$") + r" & \multicolumn{2}{c}{" + bf("Decisión") + r"} \\"
        "\n" r"\cmidrule(lr){5-6}"
        "\n" + encabezar("Método", "Frente a", "Diferencia", "corregido", "Pares", "Escenas"),
        bloques,
        previo=[r"\setlength{\tabcolsep}{5pt}"],
        nota=" ".join([
            "Elaboración propia.",
            "Cada métrica tiene once contrastes: la propuesta frente al Top-Hat clásico y cada uno de "
            "esos dos operadores frente a los cinco métodos multiescala.",
            "Diferencia: media del método de la columna Método menos media del método de la "
            "columna Frente a, sobre los veinte pares, en las unidades de cada métrica (decibelios en "
            "PSNR).",
            "$p$ corregido: valor $p$ con la corrección de Holm sobre los once contrastes de la métrica.",
            "Decisión: si el contraste es significativo al 5~\\% después de la corrección, el método "
            "de la columna Método gana o pierde según el signo de la diferencia; si no lo es, empata.",
            "En las seis métricas, un valor mayor es mejor.",
            "Pares: decisión con los veinte pares del corpus como bloques, como en la "
            "Tabla~\\ref{tab:wilcoxon_resumen}.",
            "Escenas: decisión con las trece escenas como bloques. Las métricas de cada escena se "
            "promedian sobre sus tomas, y se aplican la misma corrección y la misma regla.",
            "El Top-Hat clásico se usó con radio 5 y peso 1.",
            PROPUESTA]))


# ---------------------------------------------- 5. deteccion de objetos (M3FD)
def v2_semillas():
    """Semillas por entrada del analisis: cada contraste guarda un renglon por par de semillas."""
    p = pd.read_csv(REP / "m3fd_v2_pares_semillas.csv")
    n = p.groupby(["punto", "contra"]).size().iloc[0]
    return int(round(n ** 0.5))


def v2_csv(base):
    """La version sin redondear de un CSV del analisis de deteccion, si existe (tasas_precisas_v2.py).

    analizar_v2.py guarda cuatro decimales, y un segundo redondeo a porcentaje falla en dos
    celdas (Laplace de ambas 97.0534 y DTCWT equilibrada 62.9495). Las versiones precisas reproducen los CSV
    oficiales redondeadas a cuatro decimales; el script lo comprueba antes de escribirlas.
    """
    precisa = {"m3fd_v2_tasas": "m3fd_v2_tasas_precisas.csv",
               "m3fd_v2_contrastes": "m3fd_v2_contrastes_precisos.csv"}[base]
    return REP / precisa if (REP / precisa).exists() else REP / f"{base}.csv"


def pp(v, nd=1):
    """Una proporcion en puntos porcentuales, con punto decimal.

    Se redondea en decimal y hacia arriba en el medio, no con el float: 0.9705 por 100 da 97.04999... en
    coma flotante y se imprimiria 97.0, cuando el valor sin redondear del analisis es 97.0534. Los CSV del
    analisis (analizar_v2.py) guardan cuatro decimales, asi que aca no se puede
    recuperar mas precision; esto solo evita el segundo error de redondeo.
    """
    from decimal import Decimal, ROUND_HALF_UP
    q = (Decimal(str(v)) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    return num(float(q), nd)


# El texto del libro escribe con palabras los numeros chicos; las notas de las tablas hacen lo mismo.
PALABRA = {1: "una", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete", 8: "ocho",
           9: "nueve", 10: "diez", 11: "once", 12: "doce"}


def palabra(n):
    return PALABRA.get(int(n), str(int(n)))


def v2_grupos_prueba():
    """Grupos de bloques contiguos de la prueba, tengan o no objetos de una sola camara."""
    p = pd.read_csv(REP / "m3fd_v2_prueba.csv")
    return int(p[p["entra"]]["grupo"].nunique())


def v2_tasas():
    d = pd.read_csv(v2_csv("m3fd_v2_tasas"))
    d = d[d["punto"] == "fppi"].sort_values("equilibrada", ascending=False)
    f0 = d.iloc[0]
    n = v2_semillas()
    # la mayor tasa equilibrada, comparada en la cifra impresa, para marcar los empates
    impresas = {i: pp(f["equilibrada"]) for i, f in d.iterrows()}
    maxima = pp(d["equilibrada"].max())
    filas = []
    for i, f in d.iterrows():
        k = f["entrada"]
        filas.append(f"{CORTO[k]} & {pp(f['solo_visible'])} & {pp(f['solo_infrarroja'])} & "
                     + negrita_si(impresas[i], impresas[i] == maxima)
                     + f" & {pp(f['de_ambas'])}")
    # la tabla muestra solo las entradas fusionadas: los detectores de la visible y de la infrarroja
    # definen los objetos de una sola camara, y su tasa sobre ellos no es comparable
    assert not set(d["entrada"]) & {"VIS", "IR"}, "la visible o la infrarroja entraron a la tabla"
    return envolver(
        "v2_tasas",
        "Tasa de acierto de las entradas fusionadas en la detección de objetos",
        "lcccc",
        encabezar("Entrada", "Solo visible", "Solo infrarroja", "Equilibrada", "De ambas"),
        filas,
        nota=f"Elaboración propia. Las tasas están en porcentaje y se calcularon con el umbral "
             f"principal. "
             f"El umbral principal de cada detector se fijó para que este cometiera, en los cuadros "
             f"de seguimiento, tantos falsos positivos de personas y luces por imagen como los "
             f"detectores de la visible con un umbral de 0.25. "
             f"Solo visible y Solo infrarroja se calculan sobre los objetos que ve una sola cámara: "
             f"{int(f0['n_solo_visible'])} vistos solo por la visible y "
             f"{int(f0['n_solo_infrarroja'])} solo por la infrarroja. "
             f"La columna De ambas se calcula sobre los {int(f0['n_ambas'])} objetos que ven las "
             f"dos cámaras. "
             f"La columna Equilibrada es el promedio de las dos columnas anteriores. Las filas van "
             f"de mayor a menor tasa equilibrada, y la mayor está en negrita. "
             f"Cada tasa promedia, sobre {palabra(n)} semillas, la fracción de objetos encontrados. "
             f"La visible y la infrarroja no figuran porque sus detectores definen qué objetos ve una "
             f"sola cámara. " + PROPUESTA)


# Los tres umbrales del analisis, con el nombre que les da el libro (Seccion 3.5.3): en la fila de la
# tabla y dentro de una frase de la nota.
UMBRALES = {"fppi": ("Umbral principal", "el umbral principal"),
            "0.25": ("Umbral fijo de 0.25", "el umbral fijo"),
            "f1": ("Umbral de mejor equilibrio por clase", "el de mejor equilibrio por clase")}


def deteccion_tophat():
    """Tasa equilibrada de la propuesta menos la del Top-Hat clasico, la comparacion de deteccion que
    examina la hipotesis. Una fila por umbral, con el intervalo del 95 % por grupos (error estandar
    robusto y t con grupos menos uno), y una ultima fila con el bootstrap salvaje por grupos y el umbral
    principal. La nota da el recorrido de las nueve diferencias entre pares de semillas, desde
    m3fd_v2_pares_semillas.csv: es lo que muestra que la ventaja depende de la semilla.
    """
    d = pd.read_csv(v2_csv("m3fd_v2_contrastes"), dtype={"punto": str})
    d = d[d["contra"] == "TopHat_Clasico"].set_index("punto")
    assert sorted(d.index) == sorted(UMBRALES), "no son los tres umbrales del analisis"
    s = pd.read_csv(REP / "m3fd_v2_pares_semillas.csv", dtype={"punto": str})
    s = s[s["contra"] == "TopHat_Clasico"]
    n = v2_semillas()
    assert d["grupos"].nunique() == 1, "los umbrales no usan los mismos grupos"
    grupos = int(d["grupos"].iloc[0])

    filas, positivos, recorridos, negativas = [], [], [], set()
    for punto, (fila, frase) in UMBRALES.items():
        f = d.loc[punto]
        # con punto decimal, los extremos del intervalo se separan con coma: [a, b]
        filas.append(f"{fila} & {pp(f['diferencia'])} & [{pp(f['ic_lo'])}, {pp(f['ic_hi'])}]")
        # un limite inferior positivo que con un decimal se imprime 0.0 se aclara en la nota
        if f["ic_lo"] > 0 and pp(f["ic_lo"]) == "0.0":
            positivos.append((num(100 * float(f["ic_lo"]), 2), frase))
        # las nueve diferencias entre pares de semillas de este umbral
        p = s[s["punto"] == punto]
        assert len(p) == n * n, f"faltan pares de semillas con {frase}"
        # el CSV de pares guarda cuatro decimales; el de contrastes, el valor completo
        assert abs(p["diferencia"].min() - f["pares_min"]) < 6e-5
        assert abs(p["diferencia"].max() - f["pares_max"]) < 6e-5
        recorridos.append((pp(p["diferencia"].min()), pp(p["diferencia"].max()), frase))
        neg = p[p["diferencia"] < 0]
        # la frase de la nota vale solo si las negativas son las de una misma semilla del Top-Hat
        # clasico frente a todas las de la propuesta, con el mismo numero en los tres umbrales
        assert neg["semilla_otro"].nunique() == 1 and len(neg) == n, "cambio el patron de las negativas"
        negativas.add(len(neg))
    assert len(negativas) == 1
    # la fila del bootstrap salvaje, con el umbral principal, separada de las del intervalo con t. Sale del
    # bootstrap estudentizado con la nula impuesta (bootstrap_estudentizado_v2.py), no de las columnas wild_*
    # de analizar_v2.py, que no estudentizan
    w = pd.read_csv(REP / "m3fd_v2_bootstrap_estudentizado.csv", dtype={"punto": str})
    w = w[w["contra"] == "TopHat_Clasico"].set_index("punto")
    assert abs(w.loc["fppi", "diferencia"] - d.loc["fppi", "diferencia"]) < 1e-12
    f = w.loc["fppi"]
    filas.append(rf"\addlinespace \textit{{Bootstrap}} salvaje por grupos & {pp(f['diferencia'])} & "
                 f"[{pp(f['wcr_lo'])}, {pp(f['wcr_hi'])}]")
    p_wcr = num(float(f["p_wcr"]), 2)

    # «puntos» va solo con la primera cifra de cada enumeracion, para no repetirlo
    positivos = [f"{v} puntos con {fr}" if i == 0 else f"{v} con {fr}"
                 for i, (v, fr) in enumerate(positivos)]
    aclaracion = []
    if len(positivos) == 1:
        aclaracion = [f"El límite inferior que se muestra como 0.0 es positivo: {positivos[0]}."]
    elif positivos:
        aclaracion = ["Los límites inferiores que se muestran como 0.0 son positivos: "
                      + ", ".join(positivos[:-1]) + f" y {positivos[-1]}."]
    (a0, b0, fr0), (a1, b1, fr1), (a2, b2, fr2) = recorridos
    return envolver(
        "deteccion_tophat",
        "Diferencia de tasa equilibrada entre la propuesta y el Top-Hat clásico",
        "lcc",
        encabezar("Cálculo", "Diferencia", r"Intervalo del 95~\%"),
        filas,
        nota=" ".join(
            ["Elaboración propia. La diferencia, en puntos porcentuales, es la tasa de acierto "
             "equilibrada de la propuesta menos la del Top-Hat clásico.",
             "El cálculo de los intervalos de confianza del 95~\\% se describe en la "
             "Sección~\\ref{sec:det-comparacion}.",
             f"La unidad del análisis es el grupo de bloques contiguos de cuadros: de los "
             f"{palabra(v2_grupos_prueba())} grupos de la prueba, entran los {palabra(grupos)} que "
             f"tienen objetos de una sola cámara.",
             f"Las tres primeras filas usan un error estándar robusto por grupos y la distribución $t$ "
             f"con {palabra(grupos - 1)} grados de libertad \\parencite{{cameron2015}}.",
             "La última fila usa el umbral principal y un \\textit{bootstrap} salvaje por grupos, "
             "estudentizado y con la hipótesis nula impuesta \\parencite{cameron2008, webb2023}.",
             "Su intervalo reúne las diferencias que esa prueba no rechaza al 5~\\%, y el valor $p$ "
             f"para una diferencia nula es {p_wcr}."]
            + aclaracion
            + [f"Según el par de semillas, la diferencia va de {a0} a {b0} puntos con {fr0}.",
               f"Con {fr1} va de {a1} a {b1}, y con {fr2}, de {a2} a {b2}.",
               f"Con cada umbral, {palabra(negativas.pop())} de las {palabra(n * n)} diferencias son "
               f"negativas: frente a una misma semilla del Top-Hat clásico, las {palabra(n)} semillas "
               f"de la propuesta quedan por debajo.",
               "Por eso la diferencia no es robusta a la semilla."]))


TABLAS = [
    ("tabla_medias_seis", medias_seis),
    ("tabla_ranking_seis", ranking_seis),
    ("tabla_friedman_seis", friedman_seis),
    ("tabla_wilcoxon_resumen", wilcoxon_resumen),
    ("tabla_wilcoxon_completa", wilcoxon_completa),
    ("tabla_v2_tasas", v2_tasas),
    ("tabla_deteccion_tophat", deteccion_tophat),
]


def main():
    SAL.mkdir(parents=True, exist_ok=True)
    for nombre, constructor in TABLAS:
        tabla(nombre, constructor())
    # Una tabla que el generador ya no produce no puede quedar en la carpeta: el capitulo podria seguir
    # trayendola con \input y mostrar cifras que ya no se mantienen.
    vigentes = {f"{n}.tex" for n, _ in TABLAS}
    for p in sorted(SAL.glob("tabla_*.tex")):
        if p.name not in vigentes:
            p.unlink()
            print(f"  - borrada, ya no se genera: {p.relative_to(RAIZ)}")
    print(f"\n  {len(TABLAS)} tablas escritas en {SAL.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
