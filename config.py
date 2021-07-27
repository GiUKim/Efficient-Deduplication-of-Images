from utils import *

class Config(object):
    # 데이터셋의 이미지 총 개수
    NUM_IMAGES = 100
    #NUM_IMAGES = 40000  # (수정 할 필요 없음)
    CATEGORY = 'person'  # 데이터셋 폴더 이름 여기에 수정

    '''
    각 데이터셋 마다 기준이 달라질 수 있음
    THRESHOLD_RATE 는 고정시카고 THRESHOLD_SIM 을 수정 (상관 없음)
    THRESHOLD_RATE 가 낮을수록 더욱 엄격하게 검증함
    THRESHOLD_SIM 이 높을수록 더욱 엄격하게 검증함 
    Car 가 Person 보다 훨씬 정적이므로 특징점들이 다 살아있어 중복을 잘 발견해내는 경향이 있음 
    '''
    THRESHOLD_RATE = 0.7  # car
    # THRESHOLD_SIM = 8  # car
    THRESHOLD_SIM = 10  # person

    # 현재 이미지부터 몇 개의 이미지까지 비교할 것인지 (비교 데이터 수 제한)
    # 작으면 효율성이 증가하지만 cluster 가 많아져서 중복 데이터가 껴있을 확률이 높아짐
    MAX_ITERATE = 100  # car

    # 원본 데이터셋이 존재하는 폴더 경로
    DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\' + CATEGORY

    # 동일한 이미지를 제거한 새로운 데이터셋을 저장할 폴더 경로
    NEW_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\new_' + CATEGORY

    # 중복이라고 판단되어 제거된 이미지들이 저장된 폴더 경로
    EXCEPT_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\dup_' + CATEGORY

    # 심한 Blur, Noise 들로 Feature 가 발견되지 않은 이미지들이 저장된 폴더 경로 (데이터셋에서 제거 추천)
    DISCARD_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\bad_' + CATEGORY

    # 중복이라고 판단되어 제거된 이미지들이 저장된 폴더 경로
    CLUSTER_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\cluster_' + CATEGORY

    # 아무것도 사용하지 않았을 때 예상 순환 횟수에 대해 효율성 계산
    def get_Efficiency(total_iter, img_total_num):
        # 기존 시간복잡도는 O(n^2)
        original_iter = img_total_num * img_total_num
        return ((original_iter - total_iter) / original_iter) * 100.0

    # 캐시메모리를 사용하여 중복연산을 제거했을 때 효율성 계산
    def get_Limited_Compare_Efficiency(total_iter, img_total_num):
        # 기존 시간복잡도는 O(n^k) k는 비교할 주변 이미지의 최대 개수
        original_iter = img_total_num * Config.MAX_ITERATE
        return ((original_iter - total_iter) / original_iter) * 100.0



