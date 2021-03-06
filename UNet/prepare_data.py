import numpy as np
import os
from PIL import Image
import imgaug.augmenters as iaa


def data_gen(
    train_data: str, seg_data: str, batch_size: int, n_classes: int
) -> (np.ndarray, np.ndarray):
    inputs = np.array(os.listdir(train_data))
    batch = len(inputs) // batch_size
    identity = np.identity(n_classes, dtype=np.int16)

    while True:
        shuffle = np.random.permutation(len(inputs))
        for b in np.array_split(inputs[shuffle], batch):
            imgs = []
            segs = []
            for img_file in b:
                img = Image.open(os.path.join(train_data, img_file)).convert("RGB")
                img = img.resize((224, 224))
                img = np.asarray(img)

                seq = iaa.Sequential(
                    [
                        iaa.GaussianBlur(sigma=(0, 3.0)),
                        iaa.LogContrast(gain=(0.5, 1.0)),
                        iaa.ChannelShuffle(p=1.0),
                    ]
                )
                img = seq.augment_image(img)
                img = img / 255.0
                imgs.append(img)

                seg = Image.open(
                    os.path.join(seg_data, img_file.split(".")[0] + "-seg.png")
                )
                seg = seg.resize((224, 224))
                seg = np.asarray(seg)
                seg = identity[seg].astype(np.float32)
                segs.append(seg)

            yield np.array(imgs), np.array(segs)
