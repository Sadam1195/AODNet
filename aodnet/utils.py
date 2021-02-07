import os
import wandb
import gdown
import subprocess
import tensorflow as tf
from matplotlib import pyplot as plt


def download_dataset():
    gdown.download(
        'https://drive.google.com/uc?id=1sInD9Ydq8-x7WwqehE0EyRknMdSFPOat',
        'LOLdataset.zip', quiet=False
    )
    print('Unpacking Dataset')
    subprocess.run(['unzip', 'Dehaze-NYU.zip'])
    print('Done!!!')


def init_wandb(project_name, experiment_name, wandb_api_key):
    if project_name is not None and experiment_name is not None:
        os.environ['WANDB_API_KEY'] = wandb_api_key
        wandb.init(project=project_name, name=experiment_name, sync_tensorboard=True)


def peak_signal_noise_ratio(y_true, y_pred):
    return tf.image.psnr(y_pred, y_true, max_val=255.0)


def plot_result(image1, image2, title1, title2):
    fig = plt.figure(figsize=(12, 12))
    fig.add_subplot(1, 2, 1).set_title(title1)
    _ = plt.imshow(image1)
    fig.add_subplot(1, 2, 2).set_title(title2)
    _ = plt.imshow(image2)
    plt.show()
