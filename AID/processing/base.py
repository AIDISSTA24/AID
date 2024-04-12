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
import ast
import os

import utils
from machinery.definitions import Definition


class ProcessingBase(ast.NodeVisitor):
    def __init__(self, filename, modname, modules_analyzed):
        self.modname = modname
        # 用于跟踪已经分析过的模块的集合
        self.modules_analyzed = modules_analyzed
        self.modules_analyzed.add(self.modname)

        self.filename = os.path.abspath(filename)

        with open(filename, "rt", errors="replace") as f:
            self.contents = f.read()
        # 跟踪当前命名空间和方法的栈
        self.name_stack = []
        self.method_stack = []
        self.last_called_names = None

    def get_modules_analyzed(self):
        return self.modules_analyzed

    def merge_modules_analyzed(self, analyzed):
        self.modules_analyzed = self.modules_analyzed.union(analyzed)
    #返回当前的命名空间（通过连接name_stack的元素）
    @property
    def current_ns(self):
        return ".".join(self.name_stack)
    #返回当前的方法名（通过连接method_stack的元素）
    @property
    def current_method(self):
        return ".".join(self.method_stack)

    def visit_Module(self, node):
        #将模块名称和方法名称推入name_stack和method_stack
        self.name_stack.append(self.modname)
        self.method_stack.append(self.modname)
        self.scope_manager.get_scope(self.modname).reset_counters()
        self.generic_visit(node)
        self.method_stack.pop()
        self.name_stack.pop()

    def visit_FunctionDef(self, node):
        self.name_stack.append(node.name)
        self.method_stack.append(node.name)
        if self.scope_manager.get_scope(self.current_ns):
            self.scope_manager.get_scope(self.current_ns).reset_counters()
            for stmt in node.body:
                self.visit(stmt)
        self.method_stack.pop()
        self.name_stack.pop()

    def visit_Lambda(self, node, lambda_name=None):
        lambda_ns = utils.join_ns(self.current_ns, lambda_name)
        # 如果 Lambda 表达式的命名空间还不存在于 scope_manager 中，就创建一个新的作用域，以当前命名空间为父作用域。
        if not self.scope_manager.get_scope(lambda_ns):
            self.scope_manager.create_scope(
                lambda_ns, self.scope_manager.get_scope(self.current_ns)
            )
        self.name_stack.append(lambda_name)
        self.method_stack.append(lambda_name)
        self.visit(node.body)
        self.method_stack.pop()
        self.name_stack.pop()

    def visit_For(self, node):
        for item in node.body:
            self.visit(item)
    #Dict的节点遍历
    def visit_Dict(self, node):
        counter = self.scope_manager.get_scope(self.current_ns).inc_dict_counter()
        dict_name = utils.get_dict_name(counter)

        sc = self.scope_manager.get_scope(utils.join_ns(self.current_ns, dict_name))
        if not sc:
            return
        self.name_stack.append(dict_name)
        sc.reset_counters()
        for key, val in zip(node.keys, node.values):
            if key:
                self.visit(key)
            if val:
                self.visit(val)
        self.name_stack.pop()
    ##List的节点遍历
    def visit_List(self, node):
        counter = self.scope_manager.get_scope(self.current_ns).inc_list_counter()
        list_name = utils.get_list_name(counter)

        sc = self.scope_manager.get_scope(utils.join_ns(self.current_ns, list_name))
        if not sc:
            return
        self.name_stack.append(list_name)
        sc.reset_counters()
        for elt in node.elts:
            self.visit(elt)
        self.name_stack.pop()

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_ClassDef(self, node):
        self.name_stack.append(node.name)
        self.method_stack.append(node.name)
        if self.scope_manager.get_scope(self.current_ns):
            self.scope_manager.get_scope(self.current_ns).reset_counters()
        for stmt in node.body:
            self.visit(stmt)
        self.method_stack.pop()
        self.name_stack.pop()

    def visit_Tuple(self, node):
        for elt in node.elts:
            self.visit(elt)

    def _handle_assign(self, targetns, decoded):
        defi = self.def_manager.get(targetns)
        if not defi:
            defi = self.def_manager.create(targetns, utils.constants.NAME_DEF)

        # check if decoded is iterable 检查 decoded 是否可迭代
        try:
            iter(decoded)
        except TypeError:
            return defi

        for d in decoded:
            if isinstance(d, Definition):
                defi.get_name_pointer().add(d.get_ns())
            else:
                defi.get_lit_pointer().add(d)
        return defi
    # 用于处理 return 语句。接着，构建返回值的命名空间 return_ns，通过连接当前命名空间 (self.current_ns) 和字符串常量 utils.constants.RETURN_NAME 组成。然后，调用 _handle_assign 方法来将返回值与 return_ns 关联起来，以处理返回值的赋值操作。
    def _visit_return(self, node):
        if not node or not node.value:
            return
        # 如果节点 node 存在且具有 value 属性，则调用 self.visit(node.value) 处理返回值。
        self.visit(node.value)
        # x.y.z.<RETURN>
        return_ns = utils.join_ns(self.current_ns, utils.constants.RETURN_NAME)
        #修改逻辑，处理内置函数，保证返回值正确
        decoded = []
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id in utils.constants.BUILDIN_LIST:
            for arg in node.value.args:
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id in utils.constants.BUILDIN_LIST:
                    for argarg in arg.args:
                        decoded.extend(self.decode_node(argarg))
                else:
                    decoded.extend(self.decode_node(arg))
        else:
            decoded = self.decode_node(node.value)
        self._handle_assign(return_ns, decoded)
        #self._handle_assign(return_ns, self.decode_node(node.value))
    # visit_assign的辅助函数，获取目标节点 (target) 对应的命名空间列表。
    def _get_target_ns(self, target):
        if isinstance(target, ast.Name):
            return [utils.join_ns(self.current_ns, target.id)]
        if isinstance(target, ast.Attribute):
            bases = self._retrieve_base_names(target)
            res = []
            for base in bases:
                res.append(utils.join_ns(base, target.attr))
            return res
        if isinstance(target, ast.Subscript):
            return self.retrieve_subscript_names(target)
        return []
    # 调用时就是node.targets和node.value
    def _visit_assign(self, value, targets):
        self.visit(value)
        #修改赋值语句逻辑
        # decoded = self.decode_node(value)
        decoded = []
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in utils.constants.BUILDIN_LIST:
            #print(value.func.id)
            for arg in value.args:
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id in utils.constants.BUILDIN_LIST:
                    for argarg in arg.args:
                        decoded.extend(self.decode_node(argarg))
                else:
                    decoded.extend(self.decode_node(arg))
        else:
            decoded = self.decode_node(value)

        def do_assign(decoded, target):
            self.visit(target)
            #处理解包的情况，为什么不处理List的情况？
            if isinstance(target, ast.Tuple):
                for pos, elt in enumerate(target.elts):
                    if not isinstance(decoded, Definition) and pos < len(decoded):
                        do_assign(decoded[pos], elt)
            else:
                targetns = self._get_target_ns(target)
                for tns in targetns:
                    if not tns:
                        continue
                    defi = self._handle_assign(tns, decoded)
                    splitted = tns.split(".")
                    # 在对应Scope增加Definition对象
                    self.scope_manager.handle_assign(
                        ".".join(splitted[:-1]), splitted[-1], defi
                    )

        for target in targets:
            #print(self.current_ns, ast.dump(value), ast.dump(target))
            do_assign(decoded, target)
    # 解码抽象语法树（AST）节点，
    # 根据不同的 AST 节点类型，尝试提取名称或字面值对应的Definition对象，并将其包装在列表中返回，以便进一步处理。
    def decode_node(self, node):
        # 节点代表一个变量名，它会尝试获取当前命名空间中该名称的Definition对象，并将其包装在一个列表中返回。
        if isinstance(node, ast.Name):
            return [self.scope_manager.get_def(self.current_ns, node.id)]
        # 节点是一个函数调用节点（ast.Call），则进入此条件分支。
        # 它首先递归调用 decode_node 方法来解码函数的名称（node.func）。
        # 然后，它遍历解码后的函数名称，检查每个名称是否是一个函数定义（Definition）。
        # 如果是函数定义，它会构建该函数的返回值命名空间，并尝试获取该返回值的定义，将其添加到返回的列表中。
        elif isinstance(node, ast.Call):
            #  func 是函数，它通常是一个 Name 或 Attribute 对象。
            #if isinstance(node.func, ast.Name):
                #print(node.func.id)
                #if (node.func.id == "bool"):
                    #print(node.args)  
            decoded = self.decode_node(node.func)
            return_defs = []
            for called_def in decoded:
                if not isinstance(called_def, Definition):
                    #print(node.func.id, called_def)
                    continue
                #print(called_def.fullns)
                return_ns = utils.constants.INVALID_NAME
                if called_def.get_type() == utils.constants.FUN_DEF:
                    return_ns = utils.join_ns(
                        called_def.get_ns(), utils.constants.RETURN_NAME
                    )
                elif (
                    called_def.get_type() == utils.constants.CLS_DEF
                    or called_def.get_type() == utils.constants.EXT_DEF
                ):
                    return_ns = called_def.get_ns()
                defi = self.def_manager.get(return_ns)
                if defi:
                    return_defs.append(defi)
            #print("________________")
            return return_defs
        # 如果节点是 Lambda 表达式（ast.Lambda），则进入此条件分支。
        # 它首先获取 Lambda 表达式的计数器和 Lambda 名称，然后尝试获取 Lambda 的定义，并将其包装在列表中返回。
        elif isinstance(node, ast.Lambda):
            lambda_counter = self.scope_manager.get_scope(
                self.current_ns
            ).get_lambda_counter()
            lambda_name = utils.get_lambda_name(lambda_counter)
            return [self.scope_manager.get_def(self.current_ns, lambda_name)]
        # 如果节点是元组（ast.Tuple），则进入此条件分支。
        # 它会遍历元组的元素，并递归调用 decode_node 方法来解码每个元素，并将解码后的结果作为列表返回。
        elif isinstance(node, ast.Tuple):
            decoded = []
            for elt in node.elts:
                decoded.append(self.decode_node(elt))
            return decoded
        # 如果节点是二元操作符表达式（ast.BinOp），则进入此条件分支。
        elif isinstance(node, ast.BinOp):
            decoded_left = self.decode_node(node.left)
            decoded_right = self.decode_node(node.right)
            # return the non definition types if we're talking about a binop
            # since we only care about the type of the return (num, str, etc)
            # 哪个不是Definition对象返回哪个。
            # 因为对于二元操作符表达式，我们通常只关心其返回值的类型，如数字（int、float）、字符串（str）等，而不关心它们是否是定义或变量。
            if not isinstance(decoded_left, Definition):
                return decoded_left
            if not isinstance(decoded_right, Definition):
                return decoded_right
        # 如果节点是属性访问（ast.Attribute），则进入此条件分支。
        # 它会提取属性访问链中的所有名称，并尝试获取每个名称的定义，并将这些定义包装在列表中返回。
        elif isinstance(node, ast.Attribute):
            names = self._retrieve_attribute_names(node)
            defis = []
            for name in names:
                defi = self.def_manager.get(name)
                if defi:
                    defis.append(defi)
            return defis
        elif isinstance(node, ast.Num):
            return [node.n]
        elif isinstance(node, ast.Str):
            return [node.s]
        # 如果节点是文本值或字面值，则将其包装在列表中返回
        #真的有这种节点吗？
        elif self._is_literal(node):
            return [node]
        # 构建对应的字典或列表名称，并尝试获取其定义，将定义包装在列表中返回。
        elif isinstance(node, ast.Dict):
            dict_counter = self.scope_manager.get_scope(
                self.current_ns
            ).get_dict_counter()
            dict_name = utils.get_dict_name(dict_counter)
            scope_def = self.scope_manager.get_def(self.current_ns, dict_name)
            return [scope_def]
        elif isinstance(node, ast.List):
            list_counter = self.scope_manager.get_scope(
                self.current_ns
            ).get_list_counter()
            list_name = utils.get_list_name(list_counter)
            scope_def = self.scope_manager.get_def(self.current_ns, list_name)
            return [scope_def]
        # 节点是下标访问（ast.Subscript），则提取子脚本中的名称，并尝试获取每个名称的定义，并将这些定义包装在列表中返回。
        elif isinstance(node, ast.Subscript):
            names = self.retrieve_subscript_names(node)
            defis = []
            for name in names:
                defi = self.def_manager.get(name)
                if defi:
                    defis.append(defi)
            return defis

        return []
    # 检查给定的 item 是否为字面值（literal），即整数、字符串或浮点数。
    def _is_literal(self, item):
        return isinstance(item, int) or isinstance(item, str) or isinstance(item, float)
    # 从给定的属性访问节点 (node) 中提取父级名称。
    def _retrieve_base_names(self, node):
        if not isinstance(node, ast.Attribute):
            raise Exception("The node is not an attribute")

        if not getattr(self, "closured", None):
            return set()

        decoded = self.decode_node(node.value)
        if not decoded:
            return set()

        names = set()
        for name in decoded:
            if not name or not isinstance(name, Definition):
                continue

            for base in self.closured.get(name.get_ns(), []):
                cls = self.class_manager.get(base)
                if not cls:
                    continue

                for item in cls.get_mro():
                    names.add(item)
        return names
    #从给定的属性访问节点 (node) 中提取全部父级的命名空间。
    #只会在处理解析Attribute节点的Definition时才会调用
    def _retrieve_parent_names(self, node):
        if not isinstance(node, ast.Attribute):
            raise Exception("The node is not an attribute")
        #node.value一般是ast.name节点
        decoded = self.decode_node(node.value)
        if not decoded:
            return set()

        names = set()
        for parent in decoded:
            if not parent or not isinstance(parent, Definition):
                continue
            # 如果存在“closured”属性，意思是处于postprocessor或cgprocessor阶段，则union，
            if getattr(self, "closured", None) and self.closured.get(
                parent.get_ns(), None
            ):
                names = names.union(self.closured.get(parent.get_ns()))
            #不存在“closured”属性，意思是处于preprocessor阶段，则add
            else:
                names.add(parent.get_ns())
        #返回parent的namespace集合
        return names
    #检索属性名，返回属性的命名空间set
    def _retrieve_attribute_names(self, node):
        # 检查对象 self 中是否存在名为 "closured" 的属性，即如果是处于preprocessor阶段，则返回
        if not getattr(self, "closured", None):
            return set()
        # 获取父级节点的命名空间集合
        parent_names = self._retrieve_parent_names(node)
        names = set()
        for parent_name in parent_names:
            #获得父亲节点属性闭包里的Definition的命名空间，然后找出对应的Definition对象
            for name in self.closured.get(parent_name, []):
                defi = self.def_manager.get(name)
                if not defi:
                    continue
                #如果Definition对象是class，
                if defi.get_type() == utils.constants.CLS_DEF:
                    cls_names = self.find_cls_fun_ns(defi.get_ns(), node.attr)
                    if cls_names:
                        names = names.union(cls_names)
                    #print(1)
                    #print("命名空间:", defi.get_ns())
                    #print("需要匹配的方法名:", node.attr)
                    #print(parent_name)
                    #print("输出的方法名:", cls_names)
                    #print("______________________________")
                #如果Definition对象是function或module
                if defi.get_type() in [
                    utils.constants.FUN_DEF,
                    utils.constants.MOD_DEF,
                ]:
                    names.add(utils.join_ns(name, node.attr))
                    #print(2)
                #如果Definition对象是外部Definition
                #？？？？？？？？？？
                if defi.get_type() == utils.constants.EXT_DEF:
                    # HACK: extenral attributes can lead to infinite loops
                    # Identify them here
                    if node.attr in name:
                        continue
                    ext_name = utils.join_ns(name, node.attr)
                    if not self.def_manager.get(ext_name):
                        self.def_manager.create(ext_name, utils.constants.EXT_DEF)
                    names.add(ext_name)
                    #print(3)
        # 返回属性集合
        #print(parent_names)
        #print(names)
        #print("______________________________")
        return names
    # 迭代处理函数调用的参数
    def iterate_call_args(self, defi, node):
        for pos, arg in enumerate(node.args):
            self.visit(arg)
            #这里加逻辑
            decoded = []
            if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id in utils.constants.BUILDIN_LIST:
                for argarg in arg.args:
                    if isinstance(argarg, ast.Call) and isinstance(argarg.func, ast.Name) and argarg.func.id in utils.constants.BUILDIN_LIST:
                        for argargarg in argarg.args:
                            decoded.extend(self.decode_node(argargarg))
                    else:
                        decoded.extend(self.decode_node(argarg))
            else:
                decoded = self.decode_node(arg)
            #decoded = self.decode_node(arg)
            if defi.is_function_def():
                pos_arg_names = defi.get_name_pointer().get_pos_arg(pos)
                # if arguments for this position exist update their namespace
                if not pos_arg_names:
                    continue
                for name in pos_arg_names:
                    arg_def = self.def_manager.get(name)
                    if not arg_def:
                        continue
                    for d in decoded:
                        if isinstance(d, Definition):
                            arg_def.get_name_pointer().add(d.get_ns())
                        else:
                            arg_def.get_lit_pointer().add(d)
            else:
                for d in decoded:
                    if isinstance(d, Definition):
                        defi.get_name_pointer().add_pos_arg(pos, None, d.get_ns())
                    else:
                        defi.get_name_pointer().add_pos_lit_arg(pos, None, d)

        for keyword in node.keywords:
            self.visit(keyword.value)
            decoded = self.decode_node(keyword.value)
            if defi.is_function_def():
                arg_names = defi.get_name_pointer().get_arg(keyword.arg)
                if not arg_names:
                    continue
                for name in arg_names:
                    arg_def = self.def_manager.get(name)
                    if not arg_def:
                        continue
                    for d in decoded:
                        if isinstance(d, Definition):
                            arg_def.get_name_pointer().add(d.get_ns())
                        else:
                            arg_def.get_lit_pointer().add(d)
            else:
                for d in decoded:
                    if isinstance(d, Definition):
                        defi.get_name_pointer().add_arg(keyword.arg, d.get_ns())
                    else:
                        defi.get_name_pointer().add_lit_arg(keyword.arg, d)
    #检索下标名称，返回ast.Subscript节点的命名空间的set
    def retrieve_subscript_names(self, node):
        if not isinstance(node, ast.Subscript):
            raise Exception("The node is not an subcript")
        # preprocessor阶段不执行
        if not getattr(self, "closured", None):
            return set()
        # sl_names为slice的Definition对象
        #如果是int或str，例如x[1]
        #print(node.slice)
        if getattr(node.slice, "value", None) and self._is_literal(node.slice.value):
            sl_names = [node.slice.value]
        #如果是变量，例如x[y]
        else:
            sl_names = self.decode_node(node.slice)
        #val_names为value的Definition对象
        val_names = self.decode_node(node.value)
        #print("value")
        #for i in val_names:
        #    print(i.fullns)
        #print("slice")
        #print(sl_names)
        #print("__________")

        decoded_vals = set()
        keys = set()
        full_names = set()
        # get all names associated with this variable name
        for n in val_names:
            if n and isinstance(n, Definition) and self.closured.get(n.get_ns(), None):
                #为什么是 |=
                decoded_vals |= self.closured.get(n.get_ns())
        for s in sl_names:
            if isinstance(s, Definition) and self.closured.get(s.get_ns(), None):
                # we care about the literals pointed by the name
                # not the namespaces, so retrieve the literals pointed
                #只关心常值参数，不关心变量
                for name in self.closured.get(s.get_ns()):
                    defi = self.def_manager.get(name)
                    if not defi:
                        continue
                    keys |= defi.get_lit_pointer().get()
            elif isinstance(s, str):
                keys.add(s)
            elif isinstance(s, int):
                keys.add(utils.get_int_name(s))

        for d in decoded_vals:
            #在这里修改容器赋值的问题，见11月20日的修改，下面是原来的处理
            #添加一个逻辑，如果分析不出来切片的对象，就保留为value的对象,即
            #这里不确定是否
            # >1还是>=1
            #if len(keys) >= 1:
            for key in keys:
                # check for existence of var name and key combination
                str_key = str(key)
                if isinstance(key, int):
                    str_key = utils.get_int_name(key)
                full_ns = utils.join_ns(d, str_key)
                full_names.add(full_ns)
            #else:
            for i in val_names:
                full_names.add(i.fullns)


        #print(full_names)
        return full_names
    # 检索与ast.call节点 node 相关联的名称set。这些名称通常是函数的返回值、函数本身、或者在函数内部定义的变量名。
    def retrieve_call_names(self, node):
        names = set()
        if isinstance(node.func, ast.Name):
            defi = self.scope_manager.get_def(self.current_ns, node.func.id)
            if defi:
                names = self.closured.get(defi.get_ns(), None)
            #if (names == {'state.Stateful._client.send_request'}):
            #   print(1)           
        elif isinstance(node.func, ast.Call) and self.last_called_names:
            for name in self.last_called_names:
                return_ns = utils.join_ns(name, utils.constants.RETURN_NAME)
                returns = self.closured.get(return_ns)
                if not returns:
                    continue
                for ret in returns:
                    defi = self.def_manager.get(ret)
                    names.add(defi.get_ns())
            #if (names == {'state.Stateful._client.send_request'}):
            #    print(2)
        elif isinstance(node.func, ast.Attribute):
            names = self._retrieve_attribute_names(node.func)
            #if (names == {'state.Stateful._client.send_request'}):
            #   print(3)
            #多重继承问题出在这里
            #print(names)
        elif isinstance(node.func, ast.Subscript):
            # Calls can be performed only on single indices, not ranges
            full_names = self.retrieve_subscript_names(node.func)
            for n in full_names:
                if self.closured.get(n, None):
                    names |= self.closured.get(n)
            #if (names == {'state.Stateful._client.send_request'}):
            #    print(4)
        return names

    def analyze_submodules(self, cls, *args, **kwargs):
        imports = self.import_manager.get_imports(self.modname)

        for imp in imports:
            self.analyze_submodule(cls, imp, *args, **kwargs)
    # 分析子模块
    def analyze_submodule(self, cls, imp, *args, **kwargs):
        if imp in self.get_modules_analyzed():
            return
        # 获取模块 imp 对应的文件路径 fname。
        fname = self.import_manager.get_filepath(imp)

        if (
            not fname
            or not fname.endswith(".py")
            or self.import_manager.get_mod_dir() not in fname
        ):
            return

        self.import_manager.set_current_mod(imp, fname)
        # ???????????????????????????????????????????????????????????
        visitor = cls(fname, imp, *args, **kwargs)
        visitor.analyze()
        self.merge_modules_analyzed(visitor.get_modules_analyzed())

        self.import_manager.set_current_mod(self.modname, self.filename)
    
    # 查找类方法的命名空间set
    # 有两种返回结果，一种是可能是类命名空间？？？，另一种是外部模块的命名空间
    #这个函数导致多重继承出现问题
    def find_cls_fun_ns(self, cls_name, fn):
        
        if cls_name == '..\\SDK_dataset\\switchbot\\devices\\bulb.SwitchbotBulb' and fn == '_send_command':
            #print("yes")
            pass

        cls = self.class_manager.get(cls_name)
        if not cls:
            return set()

        ext_names = set()
        for item in cls.get_mro():
            ns = utils.join_ns(item, fn)
            names = set()
            # 是否具有名为 "closured" 的属性，如果有且属性中存在键 ns
            if getattr(self, "closured", None) and self.closured.get(ns, None):
                names = self.closured[ns]
            else:
                names.add(ns)

            #if cls_name == '..\\SDK_dataset\\switchbot\\devices\\bulb.SwitchbotBulb' and fn == '_send_command':
                #print("yes")

            if self.def_manager.get(ns):
                #if cls_name == '..\\SDK_dataset\\switchbot\\devices\\bulb.SwitchbotBulb' and fn == '_send_command':
                    #print("方法名输出：", ns)
                    #print("______________________________")
                return names
                
            parent = self.def_manager.get(item)
            if parent and parent.get_type() == utils.constants.EXT_DEF:
                ext_names.add(ns)

        for name in ext_names:
            #if name == "base_light.SwitchbotSequenceBaseLight._send_command" or name == "pyunifiprotect.data.base.ProtectMotionDeviceModel.queue_update":
            #    continue
            self.def_manager.create(name, utils.constants.EXT_DEF)
            #print(name)
            self.add_ext_mod_node(name)
        
        #if cls_name == '..\\SDK_dataset\\switchbot\\devices\\bulb.SwitchbotBulb' and fn == '_send_command':
        #    print("______________________________")

        return ext_names
    # 添加外部模块节点。
    def add_ext_mod_node(self, name):
        ext_modname = name.split(".")[0]
        ext_mod = self.module_manager.get(ext_modname)
        if not ext_mod:
            ext_mod = self.module_manager.create(ext_modname, None, external=True)
            ext_mod.add_method(ext_modname)

        ext_mod.add_method(name)
