import cv2
import os
from tqdm import tqdm
from config import Config
config = Config()

# 아무것도 사용하지 않았을 때 예상 순환 횟수에 대해 효율성 계산
def get_Efficiency(total_iter):
    # 기존 시간복잡도는 O(n^2)
    original_iter = Config.NUM_IMAGES * Config.NUM_IMAGES
    return ((original_iter - total_iter) / original_iter) * 100.0
# 캐시메모리를 사용하여 중복연산을 제거했을 때 효율성 계산
def get_Limited_Compare_Efficiency(total_iter):
    # 기존 시간복잡도는 O(n^k) k는 비교할 주변 이미지의 최대 개수
    original_iter = Config.NUM_IMAGES * Config.MAX_ITERATE
    return ((original_iter - total_iter) / original_iter) * 100.0

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

# 모든 이미지의 Feature point(descriptor)를 구함
def get_Feature_Point(cache):
    print("\n\n[GET FEATURE POINT Working ... ]")
    feature_list = []
    discard_recommend_list = []
    feature = cv2.AKAZE_create() # AKAZE 알고리즘으로 적용
    image_count = 0
    for filename in tqdm(os.listdir(config.DIRECTORY)):
        if filename.endswith(".jpg"):
            img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_GRAYSCALE)
            #img = cv2.GaussianBlur(img, (5, 5), 0)
            img = cv2.resize(img, (256, 256))
            kp, desc = feature.detectAndCompute(img, None)
            # 아무 Feature 가 없는 이미지일 경우
            if desc is None:
                discard_recommend_list.append(image_count)  # 이미지 제거 제안을 위해 리스트에 삽입
                cache[image_count] = True  # 연산 제외를 위해 cache masking
            feature_list.append(desc)
            image_count += 1
    return feature_list, cache, discard_recommend_list

def find_Feature_Matching(feature_list, cache, remain_list, cluster):
    print("\n\n[FIND MATCHING Working ... ]")
    count_loop = 0  # 반복 횟수 계산용
    config.NUM_IMAGES = check_image_size()
    for org_idx in tqdm(range(config.NUM_IMAGES - 1)):
        sub_cluster = []
        sub_cluster.append(org_idx)

        # 비교 주체 이미지가 중복 판정이 되어있으면 skip
        if cache[org_idx]:
            sub_cluster.pop()
            continue
        # 비교 주체 이미지로부터 이후 연속 MAX_ITERATE 개의 이미지를 비교 대상 이미지로 선정
        for tgt_idx in range(org_idx, org_idx + config.MAX_ITERATE):
            matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING)
            if tgt_idx > config.NUM_IMAGES - 1:
                break
            if org_idx == tgt_idx or cache[tgt_idx]:
                continue
            count_loop += 1
            matches = matcher.knnMatch(feature_list[org_idx], feature_list[tgt_idx], 2)
            similarity = 0
            is_match = False
            for m in matches:
                if len(m) < 2:
                    continue
                if m[0].distance / m[1].distance < config.THRESHOLD_RATE:
                    similarity += 1
                    if similarity >= config.THRESHOLD_SIM:
                        is_match = True
                        break
            if is_match:
                sub_cluster.append(tgt_idx)
                cache[tgt_idx] = True
                remain_list.append(org_idx)
                cache[org_idx] = True
        cluster.append(sub_cluster)
    print('')
    return count_loop, remain_list, cluster

def save_Result_At_Directory(cache, remain_list, discard_recommend_list, cluster):

    # 중복 제거 된 이미지 저장 할 디렉토리 생성(이미 존재하면 모든 파일 제거)
    if os.path.isdir(config.NEW_DIRECTORY):
        for file in os.scandir(config.NEW_DIRECTORY):
            os.remove(file.path)
    elif not os.path.isdir(config.NEW_DIRECTORY):
        os.mkdir(config.NEW_DIRECTORY)

    # 제외 된 이미지 저장 할 디렉토리 생성(이미 존재하면 모든 파일 제거)
    if os.path.isdir(config.EXCEPT_DIRECTORY):
        for file in os.scandir(config.EXCEPT_DIRECTORY):
            os.remove(file.path)
    elif not os.path.isdir(config.EXCEPT_DIRECTORY):
        os.mkdir(config.EXCEPT_DIRECTORY)

    # 삭제를 추천하는 이미지 저장 할 디렉토리 생성(이미 존재하면 모든 파일 제거)
    # Feature가 1개도 발견되지 못한 이미지들
    # 심한 Blur, Noise 등등
    if os.path.isdir(config.DISCARD_DIRECTORY):
        for file in os.scandir(config.DISCARD_DIRECTORY):
            os.remove(file.path)
    elif not os.path.isdir(config.DISCARD_DIRECTORY):
        os.mkdir(config.DISCARD_DIRECTORY)

    # 클러스터링된 이미지들을 구별하여 저장 할 디렉토리 생성(이미 존재하면 모든 파일 제거)
    if os.path.isdir(config.CLUSTER_DIRECTORY):
        for file in os.scandir(config.CLUSTER_DIRECTORY):
            os.remove(file.path)
    elif not os.path.isdir(config.CLUSTER_DIRECTORY):
        os.mkdir(config.CLUSTER_DIRECTORY)

    image_num = 0
    print("\n\n[SAVE TO DIRECTORY Working ... ]")
    for filename in tqdm(os.listdir(config.DIRECTORY)):
        if filename.endswith(".jpg"):
            img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_COLOR)
            # 살아남은 이미지들 NEW_DIRECTORY 에 저장
            if (not cache[image_num] or binary_Search(remain_list, image_num)) \
                    and not binary_Search(discard_recommend_list, image_num):
                cv2.imwrite(os.path.join(config.NEW_DIRECTORY, filename), img)
            # 살아남은 이미지들 NEW_DIRECTORY 에 저장
            elif binary_Search(discard_recommend_list, image_num):
                cv2.imwrite(os.path.join(config.DISCARD_DIRECTORY, filename), img)
            else:
                cv2.imwrite(os.path.join(config.EXCEPT_DIRECTORY, filename), img)
            image_num += 1
    print('')
    print("\n\n[CREATE CLUSTER OF IMAGE Working ... ]")
    cluster_num = 0
    for sub_cluster in tqdm(cluster):
        cluster_num += 1
        if len(sub_cluster) > 1:
            idx = 0
            for img_num in sub_cluster:
                idx += 1
                filename = os.listdir(config.DIRECTORY)[img_num]
                if filename.endswith(".jpg"):
                    img = cv2.imread(os.path.join(config.DIRECTORY, filename), cv2.IMREAD_COLOR)
                    cv2.imwrite(os.path.join(config.CLUSTER_DIRECTORY, str(cluster_num) + "_" + str(idx) + ".jpg"), img)
    print('')

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

def Summary(count_loop, elapsed_time):
    # 각 효율성 계산
    efficiency = get_Efficiency(total_iter=count_loop)
    limited_efficiency = get_Limited_Compare_Efficiency(total_iter=count_loop)

    # spec summary
    print("주 소요구간 반복 횟수: {}".format(count_loop))
    print("소요 시간: {} sec".format(round(elapsed_time, 4)))
    print("(캐시 사용)시간 효율: {}%".format(round(limited_efficiency, 4)))
    print("(총)시간 효율: {}%".format(round(efficiency, 4)))

