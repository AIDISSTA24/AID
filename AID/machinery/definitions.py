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
import utils
from machinery.pointers import LiteralPointer, NamePointer

# 管理不同命名空间中的定义信息，并处理定义之间的关系。它的方法允许创建、分配、获取定义，并计算传递闭包以及构建完整的定义关系。
class DefinitionManager(object):
    def __init__(self):
        #用于存储各个命名空间的定义信息的字典
        # key = ns, value = Definition(ns, def_type)
        self.defs = {}

    def create(self, ns, def_type):
        if not ns or not isinstance(ns, str):
            raise DefinitionError("Invalid namespace argument")
        if def_type not in Definition.types:
            raise DefinitionError("Invalid def type argument")
        if self.get(ns):
            raise DefinitionError("Definition already exists")

        self.defs[ns] = Definition(ns, def_type)
        return self.defs[ns]
    # 分配一个已有的定义到指定命名空间 ns
    # 如果是函数定义，则需要创建返回值指针
    def assign(self, ns, defi):
        self.defs[ns] = Definition(ns, defi.get_type())
        self.defs[ns].merge(defi)

        # if it is a function def, we need to create a return pointer
        #为什么？？？？？？？？？？？？？？？？
        if defi.is_function_def():
            # RETURN_NAME = "<RETURN>"
            return_ns = utils.join_ns(ns, utils.constants.RETURN_NAME)
            # NAME_DEF = "NAMEDEF"
            self.defs[return_ns] = Definition(return_ns, utils.constants.NAME_DEF)
            self.defs[return_ns].get_name_pointer().add(
                utils.join_ns(defi.get_ns(), utils.constants.RETURN_NAME)
            )

        return self.defs[ns]

    def remove(self, ns):
        if not self.get(ns):
            return
            #raise DefinitionError("Definition to be removed not exists")
        self.defs.pop(ns)

    def get(self, ns):
        if ns in self.defs:
            return self.defs[ns]

    def get_defs(self):
        return self.defs

    def handle_function_def(self, parent_ns, fn_name):
        full_ns = utils.join_ns(parent_ns, fn_name)
        #print(full_ns)
        defi = self.get(full_ns)
        if not defi:
            defi = self.create(full_ns, utils.constants.FUN_DEF)
            defi.decorator_names = set()
        #如果函数定义中存在返回值，则创建一个返回值指针，并关联到相应的命名空间。
        return_ns = utils.join_ns(full_ns, utils.constants.RETURN_NAME)
        if not self.get(return_ns):
            self.create(return_ns, utils.constants.NAME_DEF)

        return defi

    def handle_class_def(self, parent_ns, cls_name):
        full_ns = utils.join_ns(parent_ns, cls_name)
        defi = self.get(full_ns)
        if not defi:
            defi = self.create(full_ns, utils.constants.CLS_DEF)

        return defi
    # 计算定义之间的传递闭包。它通过递归计算定义之间的关系，以确定哪些定义依赖于其他定义。结果存储在 closured 字典中。
    def transitive_closure(self):
        closured = {}
        # 定义了一个内部的递归函数 dfs(defi)，它接受一个 defi 参数，表示当前正在处理的定义对象。这个函数负责计算从当前定义节点出发的传递闭包。
        def dfs(defi):
            name_pointer = defi.get_name_pointer()
            new_set = set()
            # bottom
            if closured.get(defi.get_ns(), None) is not None:
                return closured[defi.get_ns()]

            if not name_pointer.get():
                new_set.add(defi.get_ns())

            closured[defi.get_ns()] = new_set

            for name in name_pointer.get():
                if not self.defs.get(name, None):
                    continue
                items = dfs(self.defs[name])
                if not items:
                    items = set([name])
                new_set = new_set.union(items)

            closured[defi.get_ns()] = new_set
            return closured[defi.get_ns()]

        for ns, current_def in self.defs.items():
            if closured.get(current_def, None) is None:
                dfs(current_def)

        return closured
    # 完成定义之间的关系，这是整个工具处理过程中最昂贵的部分。
    # 它通过迭代和更新定义之间的关系来构建完整的定义信息，特别是在处理函数参数和返回值时，以及在处理变量引用时。
    def complete_definitions(self):
        # THE MOST expensive part of this tool's process
        # TODO: IMPROVE COMPLEXITY
        # 用于更新参数的指向关系
        # 参数 pointsto_args 表示当前参数指向的其他参数集合，arg 表示需要更新的参数，name 表示参数所属的定义的命名空间。
        def update_pointsto_args(pointsto_args, arg, name):
            changed_something = False
            # 检查当前迭代的参数是否与需要更新的参数 arg 相同，如果相同，说明不需要进行更新，直接返回 False 表示没有发生变化。
            if arg == pointsto_args:
                return False
            for pointsto_arg in pointsto_args:
                # 检查当前迭代的参数是否存在于 self.defs 字典中，如果不存在，说明该参数不是有效的定义，直接跳过继续下一个参数的处理。
                if not self.defs.get(pointsto_arg, None):
                    continue
                # 检查当前迭代的参数是否与需要更新的参数 arg 的名称相同，如果相同，说明这两个参数实际上是同一个参数，无需更新，直接跳过。
                if pointsto_arg == name:
                    continue
                # 如果当前迭代的参数与 pointsto_args 中的参数相等，说明这两个参数已经指向同一集合，也无需更新，直接跳过。
                pointsto_arg_def = self.defs[pointsto_arg].get_name_pointer()
                if pointsto_arg_def == pointsto_args:
                    continue
                # 如果以上条件都不满足，说明当前迭代的参数需要更新
                # sometimes we may end up with a cycle
                # 首先检查是否可能会导致循环引用，如果会，将 pointsto_arg 从 arg 中移除，以避免循环引用。
                if pointsto_arg in arg:
                    arg.remove(pointsto_arg)
                # 代码开始遍历 arg 中的每个项目，如果项目不在当前迭代的参数的名称指针中，且在 self.defs 中存在，就将 changed_something 设置为 True，表示发生了变化。
                for item in arg:
                    if item not in pointsto_arg_def.get():
                        if self.defs.get(item, None) is not None:
                            changed_something = True
                    # HACK: this check shouldn't be needed
                    # if we remove this the following breaks:
                    # x = lambda x: x + 1
                    # x(1)
                    # since on line 184 we don't discriminate between
                    # literal values and name values
                    if not self.defs.get(item, None):
                        continue
                    pointsto_arg_def.add(item)
            return changed_something

        for i in range(len(self.defs)):
            changed_something = False
            # 遍历了 self.defs 字典中的每个定义
            for ns, current_def in self.defs.items():
                # the name pointer of the definition we're currently iterating
                # 获取当前定义的名称指针 current_name_pointer。
                current_name_pointer = current_def.get_name_pointer()
                # iterate the names the current definition points to items
                # for name in current_name_pointer.get():
                # 遍历当前定义指向的名称指针中的所有名称
                # 这里使用 .copy() 方法是为了在迭代过程中允许修改集合。
                for name in current_name_pointer.get().copy():
                    # get the name pointer of the points to name
                    if not self.defs.get(name, None):
                        continue
                    if name == ns:
                        continue
                    #获取当前名称指针指向的定义的名称指针 pointsto_name_pointer。
                    pointsto_name_pointer = self.defs[name].get_name_pointer()
                    # iterate the arguments of the definition
                    # we're currently iterating
                    # 遍历当前名称指针的参数集合，并检查参数的位置或名称，以确定参数的指向关系。
                    for arg_name, arg in current_name_pointer.get_args().items():
                        pos = current_name_pointer.get_pos_of_name(arg_name)
                        if pos is not None:
                            pointsto_args = pointsto_name_pointer.get_pos_arg(pos)
                            if not pointsto_args:
                                pointsto_name_pointer.add_pos_arg(pos, None, arg)
                                continue
                        else:
                            pointsto_args = pointsto_name_pointer.get_arg(arg_name)
                            if not pointsto_args:
                                pointsto_name_pointer.add_arg(arg_name, arg)
                                continue
                        # 在遍历过程中，调用 update_pointsto_args 函数来更新参数的指向关系，并通过 changed_something 变量标记是否发生了变化。
                        changed_something = changed_something or update_pointsto_args(
                            pointsto_args, arg, current_def.get_ns()
                        )

            if not changed_something:
                break


class Definition(object):
    #FUN_DEF = "FUNCTIONDEF" NAME_DEF = "NAMEDEF" MOD_DEF = "MODULEDEF" CLS_DEF = "CLASSDEF" EXT_DEF = "EXTERNALDEF"
    types = [
        utils.constants.FUN_DEF,
        utils.constants.MOD_DEF,
        utils.constants.NAME_DEF,
        utils.constants.CLS_DEF,
        utils.constants.EXT_DEF,
    ]

    def __init__(self, fullns, def_type):
        self.fullns = fullns
        self.points_to = {"lit": LiteralPointer(), "name": NamePointer()}
        self.def_type = def_type

    def get_type(self):
        return self.def_type

    def is_function_def(self):
        return self.def_type == utils.constants.FUN_DEF

    def is_ext_def(self):
        return self.def_type == utils.constants.EXT_DEF

    def is_callable(self):
        return self.is_function_def() or self.is_ext_def()
    # 获取指向文字的指针
    # 实参指针
    def get_lit_pointer(self):
        return self.points_to["lit"]
    # 获取指向名称的指针
    # 形参指针
    def get_name_pointer(self):
        return self.points_to["name"]

    def get_name(self):
        return self.fullns.split(".")[-1]

    def get_ns(self):
        return self.fullns

    def merge(self, to_merge):
        for name, pointer in to_merge.points_to.items():
            self.points_to[name].merge(pointer)


class DefinitionError(Exception):
    pass
