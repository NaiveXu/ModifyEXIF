# coding:utf-8
from pyexiv2 import Image
import os,re,time
import win32file
import pywintypes

# 时间范式
time1 = re.compile(r"15\d{11}")  # 注意后三位是多余的
time2 = re.compile(r"20\d{6}_\d{6}")
time3 = re.compile(r"IMG_20\d{6}_\d{6}")
time4 = re.compile(r"mmexport20\d{12}")
time5 = re.compile(r"(S|s)creenshot_20\d{6}-\d{6}")
time6 = re.compile(r"wx_camera_15\d{11}")  # 注意后三位是多余的
time7 = re.compile(r"Screenshot_20\d\d-\d\d-\d\d-\d\d-\d\d-\d\d")
NOW_TIME = time.time()
TIME_PATTERNS = [time1, time2, time3, time4, time5, time6, time7]

class my_extractor(Image):
    def __init__(self, filename):
        self.filename = filename
        self.image = Image(filename)
        self.exif = self.image.read_exif()
        self.date_time = 0.0

    # 2个从文件名提取原始时间的函数
    def extract_time_from_datetime_of(self):
        """从filename中直接提取时间信息，转化成时间字符串形式返回"""
        time_example = r"(20\d\d)(\d\d)(\d\d)(?:_|-|)(\d\d)(\d\d)(\d\d)"
        time_raw = re.findall(time_example, self.filename)[0]
        date_time = time_raw[0] + ":"
        for i in range(1, 6):
            date_time += time_raw[i]
            if i == 2:
                date_time += " "
            elif i == 5:
                pass
            else:
                date_time += ":"
        return date_time

    def extract_time_from_timestrip_of(self):
        """
        从filename中提取出时间戳信息,然后转化成时间字符串形式返回
        
        """
        time_example = r"15\d{11}"
        time_splited = int(re.findall(time_example, self.filename)[0][:-3])
        if time_splited <= NOW_TIME:
            # 转化为'2019:05:15 18:00:17'格式
            date_time = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(time_splited))
            return date_time
        else:
            print("Wrong input you dumbass!")
            return None

    def get_time_from_FileName_Of(self, TIME_PATTERNS):
        """
        根据图片的名字获取图片本来的exif时间
        time_Patterns:list, 元素为时间模式，来自于正则表达式
        image_file:str  为图片名字，例如"20190515_180216304_iOS.jpg"
        可以用来修改的名字有
        "1513859190222.jpeg"
        "20150829_170328000.png"
        "IMG_20190520_120207.jpg"
        "mmexport20171117093617.jpg"
        "Screenshot_20190313-214413_WeChat.jpg"
        "wx_camera_1527957631631.jpg"
        """
        # 开始提取操作
        isThisFileHasBeenExtracted = False  # 标记当前文件未被提取
        # 拿6种模式来匹配文件名
        for time_rePattern in TIME_PATTERNS:
            if not isThisFileHasBeenExtracted:
                # 当这个文件还没有被提取的时间的时候再往下走
                if re.search(time_rePattern, self.filename):
                    self.date_time = self.extract_time_from_timestrip_of() if (
                        time_rePattern == time1 or time_rePattern == time6) else self.extract_time_from_datetime_of()
                    
                    isThisFileHasBeenExtracted = True
                    break  # 匹配到了就直接跳出循环就好
                else:  # 如果没有匹配，那么就进行下一次循环
                    continue

        if isThisFileHasBeenExtracted:
            # 如果匹配到了那么直接返回
            # print("Time of {} is {}".format(filename, date_time))
            return True

        else:
            # 没有匹配那就不能从这个方式搞
            return False

    def need_modify(self):
        """
        判断这个图片的EXIF信息是否需要修改，如果不需要的话就直接滚犊子吧,如果需要在进行modify_exit的操作.
        要传入Image.read_exif()这个词典，然后对比时间
        """
        # 首先看看是否存在创建时间，如果不存在直接就要搞
        if "Exif.Photo.DateTimeOriginal" in self.exif.keys():
            # 存在创建时间的话看看和我们需要对比的时间是否一致，不一致也得搞
            if self.exif[
                "Exif.Photo.DateTimeOriginal"
            ] == self.date_time:
                # 相等的话说明不用改,返回个false
                return False
        else:
            # 但凡有一点不让人满意那么就需要修改
            return True

    def change_exif(self):
        """
        image_file为图片名字，例如"20190515_180216304_iOS.jpg"
        注意，应该拍摄日期和创建日期，这2个都要修改的！！！！！！
        如果本身有这些信息的话，那么就不需要修改
        time应为需要修改成的时间，严格按照如下格式'2019:05:15 18:00:17'。如果不是就直接报错。
        没有任何返回值，直接修改。"""
        if self.need_modify():
            self.image.modify_exif({"Exif.Photo.DateTimeOriginal": self.date_time})
            return print(
                "Time of {} has been changed to {}".format(
                    self.filename, self.date_time
                )
            )
        else:
            return print("Error! Can't modify time of {}".format(self.filename))

        


def changeFileCreateTime(path, ctime):
    # path: your file path
    # ctime: Unix timestamp

    # open file and get the handle of file
    # API: http://timgolden.me.uk/pywin32-docs/win32file__CreateFile_meth.html
    handle = win32file.CreateFile(
        path,                          # file path
        win32file.GENERIC_WRITE,       # must opened with GENERIC_WRITE access
        0,
        None,
        win32file.OPEN_EXISTING,
        0,
        0
    )

    # create a PyTime object
    # API: http://timgolden.me.uk/pywin32-docs/pywintypes__Time_meth.html
    PyTime = pywintypes.Time(ctime)

    # reset the create time of file
    # API: http://timgolden.me.uk/pywin32-docs/win32file__SetFileTime_meth.html
    win32file.SetFileTime(
        handle,
        PyTime
    )


def extract_time_from_datetime_of(filename):
    """从filename中直接提取时间信息，转化成时间字符串形式返回"""
    time_example = r"(20\d\d)(?:_|-|)(\d\d)(?:_|-|)(\d\d)(?:_|-|)(\d\d)(?:_|-|)(\d\d)(?:_|-|)(\d\d)"
    time_raw = re.findall(time_example, filename)[0]
    date_time = time_raw[0] + ":"
    for i in range(1, 6):
        date_time += time_raw[i]
        if i == 2:
            date_time += " "
        elif i == 5:
            pass
        else:
            date_time += ":"
    return time.strptime(date_time, '%Y:%m:%d %H:%M:%S')

def extract_time_from_timestrip_of(filename):
    """
    从filename中提取出时间戳信息,然后转化成时间字符串形式返回
    
    """
    time_example = r"15\d{11}"
    time_splited = int(re.findall(time_example, filename)[0][:-3])
    if time_splited <= NOW_TIME:
        # 转化为'2019:05:15 18:00:17'格式
        #date_time = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(time_splited))
        # return date_time
        return time_splited
    else:
        print("Wrong input you dumbass!")
        return None

def get_time_from_FileName_Of(filename, TIME_PATTERNS):
    """
    根据图片的名字获取图片本来的exif时间
    time_Patterns:list, 元素为时间模式，来自于正则表达式
    image_file:str  为图片名字，例如"20190515_180216304_iOS.jpg"
    可以用来修改的名字有
    "1513859190222.jpeg"
    "20150829_170328000.png"
    "IMG_20190520_120207.jpg"
    "mmexport20171117093617.jpg"
    "Screenshot_20190313-214413_WeChat.jpg"
    "wx_camera_1527957631631.jpg"
    """
    # 开始提取操作
    isThisFileHasBeenExtracted = False  # 标记当前文件未被提取
    # 拿6种模式来匹配文件名
    for time_rePattern in TIME_PATTERNS:
        if not isThisFileHasBeenExtracted:
            # 当这个文件还没有被提取的时间的时候再往下走
            if re.search(time_rePattern, filename):
                date_time = extract_time_from_timestrip_of(filename) if (
                    time_rePattern == time1 or time_rePattern == time6) else extract_time_from_datetime_of(filename)
                
                isThisFileHasBeenExtracted = True
                break  # 匹配到了就直接跳出循环就好
            else:  # 如果没有匹配，那么就进行下一次循环
                continue

    return date_time if isThisFileHasBeenExtracted else False
    
    
def change_pic_DateTimeOriginal(image_file):
    '''
    image_file:图片文件的路径，image_file = r"D:\OneDrive - stu.xidian.edu.cn\图片\Comics动漫\元气寿司雄一\a09c6baegy1fz4tufthb3j20ku0acq76.jpg"
    '''
    ## 当图片不存在↓时，说明文件需要进行恢复时间的操作
    ## DateTimeOriginal:拍摄时间_照片拍摄的时间
    #if not "Exif.Photo.DateTimeOriginal" in Image(image_file).read_exif().keys():
        #test_image = my_extractor(image_file)  # 读入提取器中
        #if test_image.get_time_from_FileName_Of(TIME_PATTERNS):
            ## 当可以从文件名中提取到时间的时候，使用提取器中的change_exif()函数
            #test_image.change_exif()
        #else:
            # 当无法从文件名中提取时，用文件的“创建时间|修改时间|最后访问时间”中最早的时间
    temp_time = get_time_from_FileName_Of(image_file, TIME_PATTERNS)

    if temp_time:
        changeFileCreateTime(image_file, temp_time)
        print("Time of {} has been changed to{}".format(image_file, temp_time))
    else:
        file_time_info = os.stat(image_file)
        min_time = min(file_time_info[-3:])
        os.utime(image_file, (min_time, min_time))
        changeFileCreateTime(image_file, min_time)
        print("Time of {} has been changed to{}".format(image_file, min_time))
    
if __name__ == "__main__":
    # 对一整个文件夹内的所有图片进行处理操作
    # 首先要读入整个文件夹内的图片
    # 递归获取，使用os.walk方式
    # 图片存储目录
    pic_dir = r"D:\OneDrive - stu.xidian.edu.cn\PICTURES"
    fileset = set()
    for roots, dirs, files in os.walk(pic_dir):
        for file_name in files:
            fileset.add(os.path.join(roots, file_name))

    for file_name in fileset:
        change_pic_DateTimeOriginal(file_name.replace('\\', '/'))
