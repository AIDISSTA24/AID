#
# Copyright (c) 2020 Vitalis Salis.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import os


def get_lambda_name(counter):
    return "<lambda{}>".format(counter)


def get_dict_name(counter):
    return "<dict{}>".format(counter)


def get_list_name(counter):
    return "<list{}>".format(counter)


def get_int_name(counter):
    return "<int{}>".format(counter)


def join_ns(*args):
    return ".".join([arg for arg in args])


def to_mod_name(name, package=None):
    return os.path.splitext(name)[0].replace("/", ".")


#能够比较这两个是否是等价的
#examples\miio\device.Device.get_properties
#miio.device.Device.get_properties

#情况不完备
#time 
#device.Datetime
def equal_attribute(method1, method2):
    if method1 == method2:
        return True
    md1 = method1.replace("\\", ".")
    md2 = method2.replace("\\", ".")

    if md1 in md2:
        long = md2
        short = md1
    elif md2 in md1:
        long = md1
        short = md2
    else:
        return False
    
    #处理名称出现部分匹配的情况，例如Datetime和time
    if long.split(short)[-1] == '' and long.split(short)[0][-1] == '.':
        return True
    else:
        return False
    #return md1 in md2 or md2 in md1

#candidate: examples\miio\device.Device.get_properties
#methodset: miio.device.Device.get_properties

#candidate: examples\miio\device.Device.__init__.data
#methodset: examples\miio\device.Device.__init__

#candidate: miio.device.Device.get_properties.value
#methodset: examples\miio\device.Device.get_properties

#这个是真实情况
#candidate: miio.device.Device.get_properties
#methodset: examples\miio\device.Device.get_properties



def is_method_node(candidate, methodset):

    if candidate in methodset:
        return True

    for method in methodset:
        m1 = candidate.split("\\")[-1]
        m2 = method.split("\\")[-1]

        if m1 in m2:
            return True
        #结果是空字符串
        if m2 in m1 and m1.split(m2)[-1] == '':
            return True
            
        #"miio.device.Device.get_properties".split("device.Device.get_properties")[-1]

    '''for method in methodset:
        md1 = candidate.replace("\\", ".")
        md2 = method.replace("\\", ".")
        if md1 in md2 or md2 in md1:
            return True'''
        
    return False
