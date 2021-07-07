
class config(object):
    # 데이터셋의 이미지 총 개수
    NUM_IMAGES = 21743

    # 동일 이미지로 판단 할 해밍 거리 기준값 (해밍거리가 낮을수록 동일한 이미지일 가능성 높음)
    # 각 데이터셋 마다 기준이 달라질 수 있음
    THRESHOLD = 101  # person

    # dhash를 구하기 위해 원본 이미지를 리사이징할 때 리사이즈 크기
    resize_width = 33 # 가로(dhash 연산때문에 2^n + 1로 하는걸 추천)
    resize_height = 32 # 세로

    # 현재 이미지부터 몇 개의 이미지까지 비교할 것인지 (비교 데이터 수 제한)
    MAX_ITERATE = 300  # person

    # 몇 회의 filtering 작업을 진행 할 것인지
    PROCESSING = 3  # person
    # 각 filtering stage 마다 threshold의 감소량
    TH_REDUCE = 3  # person

    # 원본 데이터셋이 존재하는 폴더 경로
    DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\person'
    # DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\image'

    # 동일한 이미지를 제거한 새로운 데이터셋을 저장할 폴더 경로
    NEW_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\new_person'

    # 중복이라고 판단되어 제거된 이미지들이 저장된 폴더 경로
    EXCEPT_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\dup_image_person'
    #EXCEPT_DIRECTORY = 'C:\\Users\\AI\\PycharmProjects\\project1\\dup_image'

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