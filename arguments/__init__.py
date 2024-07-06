#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

from argparse import ArgumentParser, Namespace
import sys
import os

class GroupParams:
    pass


'''
一个公共的类，利用argparse实现参数配置，其中：
-arg 表示可用 -首字母 配置的参数
-
'''
class ParamGroup:
    '''
    初始化，并将类内参数配置加入argparse
    _ 开头的加入简写-x
    非_开头的只能以全拼开始
    
    '''
    def __init__(self, parser: ArgumentParser, name : str, fill_none = False):
        group = parser.add_argument_group(name)
        for key, value in vars(self).items():
            shorthand = False
            if key.startswith("_"):
                shorthand = True
                key = key[1:]
            t = type(value)
            value = value if not fill_none else None 
            if shorthand:
                if t == bool:
                    group.add_argument("--" + key, ("-" + key[0:1]), default=value, action="store_true")
                else:
                    group.add_argument("--" + key, ("-" + key[0:1]), default=value, type=t)
            else:
                if t == bool:
                    group.add_argument("--" + key, default=value, action="store_true")
                else:
                    group.add_argument("--" + key, default=value, type=t)
    '''
    返回配置参数
    '''
    def extract(self, args):
        group = GroupParams()
        for arg in vars(args).items():
            if arg[0] in vars(self) or ("_" + arg[0]) in vars(self):
                setattr(group, arg[0], arg[1])
        return group

'''
模型相关参数
'''
class ModelParams(ParamGroup): 
    def __init__(self, parser, sentinel=False):
        self.sh_degree = 3 #球协函数纬度
        self._source_path = "" #图像地址
        self._model_path = ""   #模型地址
        self._images = "images" 
        self._resolution = -1 #分辨率
        self._white_background = False #是否白色背景
        self.data_device = "cuda" #数据设备
        self.eval = False
        super().__init__(parser, "Loading Parameters", sentinel)

    def extract(self, args):
        g = super().extract(args)
        g.source_path = os.path.abspath(g.source_path) #找到绝对路径
        return g

'''
 基线相关参数
'''
class PipelineParams(ParamGroup):
    def __init__(self, parser):
        self.convert_SHs_python = False # ？
        self.compute_cov3D_python = False # ？
        self.debug = False # 是否为Debug模式
        super().__init__(parser, "Pipeline Parameters")

'''
优化器相关参数
'''
class OptimizationParams(ParamGroup):
    def __init__(self, parser):
        self.iterations = 30_000 # 迭代次数
        self.position_lr_init = 0.00016 #位置学习率初值
        self.position_lr_final = 0.0000016 #位置学习率终值
        self.position_lr_delay_mult = 0.01 #
        self.position_lr_max_steps = 30_000 #位置学习率最大迭代步数
        self.feature_lr = 0.0025 #特征学习率
        self.opacity_lr = 0.05 #不透明度
        self.scaling_lr = 0.005 #尺度学习率
        self.rotation_lr = 0.001 #旋转学习率
        self.percent_dense = 0.01 #
        self.lambda_dssim = 0.2 # d-ssim损失的系数，对应公式7
        self.densification_interval = 100 #致密化和移除透明的迭代次数
        self.opacity_reset_interval = 3000 #每3000轮设置alpha为接近0的数
        self.densify_from_iter = 500 #??
        self.densify_until_iter = 15_000 #??
        self.densify_grad_threshold = 0.0002 #用于判断致密化的梯度大小
        self.random_background = False #是否随机初始化
        super().__init__(parser, "Optimization Parameters")
    '''
    读取以训练模型的参数
    '''
    def get_combined_args(parser : ArgumentParser):
        cmdlne_string = sys.argv[1:]
        cfgfile_string = "Namespace()"
        args_cmdline = parser.parse_args(cmdlne_string)

        try:
            cfgfilepath = os.path.join(args_cmdline.model_path, "cfg_args")
            print("Looking for config file in", cfgfilepath)
            with open(cfgfilepath) as cfg_file:
                print("Config file found: {}".format(cfgfilepath))
                cfgfile_string = cfg_file.read()
        except TypeError:
            print("Config file not found at")
            pass
        args_cfgfile = eval(cfgfile_string)

        merged_dict = vars(args_cfgfile).copy()
        for k,v in vars(args_cmdline).items():
            if v != None:
                merged_dict[k] = v
        return Namespace(**merged_dict)
