import cv2
import numpy as np
import torchvision
import albumentations
from torch import Tensor
from typing import Tuple
import matplotlib.pyplot as plt

import torchlm


def callable_array_noop(
        img: np.ndarray,
        landmarks: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    # Do some transform here ...
    return img.astype(np.uint32), landmarks.astype(np.float32)


def callable_tensor_noop(
        img: Tensor,
        landmarks: Tensor
) -> Tuple[Tensor, Tensor]:
    # Do some transform here ...
    return img, landmarks


def test_torchlm_transforms_pipeline():
    print(f"torchlm version: {torchlm.__version__}")
    seed = np.random.randint(0, 1000)
    np.random.seed(seed)

    img_path = "./2.jpg"
    anno_path = "./2.txt"
    save_path = f"./logs/2_wflw_{seed}.jpg"
    img = cv2.imread(img_path)[:, :, ::-1].copy()  # RGB
    with open(anno_path, 'r') as fr:
        lm_info = fr.readlines()[0].strip('\n').split(' ')

    landmarks = [float(x) for x in lm_info[:196]]
    landmarks = np.array(landmarks).reshape(98, 2)  # (5,2) or (98, 2) for WFLW

    # some global setting will show you useful details
    torchlm.set_transforms_debug(True)
    torchlm.set_transforms_logging(True)
    torchlm.set_autodtype_logging(True)

    transform = torchlm.LandmarksCompose([
        # use native torchlm transforms
        torchlm.LandmarksRandomScale(prob=0.5),
        torchlm.LandmarksRandomTranslate(prob=0.5),
        torchlm.LandmarksRandomShear(prob=0.5),
        torchlm.LandmarksRandomMask(prob=0.5),
        torchlm.LandmarksRandomBlur(kernel_range=(5, 25), prob=0.5),
        torchlm.LandmarksRandomBrightness(prob=0.),
        torchlm.LandmarksRandomRotate(40, prob=0.5, bins=8),
        torchlm.LandmarksRandomCenterCrop((0.5, 1.0), (0.5, 1.0), prob=0.5),
        # bind torchvision image only transforms with a given bind prob
        torchlm.bind(torchvision.transforms.GaussianBlur(kernel_size=(5, 25)), prob=0.5),
        torchlm.bind(torchvision.transforms.RandomAutocontrast(p=0.5)),
        torchlm.bind(torchvision.transforms.RandomAdjustSharpness(sharpness_factor=3, p=0.5)),
        # bind albumentations image only transforms
        torchlm.bind(albumentations.ColorJitter(p=0.5)),
        torchlm.bind(albumentations.GlassBlur(p=0.5)),
        torchlm.bind(albumentations.RandomShadow(p=0.5)),
        # bind albumentations dual transforms
        torchlm.bind(albumentations.RandomCrop(height=200, width=200, p=0.5)),
        torchlm.bind(albumentations.RandomScale(p=0.5)),
        torchlm.bind(albumentations.Rotate(p=0.5)),
        # bind custom callable array functions with a given bind prob
        torchlm.bind(callable_array_noop, bind_type=torchlm.BindEnum.Callable_Array, prob=0.5),
        # bind custom callable Tensor functions
        torchlm.bind(callable_tensor_noop, bind_type=torchlm.BindEnum.Callable_Tensor, prob=0.5),
        torchlm.LandmarksResize((256, 256)),
        torchlm.LandmarksNormalize(),
        torchlm.LandmarksToTensor(),
        torchlm.LandmarksToNumpy(),
        torchlm.LandmarksUnNormalize()
    ])

    trans_img, trans_landmarks = transform(img, landmarks)
    new_img = torchlm.draw_landmarks(trans_img, trans_landmarks, circle=2)
    plt.imshow(new_img)
    plt.show()
    cv2.imwrite(save_path, new_img[:, :, ::-1])

    # unset the global status when you are in training process
    torchlm.set_transforms_debug(False)
    torchlm.set_transforms_logging(False)
    torchlm.set_autodtype_logging(False)


def test_torchlm_transform_mask():
    print(f"torchlm version: {torchlm.__version__}")
    seed = np.random.randint(0, 1000)
    np.random.seed(seed)

    with_alpha = True
    img_path = "./2.jpg"
    anno_path = "./2.txt"
    save_path = f"./logs/2_wflw_mask_alpha_{with_alpha}_{seed}.jpg"
    img = cv2.imread(img_path)[:, :, ::-1].copy()  # RGB
    with open(anno_path, 'r') as fr:
        lm_info = fr.readlines()[0].strip('\n').split(' ')

    landmarks = [float(x) for x in lm_info[:196]]
    landmarks = np.array(landmarks).reshape(98, 2)  # (5,2) or (98, 2) for WFLW

    # some global setting will show you useful details
    torchlm.set_transforms_debug(True)
    torchlm.set_transforms_logging(True)
    torchlm.set_autodtype_logging(True)

    if not with_alpha:
        transform = torchlm.LandmarksCompose([
            torchlm.LandmarksRandomMask(prob=1.),
            torchlm.LandmarksResize((256, 256))
        ])
    else:
        transform = torchlm.LandmarksCompose([
            torchlm.LandmarksRandomMaskWithAlpha(prob=1.),
            torchlm.LandmarksResize((256, 256))
        ])

    trans_img, trans_landmarks = transform(img, landmarks)
    new_img = torchlm.draw_landmarks(trans_img, trans_landmarks, circle=2)
    plt.imshow(new_img)
    plt.show()
    cv2.imwrite(save_path, new_img[:, :, ::-1])

    # unset the global status when you are in training process
    torchlm.set_transforms_debug(False)
    torchlm.set_transforms_logging(False)
    torchlm.set_autodtype_logging(False)


def test_torchlm_transform_patches_mixup():
    print(f"torchlm version: {torchlm.__version__}")
    seed = np.random.randint(0, 1000)
    np.random.seed(seed)

    with_alpha = True
    img_path = "./2.jpg"
    anno_path = "./2.txt"
    save_path = f"./logs/2_wflw_patches_mixup_alpha_{with_alpha}_{seed}.jpg"
    img = cv2.imread(img_path)[:, :, ::-1].copy()  # RGB
    with open(anno_path, 'r') as fr:
        lm_info = fr.readlines()[0].strip('\n').split(' ')

    landmarks = [float(x) for x in lm_info[:196]]
    landmarks = np.array(landmarks).reshape(98, 2)  # (5,2) or (98, 2) for WFLW

    # some global setting will show you useful details
    torchlm.set_transforms_debug(True)
    torchlm.set_transforms_logging(True)
    torchlm.set_autodtype_logging(True)

    if not with_alpha:
        transform = torchlm.LandmarksCompose([
            torchlm.LandmarksRandomPatchesMixUp(prob=1.),
            torchlm.LandmarksResize((256, 256))
        ])
    else:
        transform = torchlm.LandmarksCompose([
            torchlm.LandmarksRandomPatchesMixUpWithAlpha(alpha=0.5, prob=1.),
            torchlm.LandmarksResize((256, 256))
        ])

    trans_img, trans_landmarks = transform(img, landmarks)
    new_img = torchlm.draw_landmarks(trans_img, trans_landmarks, circle=2)
    plt.imshow(new_img)
    plt.show()
    cv2.imwrite(save_path, new_img[:, :, ::-1])

    # unset the global status when you are in training process
    torchlm.set_transforms_debug(False)
    torchlm.set_transforms_logging(False)
    torchlm.set_autodtype_logging(False)


def test_torchlm_transform_backgrounds_mixup():
    print(f"torchlm version: {torchlm.__version__}")
    seed = np.random.randint(0, 1000)
    np.random.seed(seed)

    with_alpha = True

    img_path = "./2.jpg"
    anno_path = "./2.txt"
    save_path = f"./logs/2_wflw_backgrounds_mixup_alpha_{with_alpha}_{seed}.jpg"
    img = cv2.imread(img_path)[:, :, ::-1].copy()  # RGB
    with open(anno_path, 'r') as fr:
        lm_info = fr.readlines()[0].strip('\n').split(' ')

    landmarks = [float(x) for x in lm_info[:196]]
    landmarks = np.array(landmarks).reshape(98, 2)  # (5,2) or (98, 2) for WFLW

    # some global setting will show you useful details
    torchlm.set_transforms_debug(True)
    torchlm.set_transforms_logging(True)
    torchlm.set_autodtype_logging(True)

    if not with_alpha:
        transform = torchlm.LandmarksCompose([
            torchlm.LandmarksRandomBackgroundMixUp(prob=1.),
            torchlm.LandmarksResize((256, 256))
        ])
    else:
        transform = torchlm.LandmarksCompose([
            torchlm.LandmarksRandomBackgroundMixUpWithAlpha(alpha=0.5, prob=1.),
            torchlm.LandmarksResize((256, 256))
        ])

    trans_img, trans_landmarks = transform(img, landmarks)
    new_img = torchlm.draw_landmarks(trans_img, trans_landmarks, circle=2)
    plt.imshow(new_img)
    plt.show()
    cv2.imwrite(save_path, new_img[:, :, ::-1])

    # unset the global status when you are in training process
    torchlm.set_transforms_debug(False)
    torchlm.set_transforms_logging(False)
    torchlm.set_autodtype_logging(False)


def test_torchlm_transform_center_crop():
    pass


def test_torchlm_transform_horizontal():
    pass


def test_torchlm_transform_rotate():
    pass


def test_torchlm_transform_shear():
    pass


def test_torchlm_transform_blur():
    pass

def test_torchlm_transform_align():
    pass

if __name__ == "__main__":
    # test_torchlm_transforms_pipeline()
    # test_torchlm_transform_mask()
    # test_torchlm_transform_patches_mixup()
    test_torchlm_transform_backgrounds_mixup()
