
class Config(object):
    # 데이터셋의 이미지 총 개수
    NUM_IMAGES = 40000  # (수정 할 필요 없음)
    CATEGORY = 'car'  # 데이터셋 폴더 이름 여기에 수정

    # 각 데이터셋 마다 기준이 달라질 수 있음
    THRESHOLD_RATE = 0.7  # car
    THRESHOLD_SIM = 8  # car
    # THRESHOLD_M = 0.7  # person
    # THRESHOLD_C = 5  # person

    # 현재 이미지부터 몇 개의 이미지까지 비교할 것인지 (비교 데이터 수 제한)
    #MAX_ITERATE = 1000  # person
    MAX_ITERATE = 100  # car

    # 원본 데이터셋이 존재하는 폴더 경로
    DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\' + CATEGORY
    # DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\image'

    # 동일한 이미지를 제거한 새로운 데이터셋을 저장할 폴더 경로
    NEW_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\new_' + CATEGORY

    # 중복이라고 판단되어 제거된 이미지들이 저장된 폴더 경로
    EXCEPT_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\dup_' + CATEGORY
    #EXCEPT_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\dup_image'

    DISCARD_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\bad_' + CATEGORY

    CLUSTER_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\cluster_' + CATEGORY

    # 아무것도 사용하지 않았을 때 예상 순환 횟수에 대해 효율성 계산
    def get_Efficiency(self, total_iter):
        # 기존 시간복잡도는 O(n^2)
        original_iter = Config.NUM_IMAGES * Config.NUM_IMAGES
        return ((original_iter - total_iter) / original_iter) * 100.0

    # 비교 데이터 수에 제한을 걸었을 때 효율성 계산
    def get_Limited_Compare_Efficiency(self, total_iter):
        # 기존 시간복잡도는 O(n^k) k는 비교할 주변 이미지의 최대 개수
        original_iter = Config.NUM_IMAGES * Config.MAX_ITERATE
        return ((original_iter - total_iter) / original_iter) * 100.0