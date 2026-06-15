import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK="#1a1a1a"; GRAY="#444"; RULE="#bdbdbd"; ACC="#2f5b7c"
plt.rcParams["font.family"]="DejaVu Sans"

def render_table(col_labels, rows, path, w=9.6, h=2.6, highlight_row=None, colw=None):
    fig,ax=plt.subplots(figsize=(w,h)); ax.axis("off")
    tbl=ax.table(cellText=rows, colLabels=col_labels, cellLoc="center", loc="center",
                 colWidths=colw)
    tbl.auto_set_font_size(False); tbl.set_fontsize(12); tbl.scale(1,1.6)
    for (r,c),cell in tbl.get_cells().items() if hasattr(tbl,'get_cells') else tbl.get_celld().items():
        cell.set_edgecolor("none")
        cell.set_facecolor("white")
        if r==0:
            cell.get_text().set_color(INK); cell.get_text().set_fontweight("bold")
            cell.visible_edges="B"; cell.set_edgecolor(INK); cell.set_linewidth(1.2)
        else:
            cell.get_text().set_color(GRAY)
            cell.visible_edges="B"; cell.set_edgecolor(RULE); cell.set_linewidth(0.5)
            if c==0: cell.get_text().set_color(INK)
            if highlight_row is not None and r==highlight_row:
                cell.get_text().set_color(ACC); cell.get_text().set_fontweight("bold")
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.05, transparent=True)
    plt.close(fig); print("ok",path)

# Tabla promedios (7 métodos × 6 métricas clásicas)
cols=["Método","EN","SD","FE","MG","MI_vis","MI_ir"]
rows=[
 ["Promedio","6.518","0.109","1.029","0.014","1.512","1.064"],
 ["Curvelet","6.664","0.117","1.053","0.026","1.304","0.884"],
 ["Pirámide Laplace","6.835","0.155","1.079","0.025","2.118","1.072"],
 ["Top-Hat disco L3","6.676","0.120","1.055","0.023","1.395","0.918"],
 ["Top-Hat cuadrado L3","6.690","0.121","1.057","0.023","1.391","0.914"],
 ["Top-Hat cruz L3","6.663","0.119","1.052","0.023","1.383","0.938"],
 ["Top-Hat disco L5","6.722","0.125","1.062","0.024","1.363","0.914"],
]
render_table(cols,rows,"docs/figures/_pres/tabla_promedios.png",w=10,h=2.8,highlight_row=3,
             colw=[0.26,0.12,0.12,0.12,0.12,0.13,0.13])

# Tabla Friedman (6 métricas)
cols2=["Métrica","χ² Friedman","p-valor","Sig. (α=0,05)"]
rows2=[["EN","158.00","8.4e-29","Sí"],["SD","179.41","3.1e-33","Sí"],
       ["FE","158.00","8.4e-29","Sí"],["MG","192.66","5.5e-36","Sí"],
       ["MI_vis","159.67","3.8e-29","Sí"],["MI_ir","147.37","1.3e-26","Sí"]]
render_table(cols2,rows2,"docs/figures/_pres/tabla_friedman.png",w=6.2,h=2.6,
             colw=[0.28,0.28,0.26,0.22])
