import cv2
from imageio import imread
from skimage import img_as_ubyte

from CV.scan import cut_by_external_contour, cut_by_internal_contour, \
    rgb_to_gray, gray_to_binary, cut_board_on_cells, crop_letter
from ML.letter_recognition import classify_images, nums_to_letters
from preprocessing.model import CLASSIFIER_DUMP_PATH, SCALER_DUMP_PATH


if __name__ == '__main__':
    image = imread('ML/images_to_cut/IMG_20200615_183955_6.jpg')
    image = img_as_ubyte(image)
    img_external_crop = cut_by_external_contour(image)
    img_internal_crop = cut_by_internal_contour(img_external_crop)
    img_bw = gray_to_binary(rgb_to_gray(img_internal_crop, [1, 0, 0]))
    board_squares = img_as_ubyte(cut_board_on_cells(img_bw))

    for j in range(15):
        for i in range(15):
            board_squares[j][i] = crop_letter(board_squares[j][i])

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

    cv2.imshow('', cv2.resize(cv2.cvtColor(img_internal_crop,
                                           cv2.COLOR_RGB2BGR), (700, 700)))
    cv2.waitKey()
    cv2.destroyAllWindows()
