# -*- coding: utf-8 -*-
"""Deriva del codigo el inventario CSV -> script que lo produce, para que el reporte lo publique.

POR QUE. El informe tiene tres menciones de archivos .py y cuatro de .csv en 96 paginas, asi que no se
puede ir de un numero al archivo que lo produjo. Para un reporte tecnico eso es el nucleo de la
reproducibilidad: cada tabla tiene que rastrearse hasta el script que la calculo. Y un inventario escrito
a mano se desactualiza en el primer script nuevo, y este trabajo ya tiene cuarenta y pico.

COMO SE DETECTA EL PRODUCTOR, y por que hicieron falta tres intentos.

  1. Buscar el nombre del CSV cerca de un to_csv() dio 60 «sin productor» de 67, incluidos archivos
     recien escritos. Falla porque los nombres se ARMAN —f"complementariedad_objetos{suf}.csv"— y porque
     el to_csv suele estar en otra funcion, a doscientas lineas del nombre.
  2. Buscar por raiz del nombre y creditar a todo script que contenga algun to_csv acredito como
     productor a make_avances_report.py de CSV que solo LEE: el generador escribe dos rankings propios, y
     eso alcanzaba para atribuirle cualquier archivo que mencione.
  3. Lo que si funciona es seguir la VARIABLE. Los scripts de este repositorio hacen
     `SALIDA = MR / "x.csv"` y despues `d.to_csv(SALIDA)`, o `to_csv(os.path.join(MR, "x.csv"))`
     directo. Se buscan las dos formas: el literal dentro de una llamada de escritura, y la variable a la
     que se le asigno el nombre usada en una llamada de escritura.

Los CSV sin productor son un hallazgo en si mismo: el dato existe y nadie sabe rehacerlo.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/inventario_artefactos.py
"""
import csv as _csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MR = ROOT / 'experiments' / 'results' / 'metrics_reports'
SALIDA = MR / 'inventario_artefactos.csv'
GENERADORES = {'make_avances_report.py', 'make_avances_excel.py', 'make_reporte_optimos.py',
               'make_figura_semillas.py'}
# lo que cuenta como escribir un CSV en este repositorio
ESCRITURA = re.compile(r'\.to_csv\s*\(|save_metrics_csv\s*\(|DictWriter\s*\(|_csv\.writer\s*\(|'
                       r'csv\.writer\s*\(')


def scripts():
    return sorted(p for p in (ROOT / 'experiments').rglob('*.py') if '__pycache__' not in str(p))


def vars_de_salida(texto):
    """varname -> conjunto de nombres de .csv que se le asignan, incluyendo los armados con f-string.

    Para los armados se guarda la RAIZ: de f"complementariedad_objetos{suf}.csv" queda
    «complementariedad_objetos», que despues se compara como prefijo.
    """
    out = {}
    for m in re.finditer(r'^\s*(\w+)\s*=\s*([^\n]*\.csv[\'"][^\n]*)$', texto, re.M):
        var, resto = m.group(1), m.group(2)
        for lit in re.findall(r'[\'"]([^\'"]*\.csv)[\'"]', resto):
            out.setdefault(var, set()).add(lit)
    # f-strings con sufijo variable: f"raiz{algo}.csv"
    for m in re.finditer(r'^\s*(\w+)\s*=\s*[^\n]*f[\'"][^\'"]*?([\w]+)\{[^}]*\}\.csv[\'"]',
                         texto, re.M):
        out.setdefault(m.group(1), set()).add(m.group(2) + '*')
    # y las que se devuelven desde una funcion de rutas, del tipo  SALIDA / f"raiz{suf}.csv"
    for m in re.finditer(r'f[\'"][^\'"]*?([\w]+)\{[^}]*\}\.csv[\'"]', texto):
        out.setdefault('__armadas__', set()).add(m.group(1) + '*')
    return out


def escribe(texto, var):
    """Si `var` aparece como destino de una llamada de escritura."""
    if var == '__armadas__':
        return bool(ESCRITURA.search(texto))
    for m in ESCRITURA.finditer(texto):
        # la variable puede ir dentro de los parentesis de la llamada, o en la linea anterior si el
        # to_csv se parte en dos lineas
        # la ventana va en LAS DOS DIRECCIONES: en estos scripts la asignacion de la ruta esta ANTES
        # de la llamada —«with SALIDA.open(...) as fh» y en la linea siguiente «csv.writer(fh)»—, asi que
        # mirar solo hacia adelante daba «sin productor» para archivos que si se escriben.
        seg = texto[max(0, m.start() - 220):m.start() + 220]
        if re.search(rf'\b{re.escape(var)}\b', seg):
            return True
    return False


def coincide(nombre, patrones):
    st = nombre[:-4]
    for p in patrones:
        if p.endswith('*'):
            if st.startswith(p[:-1]):
                return True
        elif p == nombre or p[:-4] == st:
            return True
    return False


def main():
    csvs = sorted(p.name for p in MR.glob('*.csv'))
    if not csvs:
        print('  no hay CSV en metrics_reports')
        return 1
    fuentes = {p: p.read_text(encoding='utf-8', errors='replace') for p in scripts()}
    vars_por_script = {p: vars_de_salida(t) for p, t in fuentes.items()}

    filas = []
    for nombre in csvs:
        prod, cons = [], []
        for p, t in fuentes.items():
            if p.name == 'inventario_artefactos.py':
                continue        # este script nombra CSV ajenos al informar: no produce ninguno
            # productor: el literal dentro de una llamada de escritura, o una variable con ese nombre
            # que se use como destino de escritura
            # el literal tiene que estar en la MISMA llamada, no en la vecindad: si no, un read_csv
            # que cae cerca de un to_csv ajeno acredita al script como productor. Se acota a los
            # parentesis de la llamada, que es lo que sigue al punto de escritura.
            directo = any(nombre in t[m.end():m.end() + 120]
                          for m in ESCRITURA.finditer(t))
            porvar = any(coincide(nombre, pats) and escribe(t, var)
                         for var, pats in vars_por_script[p].items())
            if directo or porvar:
                prod.append(p.name)
            if 'read_csv' in t and nombre[:-4].split('_m3fd')[0] in t:
                cons.append(p.name)
        prod, cons = sorted(set(prod)), sorted(set(cons))
        docs = sorted(set(cons) & GENERADORES)
        filas.append({'csv': nombre,
                      'produce': ' + '.join(prod) if prod else 'SIN PRODUCTOR',
                      'productores': len(prod),
                      'llega_a_documento': 'si' if docs else 'no',
                      'generadores': ' + '.join(docs) if docs else '—'})

    with SALIDA.open('w', encoding='utf-8', newline='') as fh:
        w = _csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    sinp = [f['csv'] for f in filas if f['productores'] == 0]
    varios = [f for f in filas if f['productores'] > 1]
    endoc = [f for f in filas if f['llega_a_documento'] == 'si']
    print(f'  {len(filas)} CSV · con productor {len(filas) - len(sinp)} · '
          f'con mas de uno {len(varios)} · llegan a un documento {len(endoc)}')
    print(f'  -> {SALIDA.relative_to(ROOT)}')
    if sinp:
        print(f'\n  SIN PRODUCTOR ({len(sinp)}):')
        for c in sinp:
            print(f'     {c}')
    if varios:
        print(f'\n  CON MAS DE UN PRODUCTOR ({len(varios)}) — hay que mirarlos:')
        for f in varios:
            print(f'     {f["csv"]:44} <- {f["produce"]}')
    print(f'\n  control, cuatro que conozco:')
    for c in ('entorno.csv', 'all_metrics.csv', 'grilla_complementariedad.csv',
              'ablacion_banco_resumen.csv'):
        f = next((x for x in filas if x['csv'] == c), None)
        print(f'     {c:44} <- {f["produce"] if f else "(no esta)"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
