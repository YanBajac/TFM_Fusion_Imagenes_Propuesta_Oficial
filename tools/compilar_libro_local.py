"""Compila el libro con pdfLaTeX y Biber en una carpeta aparte.

Copia docs/libro_v4 a build/libro/ y compila ahí (pdflatex, biber y dos pasadas más), para que los
archivos auxiliares no queden junto a las fuentes. Al final informa los errores, las referencias sin
definir y los renglones desbordados del log, y deja el PDF en build/libro/main.pdf.

Necesita MiKTeX con pdflatex y biber. No descarga nada.

Uso, desde la raíz del repositorio:
    .venv\\Scripts\\python.exe -X utf8 tools/compilar_libro_local.py
    .venv\\Scripts\\python.exe -X utf8 tools/compilar_libro_local.py --abrir     (abre el PDF al terminar)
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIBRO = RAIZ / "docs" / "libro_v4"
DESTINO = RAIZ / "build" / "libro"
MIKTEX = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64"


def entorno():
    """Si el PATH trae una entrada que es un archivo y no una carpeta, biber no arranca. Se sacan esas
    entradas solo para esta compilación."""
    env = dict(os.environ)
    partes = [p for p in env.get("PATH", "").split(os.pathsep) if p and not Path(p).is_file()]
    if MIKTEX.is_dir():
        partes.insert(0, str(MIKTEX))
    env["PATH"] = os.pathsep.join(partes)
    return env


def correr(cmd, env):
    r = subprocess.run(cmd, cwd=DESTINO, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def main():
    if not (LIBRO / "main.tex").exists():
        print(f"No se encuentra {LIBRO / 'main.tex'}")
        return 1
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    shutil.copytree(LIBRO, DESTINO, ignore=shutil.ignore_patterns("*.md"))
    env = entorno()
    pasos = [
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["biber", "main"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
    ]
    for cmd in pasos:
        print("  >", " ".join(cmd))
        codigo, salida = correr(cmd, env)
        if codigo != 0:
            print(salida[-3000:])
            print(f"\n  Falló «{' '.join(cmd)}». El log completo está en {DESTINO / 'main.log'}")
            return 1

    log = (DESTINO / "main.log").read_text(encoding="utf-8", errors="replace")
    errores = re.findall(r"^! .*", log, flags=re.M)
    sin_definir = sorted(set(re.findall(r"(?:Reference|Citation) `([^']+)' .*undefined", log)))
    desbordes = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*lines (\d+--\d+)", log)
    grandes = [(float(a), l) for a, l in desbordes if float(a) > 1.0]
    m = re.search(r"Output written on main\.pdf \((\d+) pages", log)

    print()
    print(f"  Páginas: {m.group(1) if m else '?'}")
    print(f"  Errores: {len(errores)}")
    for e in errores[:10]:
        print("    ", e)
    print(f"  Referencias o citas sin definir: {len(sin_definir)} {sin_definir[:10]}")
    print(f"  Renglones que se salen del margen más de 1 pt: {len(grandes)}")
    for a, l in grandes[:10]:
        print(f"     {a:.1f} pt, líneas {l}")
    pdf = DESTINO / "main.pdf"
    print(f"\n  PDF: {pdf}")
    if "--abrir" in sys.argv and pdf.exists():
        os.startfile(pdf)
    return 0 if not errores and not sin_definir else 1


if __name__ == "__main__":
    sys.exit(main())
