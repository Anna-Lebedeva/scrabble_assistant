import errno
import cv2
import os

path_to_raw = "../raw_set"
path_to_result = "../dataset_image/"

list_of_raw = os.listdir(path_to_raw)
count_of_raw = len(list_of_raw)

for folder in range(count_of_raw):

    try:
        os.mkdir(path_to_result + str(list_of_raw[folder]))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    path_to_raw_folder = path_to_raw + str(list_of_raw[folder]) + "/"

    list_of_raw_folder = os.listdir(path_to_raw_folder)

    count_of_raw_folder = len(list_of_raw_folder)

    for i in range(count_of_raw_folder):

        image = cv2.imread(path_to_raw_folder + list_of_raw_folder[i])
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        cv2.imwrite(path_to_result + str(list_of_raw[folder]) + "/" + list_of_raw_folder[i], gray)

        print(str(round(i*100/count_of_raw_folder, 1)) + "%")
