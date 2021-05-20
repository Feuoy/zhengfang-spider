import tesserocr
from PIL import Image


def adjust_randcodeImage(original_path, adjusted_path):
    img = Image.open(original_path)
    if img.mode == "P":
        img = img.convert('RGB')
    (x, y) = img.size
    x_s = int(76)
    y_s = int(y * x_s / x)
    img_ = img.resize((x_s, y_s), Image.ANTIALIAS)
    img_.save(adjusted_path)


def get_randcodeImage(img_path):
    img = Image.open(img_path)
    return img


def image_grayscale_deal(img):
    img = img.convert('L')
    return img


def image_thresholding_method(img):
    threshold = 160
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    img = img.point(table, '1')
    return img


def captcha_tesserocr_crack(img):
    randcode = tesserocr.image_to_text(img, "eng")
    return randcode


def identify_randcode(original_path, adjusted_path):
    adjust_randcodeImage(original_path, adjusted_path)
    img = get_randcodeImage(adjusted_path)
    img1 = image_grayscale_deal(img)
    img2 = image_thresholding_method(img1)
    randcode = captcha_tesserocr_crack(img2)
    print(randcode, end='')
    return randcode
