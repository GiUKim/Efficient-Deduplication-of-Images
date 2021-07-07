import cv2
import os
import numpy as np
import time
from PIL import Image
from config import config

# import imagehash
# import math
# import matplotlib.pyplot as plt


def get_Hamming_Distance(org_image, tgt_image):
    difference = (int(org_image, 16)) ^ (int(tgt_image, 16))
    return bin(difference).count("1")


def binary_Search(lst, find_number):
    low = 0
    high = len(lst) - 1
    while low <= high:
        middle = low + (high - low) // 2
        if lst[middle] == find_number:
            return True
        elif lst[middle] < find_number:
            low = middle + 1
        else:
            high = middle - 1
    return False


def get_DHash_Value(hash_list):
    # 반복횟수 22734 * 8 * 8 + 22734 * 64
    for filename in os.listdir(config.DIRECTORY):
        if filename.endswith(".jpg"):
            # img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_GRAYSCALE)
            # img = cv2.GaussianBlur(img, (7, 7), 0)
            # img = cv2.resize(img, dsize=(config.resize_width, config.resize_height), interpolation=cv2.INTER_LINEAR)
            #
            # t, t_otsu = cv2.threshold(img, -1, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            # # print("threshold suggestion: {}".format(t))
            # # t_otsu = t_otsu / 255
            # # 32*32 otsu thresholding 된 이미지 보기
            # # cv2.imshow("otsu", t_otsu)
            # # cv2.waitKey(0)
            # pixels = t_otsu.flatten().tolist()
            # difference = []
            # # 각 픽셀 차이 계산
            # for row in range(config.resize_height):
            #     row_start_index = row * config.resize_width
            #     for col in range(config.resize_width - 1):
            #         left_pixel_index = row_start_index + col
            #         # # 이미지 4개의 가장자리(두께: 2)의 hash에 weight (x0)
            #         # if (row <= 1) or (row >= 30) or (col <= 1) or (col >= 30):
            #         #     continue
            #         # # 이미지 중앙(8x8) 부분의 hash에 weight (x2)
            #         # if (row >= 12 and row <= 19) and (col >= 12 and col <= 19):
            #         #     difference.append(pixels[left_pixel_index] > pixels[left_pixel_index + 1])
            #         difference.append(pixels[left_pixel_index] > pixels[left_pixel_index + 1])

            img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_GRAYSCALE)
            #img = cv2.bilateralFilter(img, 9, 75, 75)
            #img = cv2.GaussianBlur(img, (config.GAUSSIAN_KERNEL, config.GAUSSIAN_KERNEL), 0)
            img = cv2.resize(img, dsize=(config.resize_width, config.resize_height), interpolation=cv2.INTER_LINEAR)
            # cv2.imshow("img", img)
            # cv2.waitKey(0)
            # img = Image.open(os.path.join(config.DIRECTORY, filename))
            # img = img.resize((config.resize_width, config.resize_height))  # 9 * 8로 이미지 리사이징
            # img = img.convert("L")  # gray s\cale로 차원 축소
            img = img / 255.0
            # cv2.imshow("img", img)
            # cv2.waitKey(0)
            pixels = img.flatten().tolist()
            #pixels = list(img.getdata())
            difference = []
            # 각 픽셀 차이 계산
            for row in range(config.resize_height):
                row_start_index = row * config.resize_width
                for col in range(config.resize_width - 1):
                    left_pixel_index = row_start_index + col
                    #이미지 4개의 가장자리(두께: 2)에 대해 hash 연산에 참여시키지 않음
                    if (row <= config.IGNORE_EDGE - 1) or (row >= 32 - config.IGNORE_EDGE) or (col <= config.IGNORE_EDGE - 1) or (col >= 32 - config.IGNORE_EDGE):
                        continue
                    # 이미지 중앙(8x8) 부분의 hash에 weight (x4)
                    if (row >= 12 and row <= 19) and (col >= 12 and col <= 19):
                        for w in range(config.CENTER_HASH_WEIGHT - 1):
                            difference.append(pixels[left_pixel_index] > pixels[left_pixel_index + 1])
                    difference.append(pixels[left_pixel_index] > pixels[left_pixel_index + 1])

            decimal_value = 0
            hash_string = ""
            # 16진수 dHash 생성
            for index, value in enumerate(difference):
                if value:
                    #decimal_value += value * (2 ** (index % 8))
                    decimal_value += (value << (index % 8))  # shift left 연산이 훨씬 빠름 (1초)
                if index % 8 == 7:
                    # rjust로 16진수가 두자리가 아닌 한자리가 나오면 MSB쪽을 0으로 채움
                    hash_string += str(hex(decimal_value)[2:].rjust(2, "0"))
                    decimal_value = 0
            hash_list.append(hash_string)


def get_Filtered_Images():
    img_num = 0
    remain_image_list = []
    count_search = 0
    count_cache = 0
    # 최종 건져낼 이미지들을 새로운 리스트에 삽입
    file_list = [filenames for (filenames) in os.listdir(config.DIRECTORY)]
    file_list_jpg = [file for file in file_list if file.endswith(".jpg")]
    for filename in file_list_jpg:
        # 캐시에 마스킹 되어있지만 중복 집단 중 1개씩의 이미지를 삽입
        if binary_Search(remain_list, img_num):
            count_search += 1
            remain_image_list.append(filename)
        # 캐시에 마스킹 되어 있지 않은 순수한 이미지 삽입
        elif not cache[img_num]:
            count_cache += 1
            remain_image_list.append(filename)
        img_num += 1

    return remain_image_list, count_search, count_cache


def save_Result_At_Directory(remain_image_list, cache, remain_list):
    # 필터링 된 이미지 저장 할 디렉토리 생성
    if not os.path.isdir(config.SAVE_DIRECTORY):
        os.mkdir(config.SAVE_DIRECTORY)

    # 제외 된 이미지 저장 할 디렉토리 생성
    if not os.path.isdir(config.EXCEPT_DIRECTORY):
        os.mkdir(config.EXCEPT_DIRECTORY)

    # 필터링 되고 남은 이미지 저장
    for filename in remain_image_list:
        org_img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_COLOR)
        cv2.imwrite(os.path.join(config.SAVE_DIRECTORY, filename), org_img)

    # 중복으로 판단되어 제외 된 이미지도 따로 저장
    image_num = 0
    for filename in os.listdir(config.DIRECTORY):
        if filename.endswith(".jpg"):
            if (cache[image_num]) and (not binary_Search(remain_list, image_num)):
                img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_COLOR)
                cv2.imwrite(os.path.join(config.EXCEPT_DIRECTORY, filename), img)
            image_num += 1

def check_image_size() :
    count = 0
    file_list = [filenames for (filenames) in os.listdir(config.DIRECTORY)]
    file_list_jpg = [file for file in file_list if file.endswith(".jpg")]
    for filename in file_list_jpg:
            img_path = os.path.join(config.DIRECTORY, filename)
            size = os.path.getsize(img_path)
            if size <= 0 :
                os.remove(img_path)
                continue
            count += 1
    return count

if __name__ == '__main__':
    config = config()
    print("BEFORE config.NUM_IMAGES : " , config.NUM_IMAGES)
    config.NUM_IMAGES = check_image_size()
    print("AFTER config.NUM_IMAGES : " , config.NUM_IMAGES)

    cache = np.zeros(config.NUM_IMAGES, dtype=bool)  # 이미지 개수만큼 bool type의 캐시 메모리 생성
    hash_list = []
    start = time.time()  # 타이머 시작
    #cv2.ocl.setUseOpenCL(True)  # 속도 올려준다고 하는데 잘 모르겠음
    # 모든 이미지에 대하여 dhash 값 구하기
    get_DHash_Value(hash_list)

    count_loop = 0
    remain_list = []
    # 전체 이미지 순회하며 비교 (time-dominant loop)
    #print(get_Hamming_Distance(hash_list[0], hash_list[1]))
    for org_idx in range(config.NUM_IMAGES - 1):
        if cache[org_idx]:
            continue
        else:
            for tgt_idx in range(org_idx, org_idx + config.MAX_ITERATE):
                if tgt_idx > config.NUM_IMAGES - 1:
                    break
                if org_idx == tgt_idx: #or cache[tgt_idx]:
                    continue

                count_loop += 1
                similarity = get_Hamming_Distance(hash_list[org_idx], hash_list[tgt_idx])
                if similarity < config.THRESHOLD:
                    # if cache[org_idx] and not cache[tgt_idx]:
                    #     cache[tgt_idx] = True
                    # else:
                    cache[org_idx] = True   # 비교한 이미지의 인덱스에 해당하는 캐시 메모리에 마스킹
                    remain_list.append(org_idx)    # 비교한 이미지는 살려야 하므로 따로 리스트에 저장
                    cache[tgt_idx] = True   # 비교된 이미지의 인덱스에 해당하는 캐시 메모리에 마스킹
                #print(similarity)

    remain_image_list = []
    count_search = 0
    count_cache = 0
    remain_image_list, count_search, count_cache = get_Filtered_Images()

    elapsed_time = time.time() - start
    efficiency = config.get_Efficiency(total_iter=count_loop)
    limited_efficiency = config.get_Limited_Compare_Efficiency(total_iter=count_loop)

    # spec summary
    print("주 소요구간 반복 횟수: {}".format(count_loop))
    print("소요 시간: {} sec".format(round(elapsed_time, 4)))
    print("중복 그룹 개수, 미중복 이미지 개수: {} {}".format(count_search, count_cache))
    print("필터링 후 남은 이미지 개수: {}".format(len(remain_image_list)))
    print("(비교 데이터 수 제한)시간 효율: {}%".format(round(limited_efficiency, 4)))
    print("(총)시간 효율: {}%".format(round(efficiency, 4)))

    save_Result_At_Directory(remain_image_list, cache, remain_list)

