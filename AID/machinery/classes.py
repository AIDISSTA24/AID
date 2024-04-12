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
class ClassManager:
    # 类的构造函数初始化了一个名为 names 的字典，用于存储类的名称和对应的 ClassNode 对象。
    def __init__(self):
        self.names = {}

    def get(self, name):
        if name in self.names:
            return self.names[name]
    # 用于创建一个新的 ClassNode 对象，并将其关联到给定的类名 name 和模块名 module。
    def create(self, name, module):
        if name not in self.names:
            cls = ClassNode(name, module)
            self.names[name] = cls
        return self.names[name]

    def get_classes(self):
        return self.names


class ClassNode:
    # ns 表示类的命名空间，module 表示所属的模块名称。
    def __init__(self, ns, module):
        self.ns = ns
        self.module = module
        # mro 属性保存了类的方法解析顺序
        self.mro = [ns]
    # 用于向当前类的方法解析顺序（MRO）中添加一个父类。
    def add_parent(self, parent):
        if isinstance(parent, str):
            self.mro.append(parent)
        elif isinstance(parent, list):
            for item in parent:
                self.mro.append(item)
        #清除冗余
        self.fix_mro()
    # 用于修复 MRO 列表中的冗余项，确保每个元素在列表中只出现一次。
    def fix_mro(self):
        new_mro = []
        for idx, item in enumerate(self.mro):
            if self.mro[idx + 1 :].count(item) > 0:
                continue
            new_mro.append(item)
        self.mro = new_mro

    def get_mro(self):
        return self.mro

    def get_module(self):
        return self.module
    # 计算和设置当前类的 MRO 列表，确保父类按照正确的顺序出现在 MRO 中
    def compute_mro(self):
        res = []
        self.mro.reverse()
        for parent in self.mro:
            if parent not in res:
                res.append(parent)

        res.reverse()
        self.mro = res

    def clear_mro(self):
        self.mro = [self.ns]
