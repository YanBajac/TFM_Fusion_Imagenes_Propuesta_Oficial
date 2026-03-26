import os
import shutil
from pathlib import Path

def reorganize_dataset():
    # Paths
    base_dir = Path(__file__).resolve().parents[2]
    source_dir = base_dir / "src" / "ds" / "TNO_Image_Fusion_Dataset"
    vis_dir = base_dir / "data" / "raw" / "VIS"
    ir_dir = base_dir / "data" / "raw" / "IR"

    # Create destination directories
    vis_dir.mkdir(parents=True, exist_ok=True)
    ir_dir.mkdir(parents=True, exist_ok=True)

    copied_count = 0

    # Walk through the original dataset
    for root, dirs, files in os.walk(source_dir):
        root_path = Path(root)
        
        # We look for pairs like VIS_*.bmp and IR_*.bmp
        vis_files = [f for f in files if f.startswith("VIS_") or "VIS" in f.upper()]
        ir_files = [f for f in files if f.startswith("IR_") or "IR" in f.upper()]
        
        # In TNO, they often share a base name after the prefix.
        # Let's clean and match them.
        for vis_f in vis_files:
            # find corresponding IR file
            # e.g., VIS_meting003_r.bmp -> IR_meting003_g.bmp
            # or VIS_1.bmp -> IR_1.bmp
            
            # extract a core identifier by removing known prefixes/suffixes
            core_id = vis_f.replace("VIS_", "").replace("_r.bmp", "").replace(".bmp", "").replace(".png", "")
            
            # Find matching IR using the core_id
            matching_ir = None
            for ir_f in ir_files:
                if core_id in ir_f:
                    matching_ir = ir_f
                    break
            
            if matching_ir:
                camera = root_path.parent.name.replace("_images", "")
                scene = root_path.name
                
                new_name = f"{camera}_{scene}_{core_id}.bmp"
                
                src_vis = root_path / vis_f
                src_ir = root_path / matching_ir
                
                dst_vis = vis_dir / new_name
                dst_ir = ir_dir / new_name
                
                shutil.copy2(src_vis, dst_vis)
                shutil.copy2(src_ir, dst_ir)
                copied_count += 1
                
    print(f"Dataset reorganizado exitosamente. Se copiaron {copied_count} pares de imágenes.")

if __name__ == "__main__":
    reorganize_dataset()
