import cv2
import os
import numpy as np
import time
from config import config

#from PIL import Image
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
            img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_GRAYSCALE)
            img = cv2.GaussianBlur(img, (7, 7), 0)
            img = cv2.resize(img, dsize=(config.resize_width, config.resize_height), interpolation=cv2.INTER_LINEAR)

            t, t_otsu = cv2.threshold(img, -1, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            #print("threshold suggestion: {}".format(t))
            #t_otsu = t_otsu / 255
            # 32*32 otsu thresholding 된 이미지 보기
            # cv2.imshow("otsu", t_otsu)
            # cv2.waitKey(0)
            pixels = t_otsu.flatten().tolist()
            difference = []
            # 각 픽셀 차이 계산
            for row in range(config.resize_height):
                row_start_index = row * config.resize_width
                for col in range(config.resize_width - 1):
                    left_pixel_index = row_start_index + col
                    # 이미지 4개의 가장자리(두께: 2)의 hash에 weight (x0)
                    if (row <= 1) or (row >= 30) or (col <= 1) or (col >= 30):
                        continue
                    # 이미지 중앙(8x8) 부분의 hash에 weight (x2)
                    if (row >= 12 and row <= 19) and (col >= 12 and col <= 19):
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
            #print(len(hash_string))
            hash_list.append(hash_string)


def save_Result_At_Directory(filtered_list):
    # 필터링 된 이미지 저장 할 디렉토리 생성
    if not os.path.isdir(config.NEW_DIRECTORY):
        os.mkdir(config.NEW_DIRECTORY)

    # 제외 된 이미지 저장 할 디렉토리 생성
    if not os.path.isdir(config.EXCEPT_DIRECTORY):
        os.mkdir(config.EXCEPT_DIRECTORY)

    image_num = 0
    filter_num = 0
    except_count = 0
    # 필터링 된 이미지들 NEW_DIRECTORY에 저장
    for filename in os.listdir(config.DIRECTORY):
        if filename.endswith(".jpg"):
            if filter_num >= len(filtered_list):
                break
            if filtered_list[filter_num] == image_num:
                filter_num += 1
                img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_COLOR)
                cv2.imwrite(os.path.join(config.NEW_DIRECTORY, filename), img)
            else:
                img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_COLOR)
                cv2.imwrite(os.path.join(config.EXCEPT_DIRECTORY, filename), img)
                except_count += 1
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
    # 이미지 개수만큼 int type의 캐시 메모리 생성
    # filtering process 횟수에 따라 cache에 해당하는 값이 증가하게끔 해야하므로 int타입으로 선언
    cache = np.zeros(config.NUM_IMAGES, dtype=int)
    hash_list = []
    start = time.time()  # 타이머 시작
    #cv2.ocl.setUseOpenCL(True)  # 속도 올려준다고 하는데 잘 모르겠음
    # 모든 이미지에 대하여 dhash 값 구하기
    get_DHash_Value(hash_list)

    count_loop = 0
    remain_list = []

    # 전체 이미지 순회하며 비교 (time-dominant loop)
    # 이미지 2개 비슷함 비교 테스트
    #print(get_Hamming_Distance(hash_list[0], hash_list[1]))
    filtered_list = []
    for processing in range(config.PROCESSING):  # 총 3번의 프로세싱 반복
        for org_idx in range(config.NUM_IMAGES - 1):
            if cache[org_idx] != processing:
                continue
            else:
                for tgt_idx in range(org_idx - config.MAX_ITERATE, org_idx + config.MAX_ITERATE):
                    # index 범위 초과 시 예외 처리
                    if tgt_idx > config.NUM_IMAGES - 1:
                        break
                    if tgt_idx < 0:
                        continue

                    # 다른 이미지에 의해 중복으로 판단되어 cache값이 업데이트 된 경우, pass
                    if org_idx == tgt_idx or cache[tgt_idx] != processing:
                        continue

                    count_loop += 1
                    # 해밍 거리 계산
                    similarity = get_Hamming_Distance(hash_list[org_idx], hash_list[tgt_idx])
                    #print(similarity)

                    # 비교 대상이 자신과 중복으로 판단할 경우
                    if similarity < (config.THRESHOLD - config.TH_REDUCE * processing):
                        # 비교하려는 대상이 이미 누군가에게 중복으로 판단되었을 때 본인의 캐시값 업데이트 후 pass
                        if cache[tgt_idx] > processing:
                            cache[org_idx] += 1
                            continue

                        cache[org_idx] += 1   # 비교한 이미지의 인덱스에 해당하는 캐시 메모리에 마스킹
                        # 마지막 loop의 경우 중복 그룹의 대표 이미지 1개씩 따로 리스트에 저장해둠
                        if processing == config.PROCESSING - 1:
                            remain_list.append(org_idx)    # 비교한 이미지는 살려야 하므로 따로 리스트에 저장
                        cache[tgt_idx] += 1   # 비교된 이미지의 인덱스에 해당하는 캐시 메모리에 마스킹
                    #print(similarity)
        # 최종리스트에 이번 loop에서 아무에게도 중복 판단이 되지 않은 이미지들을 삽입함
        for idx, val in enumerate(cache):
            if val == processing:
                filtered_list.append(idx)
        # 마지막 loop일 경우 저장해둔 중복그룹의 대표 이미지들도 최종 리스트에 삽입
        if processing == config.PROCESSING - 1:
            filtered_list.extend(remain_list)
            filtered_list = list(set(filtered_list))
            filtered_list.sort()

        print("필터링된 이미지 수 : {}, PROCESSING : {}".format(len(filtered_list), processing))

    elapsed_time = time.time() - start # 타이머 종료

    # 각 효율성 계산
    efficiency = config.get_Efficiency(total_iter=count_loop)
    limited_efficiency = config.get_Limited_Compare_Efficiency(total_iter=count_loop)

    # spec summary
    print("주 소요구간 반복 횟수: {}".format(count_loop))
    print("소요 시간: {} sec".format(round(elapsed_time, 4)))
    print("(비교 데이터 수 제한)시간 효율: {}%".format(round(limited_efficiency, 4)))
    print("(총)시간 효율: {}%".format(round(efficiency, 4)))

    # 이미지 저장
    save_Result_At_Directory(filtered_list)
