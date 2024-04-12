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
import symtable

import utils

#此代码主要用于分析 Python 代码中的作用域和变量定义，以便在代码分析和静态分析过程中跟踪和管理变量的作用域和定义信息。
#ScopeManager 用于管理多个作用域项，而 ScopeItem 则表示单个作用域，并存储变量定义和计数信息。
class ScopeManager(object):
    """Manages the scope entries"""

    def __init__(self):
        #用于存储各个命名空间的作用域信息的字典
        #key = namespace, value = ScopeItem(namespace, parent)
        self.scopes = {}
    # 处理模块的函数，接受模块名 modulename、文件名 filename 和模块内容 contents 作为参数。
    # 使用 Python 的 symtable 模块来分析模块内容，查找其中的函数和类，并返回它们的名称列表。
    def handle_module(self, modulename, filename, contents):
        functions = []
        classes = []
        # 定义一个递归函数 process 用于处理符号表中的各项内容
        def process(namespace, parent, table):
            # 获取当前表项的名称和类型
            if table.get_name() == "top" and table.get_lineno() == 0:
                # 如果是顶级符号表项，名称为空字符串
                name = "" 
            else:
                name = table.get_name()

            if name:
                fullns = utils.join_ns(namespace, name)
            else:
                fullns = namespace
            # 如果表项类型为函数，将其名称添加到 functions 列表中
            if table.get_type() == "function":
                functions.append(fullns)
            # 如果表项类型为类，将其名称添加到 classes 列表中
            if table.get_type() == "class":
                classes.append(fullns)
            # 创建对应命名空间的作用域
            sc = self.create_scope(fullns, parent)

            for t in table.get_children():
                process(fullns, sc, t)

        process(
            modulename, None, symtable.symtable(contents, filename, compile_type="exec")
        )
        return {"functions": functions, "classes": classes}
    # 处理变量的赋值语句，接受命名空间 ns、变量名 target 和定义 defi 作为参数。它将变量名和定义添加到相应的作用域中。
    def handle_assign(self, ns, target, defi):
        scope = self.get_scope(ns)
        if scope:
            scope.add_def(target, defi)
    # 首先根据给定的当前命名空间 current_ns找到ScopeItem对象
    # 然后根据变量名var_name在ScopeItem对象中找到Definition对象，如果不存在就搜索父节点，在作用域链上查找变量定义，并返回定义信息。
    def get_def(self, current_ns, var_name):
        current_scope = self.get_scope(current_ns)
        while current_scope:
            defi = current_scope.get_def(var_name)
            if defi:
                return defi
            current_scope = current_scope.parent
    #获得对应命名空间的ScopeItem对象
    def get_scope(self, namespace):
        if namespace in self.get_scopes():
            return self.get_scopes()[namespace]
    # 创建新的命名空间的ScopeItem对象
    def create_scope(self, namespace, parent):
        if namespace not in self.scopes:
            sc = ScopeItem(namespace, parent)
            self.scopes[namespace] = sc
        return self.scopes[namespace]

    def get_scopes(self):
        return self.scopes

# 表示单个作用域，并存储变量定义和计数信息
class ScopeItem(object):
    def __init__(self, fullns, parent):
        if parent and not isinstance(parent, ScopeItem):
            raise ScopeError("Parent must be a ScopeItem instance")

        if not isinstance(fullns, str):
            raise ScopeError("Namespace should be a string")
        # 父作用域
        self.parent = parent
        # 该作用域对象下的定义字典
        # key = name定义名称 value = Definition
        self.defs = {}
        self.lambda_counter = 0
        self.dict_counter = 0
        self.list_counter = 0
        # 完整命名空间 
        self.fullns = fullns

    def get_ns(self):
        return self.fullns
    # 返回当前作用域的定义字典
    def get_defs(self):
        return self.defs

    def get_def(self, name):
        defs = self.get_defs()
        if name in defs:
            return defs[name]

    def get_lambda_counter(self):
        return self.lambda_counter

    def get_dict_counter(self):
        return self.dict_counter

    def get_list_counter(self):
        return self.list_counter

    def inc_lambda_counter(self, val=1):
        self.lambda_counter += val
        return self.lambda_counter

    def inc_dict_counter(self, val=1):
        self.dict_counter += val
        return self.dict_counter

    def inc_list_counter(self, val=1):
        self.list_counter += val
        return self.list_counter

    def reset_counters(self):
        self.lambda_counter = 0
        self.dict_counter = 0
        self.list_counter = 0
    # 将变量名和定义添加到作用域的定义字典中
    def add_def(self, name, defi):
        self.defs[name] = defi
    # 合并同名变量的定义信息，如果变量名不存在，则直接添加
    def merge_def(self, name, to_merge):
        if name not in self.defs:
            self.defs[name] = to_merge
            return

        self.defs[name].merge_points_to(to_merge.get_points_to())


class ScopeError(Exception):
    pass
