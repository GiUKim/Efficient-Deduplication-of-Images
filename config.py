
class config(object):
    # 데이터셋의 이미지 총 개수
    NUM_IMAGES = 21743

    # 동일 이미지로 판단 할 해밍 거리 기준값 (해밍거리가 낮을수록 동일한 이미지일 가능성 높음)
    # 각 데이터셋 마다 기준이 달라짐
    # 자동차 데이터셋에서는 25 정도가 가장 좋은 듯
    THRESHOLD = 24

    # dhash를 구하기 위해 원본 이미지를 리사이징할 때 리사이즈 크기
    # 가로
    resize_width = 9
    # 세로
    resize_height = 8

    # 현재 이미지부터 몇 개의 이미지까지 비교할 것인지 (비교 데이터 수 제한)
    MAX_ITERATE = 100

    # 원본 데이터셋이 존재하는 폴더 경로
    # DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\image'
    DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\person'

    # 동일한 이미지를 제거한 새로운 데이터셋을 저장할 폴더 경로
    # SAVE_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\new_image'
    SAVE_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\person_new_image'

    # 중복으로 판단되어 제거된 이미지들이 저장된 폴더 경로로
    # EXCEPT_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\dup_image'
    EXCEPT_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\person_dup_image'

    # 아무것도 사용하지 않았을 때 예상 순환 횟수에 대해 효율성 계산
    def get_Efficiency(self, total_iter):
        # 기존 시간복잡도는 O(n^2)
        original_iter = config.NUM_IMAGES * config.NUM_IMAGES
        return ((original_iter - total_iter) / original_iter) * 100.0

    # 비교 데이터 수에 제한을 걸었을 때 효율성 계산
    def get_Limited_Compare_Efficiency(self, total_iter):
        # 기존 시간복잡도는 O(n^k) k는 비교할 주변 이미지의 최대 개수
        original_iter = config.NUM_IMAGES * config.MAX_ITERATE
        return ((original_iter - total_iter) / original_iter) * 100.0