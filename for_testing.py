from cv2.cv2 import imread
from skimage import img_as_ubyte

from CV.scan import cut_by_external_contour, cut_by_internal_contour, \
    rgb_to_gray, gray_to_binary, cut_board_on_cells
from ML.letter_recognition import classify_images, nums_to_letters
from preprocessing.model import CLASSIFIER_DUMP_PATH, SCALER_DUMP_PATH

image = imread('ML/images_to_cut/test/IMG_20200619_094156_0.jpg')
if image is None:
    raise Exception("Изображение не найдено")
image = img_as_ubyte(image)
img_external_crop = cut_by_external_contour(image)
img_internal_crop = cut_by_internal_contour(img_external_crop)
img_bw = gray_to_binary(rgb_to_gray(img_internal_crop, [1, 0, 0]))
board_squares = img_as_ubyte(cut_board_on_cells(img_bw))

print('тест распознавания изображений:')
clf_path = CLASSIFIER_DUMP_PATH
sc_path = SCALER_DUMP_PATH
predicted_letters, pred_probas = classify_images(board_squares,
                                                 clf_path,
                                                 sc_path=None,
                                                 probability=True)
pred_board = nums_to_letters(predicted_letters, pred_probas)
for row in pred_board:
    print(row)
