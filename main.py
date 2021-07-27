
import numpy as np
import time
from utils import *


if __name__ == '__main__':
    config = Config()
    print("BEFORE config.NUM_IMAGES : " , config.NUM_IMAGES)
    config.NUM_IMAGES = check_image_size()
    print("AFTER config.NUM_IMAGES : " , config.NUM_IMAGES)
    # 이미지 개수만큼 boolean type 의 캐시 메모리 생성
    cache = np.zeros(config.NUM_IMAGES, dtype=bool)

    start = time.time()  # 타이머 시작
    #cv2.ocl.setUseOpenCL(True)  # 속도 올려준다고 하는데 잘 모르겠음
    remain_list = []
    cluster = []
    # 모든 이미지들에 대해서 Feature descriptor 구하기
    feature_list, cache, discard_recommend_list = get_Feature_Point(cache)
    # 이미지들끼리 Feature Matching을 통해 비교
    count_loop, remain_list, cluster = find_Feature_Matching(feature_list, cache, remain_list, cluster)
    elapsed_time = time.time() - start # 타이머 종료

    # 결과 요약
    Summary(count_loop, elapsed_time, config.NUM_IMAGES)
    # 이미지 저장
    save_Result_At_Directory(cache, remain_list, discard_recommend_list, cluster)
