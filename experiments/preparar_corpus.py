# -*- coding: utf-8 -*-
"""Arma data/raw a partir del TNO descargado, leyendo el manifiesto.

POR QUE EXISTE. Las imagenes del TNO no se versionan: pesan y tienen su propia licencia. Lo unico que
viaja en el repositorio es data/raw/MANIFIESTO_CORPUS.csv, con el nombre, el tamano, el md5 y la ruta de
origen exacta de cada uno de los 42 archivos. Con eso el corpus es reconstruible, pero a mano seria
crear dos carpetas y copiar 42 archivos de a uno, renombrando cada uno segun la columna del
manifiesto: cuarenta y dos oportunidades de equivocarse, en el primer paso que da quien clona el
repositorio. Este script hace esa copia y despues comprueba el md5 de lo que copio.

COMO ENCUENTRA CADA ARCHIVO, en tres intentos y en este orden:
  1. la ruta exacta que declara el manifiesto, debajo de la carpeta que se le pasa;
  2. cualquier archivo cuya ruta TERMINE en esa ruta relativa, por si la descarga quedo con una carpeta
     de mas arriba (que es lo habitual: el zip del TNO se descomprime distinto segun la herramienta);
  3. el md5. Se indexa el arbol del TNO por tamano y se calcula el md5 solo de los candidatos que
     coinciden en bytes con algo del manifiesto. Es el intento definitivo: encuentra el archivo aunque
     lo hayan movido o renombrado, porque no depende de ninguna ruta.

DOS ARCHIVOS NO SE COPIAN: SE CONVIERTEN. El par que sustituyo al par corrupto —Triclobs_Kaptein_1123,
VIS e IR— no esta en data/raw byte a byte como en el TNO: se volvio a guardar en escala de grises de 8
bits con cv2.imwrite, porque el original no venia en ese formato. Su md5 del manifiesto es el del
archivo CONVERTIDO, no el del original, y por eso su columna origen_tno trae entre parentesis el md5 del
archivo de origen. Para esas dos filas el script busca por el md5 DE ORIGEN, rehace la conversion y
recien entonces compara contra el md5 del manifiesto. Copiarlas sin convertir da un archivo distinto y
el verificador lo rechaza, que es lo que corresponde.

Si en la carpeta que se indica el archivo ya esta en su forma convertida —porque se lo consiguio de
otra parte— tambien lo encuentra: se busca primero por el md5 de origen y despues por el del
manifiesto, y en ese segundo caso se copia sin convertir nada.

LO QUE NO HACE. No descarga nada: el TNO se baja a mano de figshare, una vez, y tiene su licencia.
Tampoco decide nada sobre el corpus: el par excluido se copia igual que los demas y es list_pairs() la
que lo retira, para que el defecto quede a la vista y sea auditable.

Uso:
    python experiments/preparar_corpus.py --tno "D:/datasets/TNO_Image_Fusion_Dataset"
    python experiments/preparar_corpus.py --tno "..." --simular     # dice que haria y no toca nada

Al terminar corre la comprobacion completa:  python experiments/verificar_corpus.py
"""
import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import cv2
import pandas as pd

MANIF = RAIZ / 'data' / 'raw' / 'MANIFIESTO_CORPUS.csv'
CRUDO = RAIZ / 'data' / 'raw'

# «ruta/al/archivo.bmp (md5 origen abc123...; nota)» -> la ruta y el md5 del archivo de origen
_NOTA = re.compile(r'^(?P<ruta>[^(]+?)\s*\(\s*md5\s+origen\s+(?P<md5>[0-9a-f]{32})', re.I)


def md5(p, bloque=1 << 20):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for trozo in iter(lambda: f.read(bloque), b''):
            h.update(trozo)
    return h.hexdigest()


def parse_origen(valor):
    """Devuelve (ruta, md5_origen). md5_origen es None cuando el archivo se copia sin convertir."""
    m = _NOTA.match(str(valor).strip())
    if m:
        return m.group('ruta').strip(), m.group('md5').lower()
    return str(valor).strip(), None


def indice_por_md5(tno, md5s):
    """md5 -> ruta, sobre el arbol del TNO. Solo se hashea lo que puede ser uno de los declarados.

    Se filtra por tamano cuando se lo conoce, pero los archivos que hay que CONVERTIR no declaran el
    tamano del original —el del manifiesto es el del convertido—, asi que para ellos hay que hashear
    todo candidato. Se resuelve al reves: se hashea todo y se guarda solo lo que interesa. Sigue siendo
    un recorrido y el TNO son unos cientos de archivos.
    """
    idx = {}
    for p in tno.rglob('*'):
        if not p.is_file():
            continue
        try:
            h = md5(p)
        except OSError:
            continue
        if h in md5s:
            idx.setdefault(h, p)
    return idx


def buscar(tno, ruta, md5s, idx):
    """Ubica el archivo de origen. md5s son los aceptables, en orden de preferencia."""
    cola = ruta.replace('\\', '/').lstrip('/')
    directo = tno / cola
    if directo.is_file() and md5(directo) in md5s:
        return directo, 'ruta declarada'
    nombre = Path(cola).name
    for p in tno.rglob(nombre):
        if p.is_file() and p.as_posix().endswith(cola) and md5(p) in md5s:
            return p, 'ruta relativa'
    for h in md5s:
        if h in idx:
            return idx[h], 'md5'
    return None, None


def convertir(fuente, destino):
    """Rehace la conversion a escala de grises de 8 bits, la misma que produjo el archivo declarado."""
    img = cv2.imread(str(fuente), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise OSError(f'cv2 no pudo leer {fuente}')
    if not cv2.imwrite(str(destino), img):
        raise OSError(f'cv2 no pudo escribir {destino}')


def main():
    ap = argparse.ArgumentParser(description='Arma data/raw desde el TNO segun el manifiesto.')
    ap.add_argument('--tno', required=True,
                    help='carpeta donde se descomprimio el TNO Image Fusion Dataset')
    ap.add_argument('--simular', action='store_true',
                    help='informa lo que haria y no escribe nada')
    args = ap.parse_args()

    tno = Path(args.tno).expanduser()
    if not tno.is_dir():
        print(f'FALLA no existe la carpeta del TNO: {tno}')
        return 1
    if not MANIF.is_file():
        print(f'FALLA falta el manifiesto: {MANIF}')
        return 1

    man = pd.read_csv(MANIF)
    print(f'manifiesto: {len(man)} archivos declarados en {man["par"].nunique()} pares')
    print(f'origen:     {tno}')
    print(f'destino:    {CRUDO}' + ('   (SIMULACION: no se escribe nada)' if args.simular else ''))

    if not args.simular:
        for mod in ('VIS', 'IR'):
            (CRUDO / mod).mkdir(parents=True, exist_ok=True)

    # cada fila aporta los md5 que sirven para encontrar su origen: el del original cuando hay que
    # convertir, y el del manifiesto siempre (el archivo puede estar ya convertido)
    filas = []
    todos_md5 = set()
    for _, f in man.iterrows():
        ruta, md5_origen = parse_origen(f['origen_tno'])
        acept = ([md5_origen] if md5_origen else []) + [str(f['md5']).lower()]
        filas.append((f, ruta, md5_origen, acept))
        todos_md5.update(acept)

    idx = None
    copiados, convertidos, ya_estaban, faltan, dudosos = [], [], [], [], []

    for f, ruta, md5_origen, acept in filas:
        destino = CRUDO / f['modalidad'] / f['archivo']
        esperado = str(f['md5']).lower()
        if destino.is_file() and md5(destino) == esperado:
            ya_estaban.append(f['archivo'])
            continue
        if idx is None:
            print(f'\nindexando el TNO por md5 (una sola vez, {len(todos_md5)} objetivos)...')
            idx = indice_por_md5(tno, todos_md5)
            print(f'  {len(idx)} de los {len(todos_md5)} md5 buscados aparecen en el arbol')
        fuente, como = buscar(tno, ruta, acept, idx)
        if fuente is None:
            faltan.append(f'{f["modalidad"]}/{f["archivo"]}  (origen: {ruta})')
            continue

        hay_que_convertir = md5_origen is not None and md5(fuente) == md5_origen
        etiqueta = f'{f["modalidad"]}/{f["archivo"]}  <- {como}'
        if args.simular:
            (convertidos if hay_que_convertir else copiados).append(etiqueta)
            continue

        destino.parent.mkdir(parents=True, exist_ok=True)
        try:
            if hay_que_convertir:
                convertir(fuente, destino)
            else:
                shutil.copy2(fuente, destino)
        except OSError as e:
            faltan.append(f'{f["modalidad"]}/{f["archivo"]}  ({e})')
            continue

        obtenido = md5(destino)
        if obtenido == esperado:
            (convertidos if hay_que_convertir else copiados).append(etiqueta)
        elif hay_que_convertir:
            # el original era el correcto (se lo encontro por su md5) y la conversion se rehizo, pero
            # los bytes del BMP no salieron identicos: eso depende del codificador de OpenCV, no de la
            # imagen. Se comprueba que los PIXELES sean los que corresponden y se avisa con precision,
            # porque verificar_corpus.py compara md5 y va a marcar estas dos filas.
            a = cv2.imread(str(destino), cv2.IMREAD_GRAYSCALE)
            b = cv2.imread(str(fuente), cv2.IMREAD_GRAYSCALE)
            iguales = a is not None and b is not None and a.shape == b.shape and (a == b).all()
            dudosos.append(f'{f["modalidad"]}/{f["archivo"]}: el origen es el correcto y la conversion '
                           f'se rehizo, pero el md5 quedo en {obtenido[:12]}... y el manifiesto declara '
                           f'{esperado[:12]}...; pixeles ' + ('IDENTICOS' if iguales else 'DISTINTOS'))
        else:
            faltan.append(f'{f["modalidad"]}/{f["archivo"]}  (se copio y el md5 no coincide)')

    print('\n--- resultado ---')
    print(f'  {len(ya_estaban):>3} ya estaban, con el md5 correcto')
    print(f'  {len(copiados):>3} {"se copiarian" if args.simular else "copiados"}')
    for c in copiados[:5]:
        print(f'        {c}')
    if len(copiados) > 5:
        print(f'        ... y {len(copiados) - 5} mas')
    print(f'  {len(convertidos):>3} {"se convertirian" if args.simular else "convertidos"} '
          f'(escala de grises de 8 bits)')
    for c in convertidos:
        print(f'        {c}')
    if dudosos:
        print(f'  {len(dudosos):>3} con el md5 distinto del declarado:')
        for d in dudosos:
            print(f'        {d}')
    print(f'  {len(faltan):>3} sin resolver')
    for f in faltan:
        print(f'        {f}')

    if faltan:
        print('\nNo se pudo armar el corpus completo. Los archivos sin resolver no estan en la carpeta')
        print('que se indico, ni por su ruta ni por su md5. Revisar que el TNO este descomprimido')
        print('entero y que la ruta de --tno apunte a la carpeta que contiene sus subcarpetas.')
        return 1
    if dudosos:
        print('\nEl corpus quedo armado pero dos archivos no coinciden byte a byte con el manifiesto.')
        print('Si sus pixeles son IDENTICOS, las metricas dan lo mismo —se calculan sobre los pixeles—')
        print('pero verificar_corpus.py los va a marcar, porque compara md5 a proposito.')
        return 1

    print('\nCorpus armado. Ahora la comprobacion completa (md5, pares, canales):')
    print('    python experiments/verificar_corpus.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
