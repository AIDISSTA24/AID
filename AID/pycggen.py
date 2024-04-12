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

import utils
from machinery.callgraph import CallGraph
from machinery.classes import ClassManager
from machinery.definitions import DefinitionManager
from machinery.imports import ImportManager
from machinery.key_err import KeyErrors
from machinery.modules import ModuleManager
from machinery.scopes import ScopeManager
from processing.cgprocessor import CallGraphProcessor
from processing.keyerrprocessor import KeyErrProcessor
from processing.postprocessor import PostProcessor
from processing.preprocessor import PreProcessor

from inference.type import TypeInference
from data.dataflow import Dataflow
from data.parameter import ParameterExtraction


class CallGraphGenerator(object):
    def __init__(self, entry_points, package, max_iter, operation):
        self.entry_points = entry_points
        self.package = package
        self.state = None
        self.max_iter = 10
        self.operation = operation
        self.setUp()
    #初始化各种管理器和调用图对象
    def setUp(self):
        self.import_manager = ImportManager()
        self.scope_manager = ScopeManager()
        self.def_manager = DefinitionManager()
        self.class_manager = ClassManager()
        self.module_manager = ModuleManager()
        self.cg = CallGraph()
        self.key_errs = KeyErrors()
    #从各种管理器中提取当前的状态信息，包括定义、作用域和类信息。返回一个包含这些信息的字典
    def extract_state(self):
        state = {}
        state["defs"] = {}
        for key, defi in self.def_manager.get_defs().items():
            state["defs"][key] = {
                "names": defi.get_name_pointer().get().copy(),
                "lit": defi.get_lit_pointer().get().copy(),
            }

        state["scopes"] = {}
        for key, scope in self.scope_manager.get_scopes().items():
            state["scopes"][key] = set(
                [x.get_ns() for (_, x) in scope.get_defs().items()]
            )

        state["classes"] = {}
        for key, ch in self.class_manager.get_classes().items():
            state["classes"][key] = ch.get_mro().copy()
        return state
    #重置管理器中的计数器，通常在每次迭代之后调用
    def reset_counters(self):
        for key, scope in self.scope_manager.get_scopes().items():
            scope.reset_counters()
    #检查当前状态是否已经收敛，如果各种信息都没有变化，则认为已经收敛
    def has_converged(self):
        if not self.state:
            return False

        curr_state = self.extract_state()
        
        # check defs
        for key, defi in curr_state["defs"].items():
            if key not in self.state["defs"]:
                return False
            if defi["names"] != self.state["defs"][key]["names"]:
                return False
            if defi["lit"] != self.state["defs"][key]["lit"]:
                return False

        # check scopes
        for key, scope in curr_state["scopes"].items():
            if key not in self.state["scopes"]:
                return False
            if scope != self.state["scopes"][key]:
                return False

        # check classes
        for key, ch in curr_state["classes"].items():
            if key not in self.state["classes"]:
                return False
            if ch != self.state["classes"][key]:
                return False

        return True
    #移除导入钩子，用于清理在分析过程中安装的import钩子。
    def remove_import_hooks(self):
        self.import_manager.remove_hooks()
    #在处理结束后执行清理工作，包括移除导入钩子等。
    def tearDown(self):
        self.remove_import_hooks()
    #根据入口点和包路径获取模块名称。
    def _get_mod_name(self, entry, pkg):
        # We do this because we want __init__ modules to
        # only contain the parent module
        # since pycg can't differentiate between functions
        # coming from __init__ files.

        input_mod = utils.to_mod_name(os.path.relpath(entry, pkg))
        #如果入口点指向__init__.py文件，则会将其剔除。
        #！！！！！！！！！！！！！！！！！！！！！！！！！！！！这里可能会有问题
        #if input_mod.endswith("__init__"):
        #    input_mod = ".".join(input_mod.split(".")[:-1])

        return input_mod
    #执行一次处理过程，可以是前处理、后处理、调用图处理或键错误处理。
    def do_pass(self, cls, install_hooks=False, *args, **kwargs):
        #cls：要执行的处理类。
        #install_hooks：是否安装导入钩子。

        #创建一个空集合modules_analyzed，用于跟踪已经分析过的模块。
        modules_analyzed = set()
        #对于每个给定的入口点（entry_point）：
        #获取入口点所在的包路径（input_pkg）和模块名（input_mod）
        #获取入口点的绝对文件路径（input_file）。
        for entry_point in self.entry_points:
            input_pkg = self.package
            input_mod = self._get_mod_name(entry_point, input_pkg)
            input_file = os.path.abspath(entry_point)
            #如果没有找到模块名，则继续处理下一个入口点。
            if not input_mod:
                continue

            if not input_pkg:
                input_pkg = os.path.dirname(input_file)

            if input_mod not in modules_analyzed:
                if install_hooks:
                    self.import_manager.set_pkg(input_pkg)
                    self.import_manager.install_hooks()

                processor = cls(
                    input_file,
                    input_mod,
                    modules_analyzed=modules_analyzed,
                    *args,
                    **kwargs,
                )
                processor.analyze()
                #更新已分析模块的集合（modules_analyzed），以包含当前处理过程中分析的模块。
                modules_analyzed = modules_analyzed.union(
                    processor.get_modules_analyzed()
                )

                if install_hooks:
                    self.remove_import_hooks()

    def do_pass_attribute_matching_to_class(self, cls, install_hooks=False, *args, **kwargs):
        #cls：要执行的处理类。
        #install_hooks：是否安装导入钩子。

        #创建一个空集合modules_analyzed，用于跟踪已经分析过的模块。
        modules_analyzed = set()
        #对于每个给定的入口点（entry_point）：
        #获取入口点所在的包路径（input_pkg）和模块名（input_mod）
        #获取入口点的绝对文件路径（input_file）。
        for entry_point in self.entry_points:
            input_pkg = self.package
            input_mod = self._get_mod_name(entry_point, input_pkg)
            input_file = os.path.abspath(entry_point)
            #如果没有找到模块名，则继续处理下一个入口点。
            if not input_mod:
                continue

            if not input_pkg:
                input_pkg = os.path.dirname(input_file)

            if input_mod not in modules_analyzed:
                if install_hooks:
                    self.import_manager.set_pkg(input_pkg)
                    self.import_manager.install_hooks()

                processor = cls(
                    input_file,
                    input_mod,
                    modules_analyzed=modules_analyzed,
                    *args,
                    **kwargs,
                )
                processor.analyze()
                #更新已分析模块的集合（modules_analyzed），以包含当前处理过程中分析的模块。
                modules_analyzed = modules_analyzed.union(
                    processor.get_modules_analyzed()
                )

                if install_hooks:
                    self.remove_import_hooks()

    def analyze(self):
        #预处理阶段
        self.do_pass(
            PreProcessor,
            True,
            self.import_manager,
            self.scope_manager,
            self.def_manager,
            self.class_manager,
            self.module_manager,
        )
        self.def_manager.complete_definitions()

        #print(self.def_manager.get("base_light.SwitchbotSequenceBaseLight._send_command"))
        #for i in self.def_manager.defs:
        #    print(i)

        print("预处理完成")
        print("____________________________________")
        print("____________________________________")
        print("____________________________________")
        #预处理结束后提取属性
        parameterExtraction = ParameterExtraction(self.class_manager, self.scope_manager, self.def_manager)
        parameterExtraction.get_parameter()


        #使用一个循环来执行迭代处理，直到满足停止迭代的条件（最大迭代次数已达到或状态收敛为止）
        iter_cnt = 0
        while (self.max_iter < 0 or iter_cnt < self.max_iter) and (
            #检查状态是否收敛
            not self.has_converged()
        ):
            self.state = self.extract_state()
            self.reset_counters()
            #执行后处理（PostProcessor）
            self.do_pass(
                PostProcessor,
                False,
                self.import_manager,
                self.scope_manager,
                self.def_manager,
                self.class_manager,
                self.module_manager,
            )

            '''if iter_cnt == 0:
                for ns, defi in self.def_manager.defs.items():
                    #if defi.get_type() == utils.constants.FUN_DEF and "_send_command" in ns:
                    if defi.get_type() == utils.constants.FUN_DEF:
                        print("函数定义", defi.fullns)
                print("____________________________________")
                print("____________________________________")
                print("____________________________________")
                for ns, defi in self.def_manager.defs.items():
                    #if defi.get_type() == utils.constants.EXT_DEF and "SwitchbotSequenceBaseLight" in ns:
                    if defi.get_type() == utils.constants.EXT_DEF:
                        print("外部调用定义", defi.fullns)
                print("____________________________________")
                for ns, defi in self.def_manager.defs.items():
                    #if defi.get_type() == utils.constants.CLS_DEF and "SwitchbotSequenceBaseLight" in ns:
                    if defi.get_type() == utils.constants.CLS_DEF:
                        print("类定义", defi.fullns)
                print("____________________________________")'''
                #for ns1, defi1 in self.def_manager.defs.items():
                #    if defi1.get_type() == utils.constants.EXT_DEF:
                #        for ns2, defi2 in self.def_manager.defs.items():
                #            if defi2.get_type() == utils.constants.FUN_DEF and utils.equal_attribute(ns1, ns2):
                #                print(ns1, ns2)

            if iter_cnt in [0]:
                ns_to_be_remove = set()
                for ns1, defi1 in self.def_manager.defs.items():
                    if defi1.get_type() == utils.constants.EXT_DEF and '.' in ns1:
                        #remove_flag = False
                        ext_class = ns1.rsplit('.', 1)[0]
                        ext_method = ns1.split('.')[-1]
                        for ns2, defi2 in self.def_manager.defs.items():
                            if defi2.get_type() == utils.constants.CLS_DEF and utils.equal_attribute(ext_class, ns2):
                                #这表示ns1的Definition是有内部定义的，这就可以考虑进行删除了
                                #print(ns1, ext_class, ns2, ext_method)
                                if ns2 + '.' + ext_method in self.def_manager.defs:
                                    #print(ns2 + '.' + ext_method)
                                    #print("该方法存在")
                                    pass
                                else:
                                    #print(ns2 + '.' + ext_method)
                                    #print("该方法不存在")
                                    ns_to_be_remove.add(ns1)
                                    #self.def_manager.remove(ns1)
                                #for ns3, defi3 in self.def_manager.defs.items():
                                #    if defi3.get_type() == utils.constants.FUN_DEF and ns2 in ns3:
                for ns in ns_to_be_remove:
                    self.def_manager.remove(ns)  
                    #print("删除了：", ns)                 



            '''if iter_cnt == 0:
                print(self.def_manager.get("base_light.SwitchbotSequenceBaseLight._send_command"))
                self.def_manager.remove("base_light.SwitchbotSequenceBaseLight._send_command")
                print(self.def_manager.get("base_light.SwitchbotSequenceBaseLight._send_command"))'''

            self.def_manager.complete_definitions()
            iter_cnt += 1

            print(iter_cnt, "后处理完成")
            print("____________________________________")
            print("____________________________________")
            print("____________________________________")

        self.reset_counters()

        print("后处理完成")
        print("____________________________________")
        print("____________________________________")
        print("____________________________________")

        #in_modules = self.module_manager.get_internal_modules
        #for in_module in in_modules:
        #    print(in_module)

        '''scope = self.scope_manager.get_scope('examples\\abode2\\devices\\light.Light.set_color_temp')
        print(scope.fullns)
        defi = scope.defs.get('response')
        print(defi.fullns)
        point = defi.points_to.get('name')
        print(point)
        val = point.values
        val.discard('state.Stateful._client.send_request')
        val.add('examples\\abode2\\client.Client.send_request')



        def2 = self.def_manager.defs['examples\\abode2\\devices\\light.Light.set_color_temp.response']
        print(def2.fullns)
        point2 = defi.points_to.get('name')
        print(point2)
        val2 = point.values
        val2.discard('state.Stateful._client.send_request')
        val2.add('examples\\abode2\\client.Client.send_request')'''

        #self.scope_manager.get_scope('examples\\abode2\\devices\\light.Light.set_color_temp').defs.get('response').points_to.get('name').values.discard('state.Stateful._client.send_request')
        #self.scope_manager.get_scope('examples\\abode2\\devices\\light.Light.set_color_temp').defs.get('response').points_to.get('name').values.add('examples\\abode2\\client.Client.send_request')

        #valSet = defi.points_to.get('name').values
        #for val in valSet:
            #print(val)
        #defi.points_to.get('name').

        typeInfer = TypeInference(self.class_manager, self.scope_manager, self.def_manager)
        #把下面这句注释掉，即可关闭类型推断功能
        typeInfer.generate()
        #attribute_matching_to_class = dict()
        attribute_matching_to_class = typeInfer._attribute_matching_to_class
        methods = typeInfer._methods_with_no_path
        attributes = typeInfer._attributes_with_no_path

        dataflow = Dataflow(self.class_manager, self.scope_manager, self.def_manager)
        #把下面这三句注释掉，即可关闭数据依赖功能
        dataflow.get_all_methods()
        dataflow.get_assign()
        dataflow.get_return()

        #self._assign_information = dataflow._assign_information
        #self._return_information = dataflow._return_information
        self.cg.add_dataflow_info(dataflow._methods, dataflow._assign_information, 
                                  dataflow._return_information, parameterExtraction._parameters)

        #改一个新的do_pass，加上typeInfer
        if self.operation == utils.constants.CALL_GRAPH_OP:
            self.do_pass_attribute_matching_to_class(
                CallGraphProcessor,
                False,
                self.import_manager,
                self.scope_manager,
                self.def_manager,
                self.class_manager,
                self.module_manager,
                attribute_matching_to_class,
                methods,
                attributes,
                call_graph=self.cg,
            )
        elif self.operation == utils.constants.KEY_ERR_OP:
            self.do_pass(
                KeyErrProcessor,
                False,
                self.import_manager,
                self.scope_manager,
                self.def_manager,
                self.class_manager,
                self.key_errs,
            )
        else:
            raise Exception("Invalid operation: " + self.operation)

    def output(self):

        self.cg.generate_datacg()

        return self.cg.get()

    def output_key_errs(self):
        return self.key_errs.get()

    # Redefined in line 227
    # def output_edges(self):
    #     return self.key_errors

    def output_edges(self):
        return self.cg.get_edges()
    #生成内部和外部模块的信息。返回包含模块信息的字典。
    def _generate_mods(self, mods):
        #mods：要生成信息的模块集合。
        res = {}
        for mod, node in mods.items():
            res[mod] = {
                "filename": (
                    os.path.relpath(node.get_filename(), self.package)
                    if node.get_filename()
                    else None
                ),
                "methods": node.get_methods(),
            }
        return res
    #获取内部模块信息
    def output_internal_mods(self):
        return self._generate_mods(self.module_manager.get_internal_modules())
    #获取外部模块信息
    def output_external_mods(self):
        return self._generate_mods(self.module_manager.get_external_modules())

    def output_functions(self):
        functions = []
        for ns, defi in self.def_manager.get_defs().items():
            if defi.is_function_def():
                functions.append(ns)
        return functions

    def output_classes(self):
        classes = {}
        for cls, node in self.class_manager.get_classes().items():
            classes[cls] = {"mro": node.get_mro(), "module": node.get_module()}
        return classes

    def get_as_graph(self):
        return self.def_manager.get_defs().items()
