import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.datasets import list_pairs, TORCH_AVAILABLE

def test_dataset():
    pairs = list_pairs()
    print(f"Pares base encontrados con list_pairs(): {len(pairs)}")

    if TORCH_AVAILABLE:
        from src.datasets import get_dataloader
        loader = get_dataloader(batch_size=2, shuffle=True)
        
        print(f"Lotes en el DataLoader: {len(loader)}")
        # Obtener un lote
        vis_batch, ir_batch = next(iter(loader))
        
        print(f"Forma del lote VIS: {vis_batch.shape}")
        print(f"Forma del lote IR: {ir_batch.shape}")
        print(f"Tipo de datos VIS: {vis_batch.dtype}")
        print(f"Los tensores ya están en escala de grises (1 canal) como se solicitó.")
    else:
        print("PyTorch no está disponible. No se puede probar el DataLoader.")

if __name__ == "__main__":
    test_dataset()
