# -*- coding:utf-8 -*-
import logging
from PIL import Image, ImageDraw, ImageFont
# from base.logger.loger import logger_pim as logger
import time
import os
import zipfile

# OUT_LOG_DIR = "D:\\git_repos\\xiaomi_tools\\out\\PicResource\\"
OUT_LOG_DIR = os.getcwd()  # 默认保存图片至当前文件的目录
TIME_FORMAT = time.strftime("%Y%m%d_%H%M")
DEFAULT_OUT_DIR = os.path.join(OUT_LOG_DIR, TIME_FORMAT)
DEFAULT_FRONT_TYPE = 'C:\\Windows\\Fonts\\simhei.ttf'


def get_logger(level=logging.DEBUG, to_file=True):
    # 配置日志
    logger = logging.getLogger("PIM_TEST")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    logger.setLevel(level=level)

    # 配置保存日志到文件
    if to_file:
        handler = logging.FileHandler("{}\\pim_log.txt".format(DEFAULT_OUT_DIR), encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # 配置串口打印
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


logger = get_logger()


# 将dir_name中的文件，打包压缩至dir_name, zip_name_path
def zip_dir(dir_name, zip_name_path):
    if os.path.isfile(zip_name_path):
        os.remove(zip_name_path)
        logger.warning("文件存在，先删除文件")

    file_list = []
    if os.path.isfile(dir_name):
        file_list.append(dir_name)
    else:
        for root, dirs, files in os.walk(dir_name):
            for name in files:
                file_list.append(os.path.join(root, name))
    logger.info("压缩了{}个文件".format(len(file_list)))

    zf = zipfile.ZipFile(zip_name_path, "w", zipfile.zlib.DEFLATED)

    for tar in file_list:
        arcname = tar[len(dir_name):]

        zf.write(tar, arcname)
    zf.close()


# 解压缩zip文件
def unzip_file(zipfilename, unziptodir):
  if not os.path.exists(unziptodir): os.mkdir(unziptodir, "0777")
  zfobj = zipfile.ZipFile(zipfilename)
  for name in zfobj.namelist():
    name = name.replace('\\','/')
    if name.endswith('/'):
      os.mkdir(os.path.join(unziptodir, name))
    else:
      ext_filename = os.path.join(unziptodir, name)
      ext_dir= os.path.dirname(ext_filename)
      if not os.path.exists(ext_dir) : os.mkdir(ext_dir,"0777")
      outfile = open(ext_filename, 'wb')
      outfile.write(zfobj.read(name))
      outfile.close()


class PicResource(object):
    """ 生成图片
    out_path 为保存图片的目录
    test=PicResource(out_path)  # out_path非必填，默认值为DEFAULT_OUT_DIR
    test.set_new_pic(100,100)  # 设置图片像素
    test.set_front_size(200)  # 设置字体大小，有默认值，可不设置
    test.set_align("left"，10) # 设置字体对其方式为向左对其，左边像素为10开始，此配置为默认值
    test.set_align("middle")  # 设置字体对其方式为居中，有默认值，可不设置
    test.set_interval(100)  # 设置每行字体居住间隔，有默认值10，可不设置
    test.add_text("红色")  # 图片中增加文字
    test.save_pic(file_name)  # 将图片保存到out_path，默认图片格式为jpg
    test.save_pic(file_name, pic_format="png")  # 将图片保存到out_path， 保存图片格式为png
    test.show() # 查看当前生成图片
    test.get_out_path() # 获取当前图片保存位置

    """
    def __init__(self, out_path=DEFAULT_OUT_DIR):
        self.__width = None
        self.__high = None
        self.__draw = None
        self.__new_img = None
        self.__font = None
        self.__align_type = None
        self.__left = None
        self.__font_type = None
        self.__interval = None
        self.__x = None
        self.__y = None

        # 默认背景颜色
        self.__default_color = (100, 100, 100, 255)

        # 默认图片保存位置
        self.__out = None
        self.__set_out_path(out_path)

    def __init_params(self):
        # 设置默参数
        self.__width = None
        self.__high = None
        self.__draw = None
        self.__new_img = None
        self.__font = None
        self.__align_type = "left"
        self.__left = 10
        self.__font_type = DEFAULT_FRONT_TYPE
        self.__interval = 10
        self.__x = 0
        self.__y = 0

    def set_new_pic(self, width, high, color=None):
        # 每次新建图片，初始化参数
        self.__init_params()

        self.__width = width
        self.__high = high
        if color is None:
            color = self.__default_color
        self.__new_img = Image.new('RGBA', (int(width), int(high)), color)
        self.__draw = ImageDraw.Draw(self.__new_img)

    def get_out_path(self):
        return self.__out

    def set_align(self, align_type, num=None):
        if align_type == "left":
            if num is not None:
                self.__left = num
            self.__align_type = align_type

        elif align_type == "middle":
            self.__align_type = align_type

    def set_interval(self, interval):
        self.__interval = interval

    def set_front_size(self, size):
        self.__font = ImageFont.truetype(self.__font_type, size)

    def add_text(self, text, color=(0, 0, 0)):
        y = self.__y + self.__interval
        fnt_size = self.__font.getsize(text)
        if self.__align_type == "left":
            x = self.__left
        elif self.__align_type == "middle":
            x = (self.__width - fnt_size[0]) / 2

        self.__draw.text((x, y), text, font=self.__font, fill=color)
        self.__y += fnt_size[1]

    def show(self):
        self.__new_img.show()

    def save_pic(self, file_name, pic_format="jpg"):
        file_name = "{}.{}".format(file_name, pic_format)
        file_path = os.path.join(self.__out, file_name)


        if pic_format == "jpg":
            self.__new_img = self.__new_img.convert('RGB')

        elif pic_format == "png":
            pass
        logger.info(file_path)
        self.__new_img.save(file_path)

    def __set_out_path(self, out_path=DEFAULT_OUT_DIR):
        # 如果目录不存在，新建目录
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        self.__out = out_path


class ProductAssert(object):
    """为商品家资源图生成图片

    # 调用ProductAssert
    test = ProductAssert()

    # 设置生成图片的类型，目前支持的类型，在self.__support_type变量中，如果不在变量中，不生成该类型图片
    # 不设置此项，默认支持self.__support_type中所有类型，不同平台需要类型不一样，最好进行设置
    test.set_out_assert_type(["主图", "透明图"])

    # 设置图片类型的格式，包含像素，图片格式，大小目前不支持
    # 没有设置的话，默认高为self.__default_high，宽为__default_weight
    # 同样货号不同平台，同样类型需要的图片像素不一样，格式不一样，最好进行设置
    test.set_asset_type_size({"主图":[800, 800],"透明图":[*, *]})

    # 根据货号列表和颜色列表，生成资源图
    test.get_asserts(["305089"], ["Color1"])

    # 打包资源图
    test.zip_asserts()
    """
    def __init__(self, out_path=DEFAULT_OUT_DIR):
        self.__spu_list = None
        self.__color_list = None
        self.__pic_tool = PicResource(out_path)
        self.__full_name = None

        # 支持的生成资源图的类型
        self.__support_type = ["主图", "透明图", "颜色图", "竖图", "吊牌", "水洗标", "分享图", "鞋盒图", "列表图", "无线主图"]
        self.__ignore_type = ["主图视频", "视频主图", "白底图", "场景图", "全画图", "详情页素材图", "其他"]
        self.__default_high = 800
        self.__default_weight = 800
        # 生成资源图类型列表，默认为支持的所有类型
        self.__assert_type_list = self.__support_type
        # 设置生成资源图类型，图片的参数，像素，格式，大小目前不支持
        self.__asset_type_size = {}
        self.__out = out_path

    def set_out_assert_type(self, assert_type_list):
        out_type = []
        for assert_type in assert_type_list:
            if assert_type in self.__support_type:
                out_type.append(assert_type)
            else:
                # 如果assert_type为忽略类型，则不报错，否则打印warning消息
                if assert_type not in self.__ignore_type:
                    logger.warning("不支持{}类型的资源图".format(assert_type))
        self.__assert_type_list = out_type

    # 配置不同asset_type的图片格式
    def set_asset_type_size(self, size_dict):
        logger.debug("set_asset_type_size 参数为{}".format(size_dict))

        # 校验输入参数类型为dict
        assert type(size_dict) == dict, "set_asset_type_size:输入的size_dict[{}]，类型不正确，应该为dict，而不是{}".\
            format(size_dict, type(size_dict))

        tmp_dict = {}
        # 只记录支持的asset_type
        for asset_type in size_dict:
            if asset_type in self.__support_type:
                tmp_list = size_dict[asset_type]
                # 校验asset_type的value为两个数字或None，如果不满足要求，不保存
                if type(tmp_list) != list:
                    logger.error("输入dict中，{}的值[{}]不符合要求，类型应该为list，而不是{}\n".format(asset_type, tmp_list, type(tmp_list)))
                    logger.error("正确的应该为[weight, high], key:[100, 100] 或 [100:None], 且列表长度等于2")
                    continue
                elif len(tmp_list) != 2:
                    logger.error("输入dict中，{}的值[{}]不符合要求，列表长度应该等于2，而不是{}".format(asset_type, tmp_list, len(tmp_list)))
                    logger.error("正确的应该为[weight, high],key:[100, 100] 或 [100:None], 且列表长度等于2")
                    continue
                else:
                    pass

                weight, high = tmp_list
                if weight is None:
                    weight = self.__default_weight

                if high is None:
                    high = self.__default_high

                if type(weight) != int:
                    logger.error("输入dict中，{}的值[{}]不符合要求，[weight, high]中 weight应该类型为int，而不是{}"
                                 .format(asset_type, tmp_list, type(weight)))
                    logger.error("正确的应该为[weight, high],key:[100, 100] 或 [100:None], 且列表长度等于2")
                    continue

                if type(high) != int:
                    logger.error("输入dict中，{}的值[{}]不符合要求，，[weight, high]中 high应该类型为int，而不是{}"
                                 .format(asset_type, tmp_list, type(high)))
                    logger.error("正确的应该为[weight, high],key:[100, 100] 或 [100:None], 且列表长度等于2")
                    continue

                tmp_dict[asset_type] = [weight, high]

        self.__asset_type_size = size_dict

    # 根据货号和颜色生成资源图
    def get_asserts(self, spu_list, color_list, is_full=False):
        self.__spu_list = spu_list
        self.__color_list = color_list
        self.__full_name = is_full

        for spu in self.__spu_list:
            for color_name in self.__color_list:
                if self.__full_name:
                    color_code = color_name
                else:
                    color_code = "{}{}".format(spu, color_name)
                self.draw_assert_cc(spu, color_code)

    # 根据cc生成资源图
    def draw_assert_cc(self, spu, cc):
        for assert_type in self.__assert_type_list:
            self.draw_assert_type(assert_type, spu, cc)

    # 根据资源图类型生成资源图
    def draw_assert_type(self, assert_type, spu, cc):
        if assert_type in ["主图", "无线主图"]:
            for index in range(1, 6):
                file_name = "{}-{}-{}-{}".format(spu, assert_type, index, cc)
                self.__drew_assert(assert_type, spu, cc, index)
                self.__pic_tool.save_pic(file_name)
        else:
            file_name = "{}-{}-{}".format(spu, assert_type, cc)
            self.__drew_assert(assert_type, spu, cc)
            if assert_type =="透明图":
                self.__pic_tool.save_pic(file_name, pic_format="png")
            else:
                self.__pic_tool.save_pic(file_name)
        return

    # 将生成文件压缩至zip格式
    def zip_asserts(self, zip_name=None, suffix=None, out_path=None):
        if zip_name is None:
            zip_name = self.__get_default_zip_name(suffix=suffix)

        if out_path is None:
            out_path = self.__out

        zip_path = os.path.join(out_path, zip_name)
        zip_dir(self.__out, zip_path)

    # 获取资源图保存位置
    def get_out_path(self):
        return self.__out

    def __drew_assert(self, assert_type, spu, cc, pic_index=None):
        width, high = self.__get_asset_type_size(assert_type)
        self.__pic_tool.set_new_pic(width, high)
        self.__pic_tool.set_front_size(100)
        self.__pic_tool.set_align("middle")
        self.__pic_tool.set_interval(100)

        text = "测试商品图片"
        self.__pic_tool.add_text(text)

        self.__pic_tool.set_front_size(50)
        text = "SPU:{}".format(spu)
        self.__pic_tool.add_text(text)

        text = "CC:{}".format(cc)
        self.__pic_tool.add_text(text)

        if pic_index:
            text = "{}:{}".format(assert_type, pic_index)
        else:
            text = assert_type
        self.__pic_tool.add_text(text)

        text = "像素:{}*{}".format(width, high)
        self.__pic_tool.add_text(text)

        text = "Timestamp:{}".format(TIME_FORMAT)
        self.__pic_tool.add_text(text)

    def __get_asset_type_size(self, asset_type):
        if asset_type not in self.__asset_type_size:
            return [self.__default_weight, self.__default_high]

        return self.__asset_type_size[asset_type]

    # 生成默认压缩文件名称
    # 默认图片规则：
    # 当只有一个spu和一个颜色，名称为[spuId_colorCode.zip]
    # 当只有一个spu和多个(3个)颜色，名称为[spuId_3cc.zip]
    # 当只有多个spu，名称为[spuId1_spuId2_ncc.zip]
    def __get_default_zip_name(self, prefix="asset", suffix=None):
        spu_name = "_".join(self.__spu_list)
        if len(self.__spu_list) == 1 and len(self.__color_list) == 1:
            zip_name = "{}{}".format(spu_name, self.__color_list[0])
        elif len(self.__color_list) == 1:
            zip_name = "{}_{}".format(spu_name, self.__color_list[0])
        else:
            zip_name = "{}_{}cc".format(spu_name, len(self.__color_list))

        if prefix is not None:
            zip_name = prefix + "_" + zip_name

        if suffix is not None:
            zip_name = zip_name + "_" + suffix

        zip_name += ".zip"
        return zip_name


class ProductPdp(object):
    """为商品家生成第三方资源图

    # ProductPdp
    test = ProductPdp()

    # 设置图片类型的格式，包含像素，图片格式，大小目前不支持
    # 没有设置的话，默认高为self.__default_high，宽为__default_weight
    # 同样货号不同平台，同样类型需要的图片像素不一样，格式不一样，最好进行设置
    test.set_asset_type_size({"主图":[],"透明图":[]})

    # 根据货号列表生成3张详情页，详情页格式为(spuId-PC-1.jpg)
    test.get_third_part_pdp(["spuId"], dpd_type="PC", num=3)

    # 打包第三方详情页
    test.zip_asserts()
    """
    def __init__(self, out_path=DEFAULT_OUT_DIR):
        self.__spu_list = None
        self.__pic_tool = PicResource(out_path)
        self.__pdp_num = None
        self.__default_high = 800
        self.__default_weight = 800
        self.__pdp_size = [750, 600]
        self.__out = out_path

    def get_third_part_pdp(self, spu_list, dpd_type="PC", num=3):
        self.__pdp_num = num
        self.__spu_list = spu_list
        for spu in spu_list:
            self.__draw_pdp(spu, dpd_type, num)

    def __get_default_zip_name(self, prefix="pdp", suffix=None):
        spu_name = "_".join(self.__spu_list)
        zip_name = "{}_{}pic".format(spu_name, self.__pdp_num)

        if prefix is not None:
            zip_name = prefix + "_" + zip_name

        if suffix is not None:
            zip_name = zip_name + "_" + suffix

        zip_name += ".zip"
        return zip_name

    def zip_asserts(self, zip_name=None, suffix=None, out_path=None):
        print(zip_name)
        # 如果没有设置压缩文件的名称，则自定义设置
        if zip_name is None:
            zip_name = self.__get_default_zip_name(suffix=suffix)

        if out_path is None:
            out_path = self.__out
        zip_path = os.path.join(out_path, zip_name)
        zip_dir(self.__out, zip_path)

    def __draw_pdp(self, spu, dpd_type, num):
        for index in range(1, num+1):
            tmp_index = "0" + str(index)
            file_name = "{}-{}-{}".format(spu, dpd_type, tmp_index)
            self.__drew_one_pdp(spu, index)
            self.__pic_tool.save_pic(file_name)

    # 生成一张详情页
    # 根据输入参数不一样，生成文案不一样的详情页
    def __drew_one_pdp(self, spu, pic_index):
        weight, high = self.__pdp_size
        self.__pic_tool.set_new_pic(weight, high)
        self.__pic_tool.set_front_size(100)
        self.__pic_tool.set_align("middle")
        self.__pic_tool.set_interval(100)

        text = "详情页"
        self.__pic_tool.add_text(text)

        self.__pic_tool.set_front_size(50)
        text = "SPU:{}".format(spu)
        self.__pic_tool.add_text(text)

        text = "index:{}".format(pic_index)
        self.__pic_tool.add_text(text)

        text = "像素:{}*{}".format(weight, high)
        self.__pic_tool.add_text(text)

    def get_out_path(self):
        return self.__out


class ProductMaterial(object):
    def __init__(self, out_path=DEFAULT_OUT_DIR):
        self.__spu_list = None
        self._pic_tool = PicResource()
        self.__out = out_path

    def generate_pic(self, spu_list):
        self.__spu_list = spu_list
        for one in self.__spu_list:
            self.get_p(one)
            self.get_pp(one)
            self.get_xj(one)
            self.get_m(one)

    def get_p(self, spu_id):
        file_name = "{}-p-f".format(spu_id)
        self.__drew_pic(600, 600, file_name)
        self._pic_tool.save_pic(file_name, pic_format="jpg")

        file_name = "{}-p-z".format(spu_id)
        self.__drew_pic(580, 580, file_name)
        self._pic_tool.save_pic(file_name, pic_format="jpg")

    def get_pp(self, spu_id):
        file_name = "{}-pp-f".format(spu_id)
        self.__drew_pic(350, 350, file_name)
        self._pic_tool.save_pic(file_name, pic_format="jpg")

        file_name = "{}-pp-z".format(spu_id)
        self.__drew_pic(350, 350, file_name)
        self._pic_tool.save_pic(file_name, pic_format="jpg")

    def get_xj(self, spu_id):
        for index in range(1, 6):
            file_name = "{}-xj-{}".format(spu_id, index)
            self.__drew_pic(560, 560, file_name)
            self._pic_tool.save_pic(file_name, pic_format="jpg")

    def get_m(self, spu_id):
        for index in range(1, 6):

            file_name = "{}-m-1-{}".format(spu_id, index)
            self.__drew_pic(560, 560, file_name)
            self._pic_tool.save_pic(file_name, pic_format="jpg")

    def __drew_pic(self, weight, high, file_name):
        self._pic_tool.set_new_pic(high, weight)
        self._pic_tool.set_front_size(50)
        self._pic_tool.set_align("middle")
        self._pic_tool.set_interval(50)

        self._pic_tool.add_text(file_name)

        text = "{}*{}".format(weight, high)
        self._pic_tool.add_text(text)

    def zip_asserts(self, zip_name, out_path=None):
        if out_path is None:
            out_path = self.__out
        zip_path = os.path.join(out_path, zip_name)
        zip_dir(self.__out, zip_path)


class ProductPlatform(object):
    """ 平台参数配置，由于没有平台都是固定的，故写成全局变量，而是写在代码里
    # ProductPdp
    test = ProductPlatform()


    """
    def __init__(self):
        self.__spu_list = None
        self.__color_list = None
        self.__platform = None
        self.__full_name = None

        self.__out = None
        self.__set_out_path()
        self.__product_assert = ProductAssert(self.__out+"/资源图")
        self.__product_pdp = ProductPdp(self.__out+"/详情页")
        # self.__product_me = ProductMaterial(self.__out+"素材图")

        # 支持的生成的类型
        self.__support_platform = ["TMALL", "JD", "VIP", "YAHOO", "MOMO", "SUNING", "WEBSITE"]
        # self.__support_platform = ["TMALL", "JD", "VIP", "WEBSITE", "JUHUASUAN", "KAOLA", "PINDUODUO", "YAHOO", "MOMO"]
        self.__support_type = ["主图", "透明图", "颜色图", "竖图", "吊牌", "水洗标", "鞋盒图", "分享图", "列表图", "无线主图"]
        # 天猫支持：主图，无线主图，主图视频，颜色图，透明图，竖图，吊牌，水洗标，鞋盒图，详情页素材图，视频主图，白底图，
        # 场景图，全画图，其他
        # 京东支持：主图，列表图，主图视频，透明图，详情页素材图，其他
        # 唯品会支持：主图，主图视频，颜色图，透明图，竖图，详情页素材图，其他
        # 官方商城支持：主图，主图视频，颜色图，透明图，竖图，详情页素材图，其他
        # 聚划算支持：主图
        # 考拉海购支持：主图，主图视频，颜色图，透明图，竖图，详情页素材图，其他
        # 拼多多支持：主图，主图视频，颜色图，透明图，竖图，详情页素材图，其他
        # 雅虎支持：主图，主图视频，颜色图，透明图，竖图，详情页素材图，其他
        # 陌陌支持：主图，主图视频，颜色图，透明图，竖图，详情页素材图，其他
        self.__default_support_type = {
            "TMALL": ["主图", "无线主图", "主图视频", "颜色图", "透明图", "竖图", "吊牌", "水洗标", "鞋盒图", "详情页素材图",
                      "视频主图", "白底图", "场景图", "全画图", "其他"],
            "JD": ["主图", "列表图", "主图视频", "颜色图", "透明图", "详情页素材图", "其他"], #颜色图后加
            "VIP": ["主图", "主图视频", "颜色图", "透明图", "竖图", "详情页素材图", "其他"],
            "WEBSITE": ["主图", "主图视频", "颜色图", "分享图", "透明图", "竖图", "详情页素材图", "其他"],
            "JUHUASUAN": ["主图"],
            "KAOLA": ["主图", "主图视频", "颜色图", "透明图", "竖图", "详情页素材图", "其他"],
            "PINDUODUO": ["主图", "主图视频", "颜色图", "透明图", "竖图", "详情页素材图", "其他"],
            "YAHOO": ["主图", "主图视频", "颜色图", "透明图", "竖图", "详情页素材图", "其他"],
            "MOMO": ["主图", "主图视频", "颜色图", "透明图", "竖图", "详情页素材图", "其他"],
            "SUNING": ["主图", "主图视频", "颜色图", "透明图", "竖图", "详情页素材图", "其他"],
        }
        self.__default_assert_size = {
            "TMALL": {
                "主图": [800, 800],
                "无线主图": [800, 800],
                "吊牌": [460, 460],
                "竖图": [800, 1200],
                "透明图": [800, 800],
                "颜色图": [800, 800],
            },
            "JD": {
                "主图": [800, 800],
                "无线主图": [800, 800],
                "吊牌": [460, 460],
                "竖图": [800, 800],
                "透明图": [800, 800],
            },
            "WEBSITE": {
                "主图": [972 , 1296],
                "颜色图": [972 , 1296],
            },
            "SUNING": {
                "主图": [800, 800], #白底正面图，＜2M， PNG、JPG、JPEG
                "竖图": [800, 1200], #<2M， jpg、png、jpeg、gif
                "透明图": [800, 800], #正面图，2M，PNG
                "颜色图": [800, 800],
                "分享图": [800, 800],
            },
            "VIP": {
                "主图": [1200, 1200],
                "颜色图": [1200, 1200],
                "竖图": [950, 1200],
                "透明图": [5000, 5000],
            },
            "JUHUASUAN": {},
            "KAOLA": {},
            "PINDUODUO": {},
            "YAHOO": {
                "主图": [800, 800],
                "颜色图": [800, 800],
            },
            "MOMO": {
                "主图": [800, 800],
                "颜色图": [800, 800],
            },
        }
        self.__assert_type_list = []
        self.__assert_type_size = {}

    def __init_params(self):
        # 初始化参数，每次获取资源图，需要将上次保存的参数进行初始化，以免影响后面生成图片的准确性
        self.__spu_list = None
        self.__color_list = None
        self.__platform = None
        self.__assert_type_list = []
        self.__assert_type_size = {}
        self.__full_name = None

    def __set_assert_type(self, platform):
        self.__platform = str(platform)
        platform = self.__platform.upper()
        logger.debug(self.__support_platform)
        assert platform in self.__support_platform, "ERROR!!! 目前不支持[{}]类型".format(self.platform)

        # 获取默认支持的资源图类型, 如果没有配置则不设置
        if platform in self.__default_support_type:
            self.__assert_type_list = self.__default_support_type[platform]

        # 获取资源类型的像素, 如果没有配置则不设置
        if platform in self.__default_assert_size:
            self.__assert_type_size = self.__default_assert_size[platform]

    def __set_spu_color(self, spu_list, color_list):
        self.__spu_list = spu_list
        self.__color_list = color_list

    def get_asserts(self, spu_list, color_list, platform=None, is_full=False, zip_name=None):
        self.__full_name = is_full
        self.__set_params(spu_list, color_list, platform)
        self.__product_assert.get_asserts(self.__spu_list, self.__color_list, is_full)
        self.__product_assert.zip_asserts(zip_name=zip_name, suffix=self.__platform)
        self.__product_pdp.get_third_part_pdp(self.__spu_list)
        self.__product_pdp.zip_asserts(zip_name=zip_name, suffix=self.__platform)

    def __set_out_path(self, out_path=DEFAULT_OUT_DIR):
        # 如果目录不存在，新建目录
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        self.__out = out_path

    def __set_params(self, spu_list, color_list, platform=None):
        # 初始化自己的参数
        self.__init_params()
        if platform is None:
            logger.warning("没有输入平台，默认平台为天猫(TMALL)")
            platform = "TMALL"

        # 设置self.product_tool的参数
        self.__set_assert_type(platform)
        self.__set_spu_color(spu_list, color_list)

        if len(self.__assert_type_list) > 0:
            self.__product_assert.set_out_assert_type(self.__assert_type_list)

        if len(self.__assert_type_size) > 0:
            self.__product_assert.set_asset_type_size(self.__assert_type_size)

    def __is_support_platform(self):
        platform = self.__platform.upper()
        if platform in self.__support_platform:
            return True
        logger.error("ERROR!!! 目前不支持[{}]类型".format(platform))
        return False

class ProductDefault(object):

    def generate_tmall(self):
        self.get_pic("主图", 800, 800)
        self.get_pic("吊牌", 460, 460)
        self.get_pic("竖图", 800, 1200)
        self.get_pic("透明图", 800, 800, pic_format="png")
        self.get_pic("颜色图", 800, 800)
        self.get_pic("无线主图", 800, 800)
        self.get_pic("详情页", 790, 300)

    def generate_suning(self):
        self.get_pic("主图1", weight=800, high=800, other_list=["平台：苏宁"])
        self.get_pic("主图2", weight=800, high=800, other_list=["平台：苏宁"])
        self.get_pic("主图3", weight=800, high=800, other_list=["平台：苏宁"])
        self.get_pic("主图4", weight=800, high=800, other_list=["平台：苏宁"])
        self.get_pic("主图5", weight=800, high=800, other_list=["平台：苏宁"])
        self.get_pic("吊牌", weight=460, high=460, other_list=["平台：苏宁"])
        self.get_pic("竖图", weight=800, high=1200, other_list=["平台：苏宁"])
        self.get_pic("透明图", weight=800, high=800, pic_format="png", other_list=["平台：苏宁"])
        self.get_pic("颜色图", weight=800, high=800, other_list=["平台：苏宁"])
        self.get_pic("详情页", weight=750, high=300, other_list=["平台：苏宁"])

    def get_pic(self, file_name, weight, high, pic_format="jpg", other_list=[]):
        pic = self.__drew_pic(weight, high, file_name, other_list=other_list)
        pic.save_pic(file_name, pic_format=pic_format)

    def __drew_pic(self, weight, high, file_name, other_list=[]):
        pic = PicResource()
        pic.set_new_pic(weight, high)
        pic.set_front_size(50)
        pic.set_align("middle")
        pic.set_interval(50)

        text = "默认【{}】".format(file_name)
        pic.add_text(text)
        text = "像素：{}*{}".format(weight, high)
        pic.add_text(text)

        if other_list !=[] and type(other_list)==list:
            for line in other_list:
                pic.add_text(line)


        return pic

# EXCEL_LOG_DIR = "D:\\python_project\\xiaomi_tools\\out\\excel\\"
# excel_path = os.path.join(EXCEL_LOG_DIR, "416375.xlsx")
# out_excel_path = os.path.join(EXCEL_LOG_DIR, "test.xlsx")



# spu_list = ["test00001"]
# test = ProductMaterial()
# test.generate_pic(spu_list)
# new_spu_list(spu_list)
# test.zip_asserts("test.zip", OUT_LOG_DIR)


def draw_tmall_default():
    test = ProductDefault()
    # test.generate_tmall()
    test.generate_suning()

# draw_tmall_default()


# test = ProductAssert()
# test.get_asserts(["spu_id_1", "spu_id_2"], ["Color1", "Color2"])
# test.zip_asserts()
#
# test = ProductPdp()
# test.get_third_part_pdp(["305089", "305089-1"])
# test.zip_asserts()


# spu_list = ["wmv_test", "avi_test", "mpg_test","mpeg_test","3gp_test","mov_test","mp4_test","flv_test","f4v_test","m4v_test","m2t_test","mts_test","rmvb_test","vob_test","mkv_test"]

# spu_list = ["test001", "test002", "test003", "test004", "test005", "test006", "test007", "test008", "test009", "test010", "test011", "test012", "test013", "test014", "test015", "test016", "test017", "test018", "test019", "test020", "test021", "test022", "test023", "test024", "test025", "test026", "test027", "test028", "test029", "test030", "test031", "test032", "test033", "test034", "test035", "test036", "test037", "test038", "test039", "test040", "test041", "test042", "test043", "test044", "test045", "test046", "test047", "test048", "test049", "test050", "test051", "test052", "test053", "test054", "test055", "test056", "test057", "test058", "test059", "test060", "test061", "test062", "test063", "test064", "test065", "test066", "test067", "test068", "test069", "test070", "test071", "test072", "test073", "test074", "test075", "test076", "test077", "test078", "test079", "test080", "test081", "test082", "test083", "test084", "test085", "test086", "test087", "test088", "test089", "test090", "test091", "test092", "test093", "test094", "test095", "test096", "test097", "test098", "test099", "test100"]
def generate():
    spu_list = ["gaptest001", "gaptest002", "gaptest003"] #suning002
    # color_list = ["diaodai"]
    # color_list_with_spu_id = ["Color1", "Color2", "Color3"]
    # color_list_with_spu_id = ["Color1", "Color2", "Color3"]
    test = ProductPlatform()
    # test.get_asserts(spu_list, color_list, platform="VIP", is_full=True)
    # test.get_asserts(["api001"], ["Color1"], platform="TMALL", is_full=False)  #TMALL SUNING WEBSITE
    # test.get_asserts(["vip001"], ["Color1", "Color2", "Color3"], platform="VIP", is_full=False)  #TMALL SUNING WEBSITE
    # test.get_asserts(["test001"], ["test001CASSIA", "test003NATURAL1", "test001HEATHER GREY"], platform="VIP", is_full=True)  #TMALL SUNING WEBSITE
    # test.get_asserts(["gap001"], ["Color1", "Color2", "Color3"], platform="WEBSITE", is_full=False)  #TMALL SUNING WEBSITE
    # test.get_asserts(["suning001"], ["Color1", "Color2", "Color3", "Color4"], platform="SUNING", is_full=False)  # TMALL SUNING WEBSITE
    # test.get_asserts(["vip001"], ["vip001color_code_test"], platform="VIP",
    #                  is_full=True)  # TMALL SUNING WEBSITE
    # test.get_asserts(["yahoo001"], ["Color1", "Color2", "Color3"], platform="YAHOO", is_full=False)  # TMALL SUNING WEBSITE
    # test.get_asserts(["momo001"], ["Color1", "Color2", "Color3"], platform="MOMO",
    #                  is_full=False)  # TMALL SUNING WEBSITE

    test.get_asserts(["LEB60_PIM"], ["Color1"], platform="JD", is_full=False)  #TMALL SUNING WEBSITE
generate()