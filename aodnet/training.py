import os
import tensorflow as tf
from typing import Tuple
from .models import AODNet
from datetime import datetime
from wandb.keras import WandbCallback
from .dataloader import DeHazeDataLoader
from .utils import peak_signal_noise_ratio, plot_result


class Trainer:

    def __init__(self):
        self.train_dataset = None
        self.val_dataset = None
        self.model = None

    def __len__(self):
        return len(self.train_dataset)

    def build_datasets(self, dataset_path: str, image_crop_size: int, batch_size: int, val_split: float):
        dataloader = DeHazeDataLoader(dataset_path=dataset_path)
        self.train_dataset, self.val_dataset = dataloader.build_dataset(
            image_crop_size=image_crop_size, batch_size=batch_size, val_split=val_split
        )
        print(self.train_dataset)
        print(self.val_dataset)
        x, y = next(iter(self.train_dataset))
        for _ in range(x.shape[0]):
            plot_result(x.numpy()[_], y.numpy()[_], 'Hazy', 'Original')

    def build_model(
            self, build_shape: Tuple[int, int, int, int], stddev: float = 0.02,
            weight_decay: float = 1e-4, learning_rate: float = 1e-4):
        self.model = AODNet(stddev=stddev, weight_decay=weight_decay)
        self.model.build(build_shape)
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss=tf.keras.losses.MeanSquaredError(), metrics=[peak_signal_noise_ratio]
        )
        self.model.summary()

    def train(self, checkpoint_dir: str = './checkpoints/', epochs: int = 10):
        log_dir = "./logs/fit/" + datetime.now().strftime("%Y%m%d-%H%M%S")
        callbacks = [
            tf.keras.callbacks.ModelCheckpoint(
                os.path.join(checkpoint_dir, 'low_light_weights_best.h5'),
                monitor='val_loss', save_weights_only=True,
                mode="max", save_best_only=True, save_freq=1
            ),
            tf.keras.callbacks.TensorBoard(
                log_dir=log_dir, histogram_freq=1,
                update_freq=50, write_images=True
            ),
            WandbCallback()
        ]
        return self.model.fit(
            self.train_dataset, epochs=epochs,
            validation_data=self.val_dataset, callbacks=callbacks
        )
