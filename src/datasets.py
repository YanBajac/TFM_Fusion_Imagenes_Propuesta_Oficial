"""
datasets.py
-----------
Funciones para cargar y gestionar pares de imágenes visibles (VIS) e infrarrojas (IR).
"""

from pathlib import Path
import cv2
import numpy as np


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

# Pares excluidos del corpus por defectos verificados en los archivos de origen.
# Athena_heather_IR_hei_vis_g: el archivo del slot VIS es una copia byte a byte del
# IR del mismo nombre (md5 056b42a579c2ddbc28d325f5ca909bb0, que ademas coincide con
# IR/Athena_heather_hei_vis.bmp). No es un par VIS/IR: es la misma imagen dos veces,
# de modo que MSE(VIS,IR)=0 y todo metodo que devuelva la entrada sin modificarla
# obtiene SSIM=1 y un PSNR infinito, lo que invalida cualquier promedio de fidelidad.
# El corpus efectivo queda en 19 pares.
PARES_EXCLUIDOS = {"Athena_heather_IR_hei_vis_g"}


def load_image(path: str | Path, grayscale: bool = True) -> np.ndarray:
    """Carga una imagen desde disco."""
    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imread(str(path), flag)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen: {path}")
    return img.astype(np.float32) / 255.0


def load_pair(vis_path: str | Path, ir_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Carga un par VIS/IR y retorna ambas imágenes normalizadas."""
    vis = load_image(vis_path)
    ir = load_image(ir_path)
    return vis, ir


def list_pairs(vis_dir: str | Path = None, ir_dir: str | Path = None,
               incluir_excluidos: bool = False) -> list[tuple[Path, Path]]:
    """
    Retorna una lista de tuplas (vis_path, ir_path) buscando imágenes
    con el mismo nombre en los subdirectorios VIS e IR dentro de raw/.

    Los pares de PARES_EXCLUIDOS se omiten por defecto (ver el comentario de esa
    constante). Con incluir_excluidos=True se devuelve el corpus completo, lo que
    sirve para auditar o documentar el defecto, no para producir resultados.
    """
    vis_dir = Path(vis_dir) if vis_dir else RAW_DIR / "VIS"
    ir_dir = Path(ir_dir) if ir_dir else RAW_DIR / "IR"

    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    vis_files = {f.stem: f for f in vis_dir.iterdir() if f.suffix.lower() in extensions}
    ir_files = {f.stem: f for f in ir_dir.iterdir() if f.suffix.lower() in extensions}

    common = sorted(vis_files.keys() & ir_files.keys())
    if not incluir_excluidos:
        common = [k for k in common if k not in PARES_EXCLUIDOS]
    return [(vis_files[k], ir_files[k]) for k in common]


try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    from torchvision import transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

if TORCH_AVAILABLE:
    class TNOFusionDataset(Dataset):
        """
        Dataset de PyTorch para cargar pares de imágenes (VIS e IR) simultáneamente.
        Aplica conversión a escala de grises y convierte a tensores al vuelo.
        """
        def __init__(self, vis_dir: str | Path = None, ir_dir: str | Path = None, transform=None):
            self.pairs = list_pairs(vis_dir, ir_dir)
            if transform is None:
                # Transformación por defecto: escala de grises y conversión a Tensor [0, 1]
                self.transform = transforms.Compose([
                    transforms.Grayscale(num_output_channels=1),
                    transforms.ToTensor()
                ])
            else:
                self.transform = transform

        def __len__(self):
            return len(self.pairs)

        def __getitem__(self, idx):
            vis_path, ir_path = self.pairs[idx]
            
            # Cargar con PIL para que torchvision.transforms funcione nativamente
            vis_img = Image.open(vis_path).convert('RGB')
            ir_img = Image.open(ir_path).convert('RGB')
            
            if self.transform:
                vis_tensor = self.transform(vis_img)
                ir_tensor = self.transform(ir_img)
            
            return vis_tensor, ir_tensor

    def get_dataloader(vis_dir=None, ir_dir=None, batch_size=4, shuffle=True, num_workers=0):
        """
        Crea un DataLoader de PyTorch para el dataset de fusión.
        """
        dataset = TNOFusionDataset(vis_dir, ir_dir)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
        return dataloader

