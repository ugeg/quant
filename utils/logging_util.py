import logging

# 用于打印日志
import time

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def count_time(fun):
    def warpper(*args):
        s_time = time.time()
        fun(*args)
        e_time = time.time()
        t_time = e_time - s_time
        logging.info('%s 耗时：%.2f s', fun.__name__, t_time)
        # print('%s耗时：%s' % (fun.__name__, t_time))

    return warpper
