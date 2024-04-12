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
import copy
import importlib
import os
import sys
from importlib import abc

import utils


def get_custom_loader(ig_obj):
    """
    Closure which returns a custom loader
    that modifies an ImportManager object
    """

    class CustomLoader(abc.SourceLoader):
        def __init__(self, fullname, path):
            self.fullname = fullname
            self.path = path

            ig_obj.create_edge(self.fullname)
            if not ig_obj.get_node(self.fullname):
                ig_obj.create_node(self.fullname)
                ig_obj.set_filepath(self.fullname, self.path)

        def get_filename(self, fullname):
            return self.path

        def get_data(self, filename):
            return ""

    return CustomLoader


class ImportManager(object):
    def __init__(self):
        #存储模块之间的导入关系和文件路径信息的字典
        self.import_graph = dict()
        #用于存储当前模块的名称
        self.current_module = ""
        # 用于存储当前模块的文件路径
        self.input_file = ""
        # 用于存储模块所在的目录路径
        self.mod_dir = None
        #用于存储系统的旧路径钩子和路径信息，以便后续可以还原它们
        self.old_path_hooks = None
        self.old_path = None
    #设置模块所在的包目录路径
    def set_pkg(self, input_pkg):
        self.mod_dir = input_pkg

    def get_mod_dir(self):
        return self.mod_dir

    def get_node(self, name):
        if name in self.import_graph:
            return self.import_graph[name]
    # 创建一个新的模块节点，并将其添加到 import_graph 中
    # 如果给定名称的节点已经存在，将会引发 ImportManagerError 异常
    def create_node(self, name):
        if not name or not isinstance(name, str):
            raise ImportManagerError("Invalid node name")

        if self.get_node(name):
            raise ImportManagerError("Can't create a node a second time")

        self.import_graph[name] = {"filename": "", "imports": set()}
        return self.import_graph[name]
    # 方法用于创建模块之间的导入关系，将当前模块（由 _get_module_path 方法返回）导入到目标模块中
    # 如果当前模块不存在，会引发异常
    def create_edge(self, dest):
        if not dest or not isinstance(dest, str):
            raise ImportManagerError("Invalid node name")

        node = self.get_node(self._get_module_path())
        if not node:
            raise ImportManagerError("Can't add edge to a non existing node")

        node["imports"].add(dest)
    # 用于清除Python的导入缓存，包括 importlib 和 sys 模块的缓存信息
    def _clear_caches(self):
        importlib.invalidate_caches()
        sys.path_importer_cache.clear()
        # TODO: maybe not do that since it empties the whole cache
        for name in self.import_graph:
            if name in sys.modules:
                del sys.modules[name]
    #返回当前模块的路径
    def _get_module_path(self):
        return self.current_module
    #设置当前模块的名称和文件路径
    def set_current_mod(self, name, fname):
        self.current_module = name
        self.input_file = os.path.abspath(fname)
    #根据模块名称获取文件路径信息
    def get_filepath(self, modname):
        if modname in self.import_graph:
            return self.import_graph[modname]["filename"]
    # 设置给定模块节点的文件路径信息
    def set_filepath(self, node_name, filename):
        if not filename or not isinstance(filename, str):
            raise ImportManagerError("Invalid node name")

        node = self.get_node(node_name)
        if not node:
            raise ImportManagerError("Node does not exist")

        node["filename"] = os.path.abspath(filename)

    def get_imports(self, modname):
        if modname not in self.import_graph:
            return []
        return self.import_graph[modname]["imports"]
    #检查当前模块是否为包的 __init__.py 文件
    def _is_init_file(self):
        return self.input_file.endswith("__init__.py")
    #处理相对导入的级别关系，返回模块名称和包名称
    #?????????????
    def _handle_import_level(self, name, level):
        # add a dot for each level
        # 它获取当前模块的包路径并将其按.分割成一个包名的列表。
        # 例如，如果当前模块的包路径是 my_package.subpackage.module，那么package将包含 ['my_package', 'subpackage', 'module']。
        package = self._get_module_path().split(".")
        #检查指定的相对导入级别是否超过了包的深度
        if level > len(package):
            raise ImportError("Attempting import beyond top level package")
        #创建一个字符串，mod_name包含与级别相对应数量的点号 .，然后连接上要导入的模块的名称 name。这是为了构建相对导入的目标模块的名称。
        mod_name = ("." * level) + name
        # When an __init__ file is analyzed,
        # then the module name doesn't contain
        # the __init__ part in it,
        # so special care must be taken for levels.
        #检查当前模块是否是一个 __init__.py 文件，同时检查级别是否大于等于1。
        if self._is_init_file() and level >= 1:
            #如果级别不等于1，则减少级别的值（level -= 1）。这是因为在__init__.py文件内，级别需要减少1，以避免导入父包的模块时出现错误。
            if level != 1:
                level -= 1
                #将包列表中的最后 level 个元素删除，以获取新的包路径。
                package = package[:-level]
        else:
            package = package[:-level]

        return mod_name, ".".join(package)
    #执行模块导入操作
    def _do_import(self, mod_name, package):
        #检查要导入的模块 mod_name 是否已经存在于 Python 的模块缓存 sys.modules 中。
        if mod_name in sys.modules:
            self.create_edge(mod_name)
            return sys.modules[mod_name]
        #使用 importlib.util.find_spec 函数尝试查找要导入的模块的规范（module_spec）。
        # find_spec 函数用于查找模块的信息，如果找到了模块规范，它将包含有关模块的详细信息，否则将引发 ModuleNotFoundError 异常。
        try:
            module_spec = importlib.util.find_spec(mod_name, package=package)
        except ModuleNotFoundError:
            module_spec = None

        # 如果是，说明未找到模块规范，这意味着模块还没有加载，或者在指定的包中找不到。
        if module_spec is None:
            #使用 importlib.import_module 函数动态加载模块。这个函数会加载指定名称的模块，并返回模块对象。
            # package 参数用于指定包名，以便在包内搜索模块。
            return importlib.import_module(mod_name, package=package)
        # 使用 importlib.util.module_from_spec 函数来创建一个模块对象。
        # 这个函数接受一个模块规范对象，并返回一个模块对象，它不会实际加载模块，只是创建一个包含模块信息的对象。
        return importlib.util.module_from_spec(module_spec)
    # 处理模块的导入，包括相对导入
    def handle_import(self, name, level):
        # We currently don't support builtin modules because they're frozen.
        # Add an edge and continue.
        # TODO: identify a way to include frozen modules
        root = name.split(".")[0]
        #如果模块的根名称在 sys.builtin_module_names 中（表示这是Python的内置模块），则创建一个导入关系（边），并继续处理其他导入。
        # 这是因为内置模块通常是“冻结”的，不需要实际导入，但仍然可以记录其存在。
        if root in sys.builtin_module_names:
            self.create_edge(root)
            return

        # Import the module
        try:
            mod_name, package = self._handle_import_level(name, level)
        except ImportError:
            return
        # 计算模块的父模块名称 parent 和父模块的名称 parent_name。
        parent = ".".join(mod_name.split(".")[:-1])
        parent_name = ".".join(name.split(".")[:-1])
        #为什么是这四个？？？？？？？？？？？
        combos = [
            (mod_name, package),
            (parent, package),
            (utils.join_ns(package, name), ""),
            (utils.join_ns(package, parent_name), ""),
        ]

        mod = None
        for mn, pkg in combos:
            try:
                mod = self._do_import(mn, pkg)
                break
            except Exception:
                continue

        if not mod:
            return
        # 方法检查导入的模块是否具有 __file__ 属性，以及该属性是否包含文件路径信息。
        # 如果模块没有文件路径信息，或者文件路径不包含在 self.mod_dir 中（指定的模块目录），则返回 None，表示导入失败。
        if not hasattr(mod, "__file__") or not mod.__file__:
            return
        if self.mod_dir not in mod.__file__:
            return
        fname = mod.__file__
        if fname.endswith("__init__.py"):
            fname = os.path.split(fname)[0]
        # 返回文件的相对路径，该路径是模块相对于 self.mod_dir 的相对路径，即文件在模块目录下的相对位置。
        return utils.to_mod_name(os.path.relpath(fname, self.mod_dir))

    def get_import_graph(self):
        return self.import_graph

    def install_hooks(self):
        loader = get_custom_loader(self)
        self.old_path_hooks = copy.deepcopy(sys.path_hooks)
        self.old_path = copy.deepcopy(sys.path)

        loader_details = loader, importlib.machinery.all_suffixes()
        sys.path_hooks.insert(
            0, importlib.machinery.FileFinder.path_hook(loader_details)
        )
        sys.path.insert(0, os.path.abspath(self.mod_dir))

        self._clear_caches()

    def remove_hooks(self):
        sys.path_hooks = self.old_path_hooks
        sys.path = self.old_path

        self._clear_caches()


class ImportManagerError(Exception):
    pass
