from pathlib import Path

import numpy as np
from PIL import Image


IMAGE_SIZE = (64, 64)


def preprocess_radiografia(image_path: str | Path, output_path: str | Path | None = None) -> np.ndarray:
    image = Image.open(image_path).convert("L").resize(IMAGE_SIZE)
    if output_path is not None:
        image.save(output_path)

    array = np.asarray(image, dtype=np.float32) / 255.0
    return array.flatten().reshape(1, -1)
