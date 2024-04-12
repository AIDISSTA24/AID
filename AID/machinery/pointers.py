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
# 基础的指针类，用于管理指向关系
class Pointer(object):
    def __init__(self):
        self.values = set()

    def add(self, item):
        self.values.add(item)

    def add_set(self, s):
        self.values = self.values.union(s)

    def get(self):
        return self.values

    def merge(self, pointer):
        self.values = self.values.union(pointer.values)

# 用于处理文字字面量的指向关系
class LiteralPointer(Pointer):
    STR_LIT = "STRING"
    INT_LIT = "INTEGER"
    UNK_LIT = "UNKNOWN"

    # no need to add the actual item
    def add(self, item):
        if isinstance(item, str):
            self.values.add(item)
        elif isinstance(item, int):
            self.values.add(item)
        else:
            self.values.add(self.UNK_LIT)

# 用于管理名称指针和参数之间的关系
class NamePointer(Pointer):
    def __init__(self):
        super().__init__()
        # 用于将参数位置映射到参数名称
        self.pos_to_name = {}
        # 用于将参数名称映射到参数位置
        self.name_to_pos = {}
        # 用于存储参数名称与参数值集合之间的关系的字典
        self.args = {}
    # 用于确保参数位置是有效的整数。如果参数位置无效，将引发 PointerError 异常。
    def _sanitize_pos(self, pos):
        try:
            int(pos)
        except ValueError:
            raise PointerError("Invalid position for argument")

        return pos
    # 用于获取参数名称对应的参数值集合，如果参数名称不存在，则创建一个新的空集合并返回。
    def get_or_create(self, name):
        if name not in self.args:
            self.args[name] = set()
        return self.args[name]
    # 用于将参数名称与参数值关联，并将它们添加到 args 字典中。
    def add_arg(self, name, item):
        self.get_or_create(name)
        if isinstance(item, str):
            self.args[name].add(item)
        elif isinstance(item, set):
            self.args[name] = self.args[name].union(item)
        else:
            raise Exception()
    # 用于将参数名称与文字字面量参数值关联，根据参数值的类型添加相应的文字字面量类型（例如，字符串或整数文字字面量）到参数值集合中。
    def add_lit_arg(self, name, item):
        arg = self.get_or_create(name)
        if isinstance(item, str):
            arg.add(LiteralPointer.STR_LIT)
        elif isinstance(item, int):
            arg.add(LiteralPointer.INT_LIT)
        else:
            arg.add(LiteralPointer.UNK_LIT)
    # 用于将参数位置、参数名称和参数值关联，并将它们添加到 args 字典中。
    def add_pos_arg(self, pos, name, item):
        pos = self._sanitize_pos(pos)
        if not name:
            if self.pos_to_name.get(pos, None):
                name = self.pos_to_name[pos]
            else:
                name = str(pos)
        self.pos_to_name[pos] = name
        self.name_to_pos[name] = pos

        self.add_arg(name, item)
    # 用于将参数名称与参数值关联，并将它们添加到 args 字典中。
    def add_name_arg(self, name, item):
        self.add_arg(name, item)
    # 用于将参数位置、参数名称和文字字面量参数值关联，并根据参数值的类型添加相应的文字字面量类型到参数值集合中。
    def add_pos_lit_arg(self, pos, name, item):
        pos = self._sanitize_pos(pos)
        if not name:
            name = str(pos)
        self.pos_to_name[pos] = name
        self.name_to_pos[name] = pos
        self.add_lit_arg(name, item)
    # 根据参数位置获取参数值
    def get_pos_arg(self, pos):
        pos = self._sanitize_pos(pos)
        name = self.pos_to_name.get(pos, None)
        return self.get_arg(name)

    def get_arg(self, name):
        if self.args.get(name, None):
            return self.args[name]

    def get_args(self):
        return self.args
    # 获取所有参数位置与参数值集合之间的关系
    def get_pos_args(self):
        args = {}
        for pos, name in self.pos_to_name.items():
            args[pos] = self.args[name]
        return args

    def get_pos_of_name(self, name):
        if name in self.name_to_pos:
            return self.name_to_pos[name]

    def get_pos_names(self):
        return self.pos_to_name
    # 用于合并另一个名称指针对象 pointer 的值和关系到当前名称指针对象。
    def merge(self, pointer):
        super().merge(pointer)
        if hasattr(pointer, "get_pos_names"):
            for pos, name in pointer.get_pos_names().items():
                self.pos_to_name[pos] = name
            for name, arg in pointer.get_args().items():
                self.add_arg(name, arg)


class PointerError(Exception):
    pass
