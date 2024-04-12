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

class CallGraph(object):
    def __init__(self):
        self.cg = {}
        self.modnames = {}

        self._return_information = {}
        self._assign_information = {}

        self.datacg = {}
        self.enhancedcg = {}

    def add_dataflow_info(self, methods_info, assign_info, return_info, parameter_info):       
        
        #self._methods = set()
        self._methods = methods_info
        self._assign_information = assign_info
        self._return_information = return_info
        #(parameter, method)
        self._parameter_information = parameter_info

        #for v in methods_info:
        #    self._methods.add(v.split("\\")[-1])
            

    def add_node(self, name, modname=""):
        if not isinstance(name, str):
            raise CallGraphError("Only string node names allowed")
        if not name:
            raise CallGraphError("Empty node name")

        if name not in self.cg:
            self.cg[name] = set()
            self.modnames[name] = modname

        if name in self.cg and not self.modnames[name]:
            self.modnames[name] = modname

    def add_edge(self, src, dest):
        self.add_node(src)
        self.add_node(dest)
        self.cg[src].add(dest)

    def get(self):

        '''print("全部的方法名")
        for i in self._methods:
            print(i)
        print("_______________________")'''
        
        '''print("赋值和参数依赖：")
        for k,v in self._assign_information.items():
            print(k,v)
        print("_______________________")'''

        '''print("返回值依赖：")
        for k,v in self._return_information.items():
            print(k,v)
        print("_______________________")'''

        #映射的例子
        #examples\miio\integrations\yeelight\light\yeelight.YeelightStatus.__init__.data #examples\miio\integrations\yeelight\light\yeelight.YeelightStatus.__init__
        '''print("参数映射")
        for k,v in self._parameter_information.items():
            print(k,v)
        print("_______________________")'''


        #return self.cg
        return self.enhancedcg

    def get_edges(self):
        output = []
        for src in self.cg:
            for dst in self.cg[src]:
                output.append([src, dst])
        return output

    def get_modules(self):
        return self.modnames
    

    def generate_datacg(self):
        #print("开始生成数据流图：")
        for key, value in self._assign_information.items():
            #if key.split("\\")[-1] in self._methods:
            if utils.common.is_method_node(key, self._methods):
                #print(key)
                visited = set()
                queue = [key]
                while queue:
                    current_node = queue.pop(0)
                    if current_node not in visited:
                        visited.add(current_node)
                        #print(current_node)
                        #print("_______________________")
                        
                            #if (current_node.split("\\")[-1] in self._methods or (current_node in self._parameter_information and self._parameter_information[current_node].split("\\")[-1] in self._methods)) and current_node != key:
                            #逻辑：首先判断当前节点是否是方法节点，即是否在self._methods里
                            #if current_node.split("\\")[-1] in self._methods and current_node != key:
                        #if "device.Device.get_properties" in key:
                        #    print("current_node: " + current_node)
                        if utils.common.is_method_node(current_node, self._methods) and current_node != key:
                            #if "device.Device.get_properties" in key:
                            #print(key + " 与 " + current_node + " 相连")
                            if current_node not in self.datacg:
                                self.datacg[current_node] = set()
                            self.datacg[current_node].add(key)
                        elif current_node in self._parameter_information and current_node != key:
                            #if "device.Device.get_properties" in key:
                            #print(key + " 与 " + self._parameter_information[current_node] + " 相连")
                            if self._parameter_information[current_node] not in self.datacg:
                                self.datacg[self._parameter_information[current_node]] = set()
                            self.datacg[self._parameter_information[current_node]].add(key)
                        else:
                            #if "device.Device.get_properties" in key:
                            #    print(self._assign_information.get(current_node, []))
                            queue.extend(self._assign_information.get(current_node, []))
                            #if "device.Device.get_properties" in key:
                            #    print(self._return_information.get(current_node, []))
                            queue.extend(self._return_information.get(current_node, []))
        #print("_______________________")
        #print("_______________________")
        for key, value in self._return_information.items():
            #if key.split("\\")[-1] in self._methods:
            if utils.common.is_method_node(key, self._methods):
                #print(key)
                visited = set()
                queue = [key]
                while queue:
                    current_node = queue.pop(0)
                    if current_node not in visited:
                        visited.add(current_node)
                        #print(current_node)
                        #print("_______________________")
                        #if (current_node.split("\\")[-1] in self._methods or (current_node in self._parameter_information and self._parameter_information[current_node].split("\\")[-1] in self._methods)) and current_node != key:
                        #if current_node.split("\\")[-1] in self._methods and current_node != key:
                        if utils.common.is_method_node(current_node, self._methods) and current_node != key:
                            #if "device.Device.get_properties" in key:
                            #print(key + " 与 " + current_node + " 相连")
                            if current_node not in self.datacg:
                                self.datacg[current_node] = set()
                            self.datacg[current_node].add(key)
                        elif current_node in self._parameter_information and current_node != key:
                            #if "device.Device.get_properties" in key:
                            #print(key + " 与 " + self._parameter_information[current_node] + " 相连")
                            if self._parameter_information[current_node] not in self.datacg:
                                self.datacg[self._parameter_information[current_node]] = set()
                            self.datacg[self._parameter_information[current_node]].add(key)
                        else:
                            queue.extend(self._assign_information.get(current_node, []))
                            queue.extend(self._return_information.get(current_node, []))
        #print("_______________________")

        '''for k,v in self.datacg.items():
            print(k,v)
        print("_______________________")
        for k,v in self.cg.items():
            print(k,v)
        print("_______________________")'''

        for key in self.cg.keys() | self.datacg.keys():
            self.enhancedcg[key] = self.cg.get(key, set()) | self.datacg.get(key, set())

        '''for k,v in self.enhancedcg.items():
            print(k,v)
        print("_______________________")'''



        #在这里进行一部同步的操作，就是将路径不一致的改为一致的
        #例如miio.device.Device.get_properties和examples\\miio\\device.Device.get_properties
        #将miio.device.Device.get_properties改为examples\\miio\\device.Device.get_properties
        all_nodes = set()
        for k,v in self.enhancedcg.items():
            all_nodes.add(k)
            all_nodes.union(v)
        #print("_______________________")
        #print("全部节点：")
        #print(all_nodes)
        #key为miio.device.Device.get_properties，value为examples\\miio\\device.Device.get_properties
        equal_dict = dict()
        for n1 in all_nodes:
            for n2 in all_nodes:
                if n1 != n2 and ('.' in n1 and '.' in n2) and ('\\' in n1 or '\\' in n2):
                    v1 = n1.replace('\\', '.')
                    v2 = n2.replace('\\', '.')
                    if v1 != v2 and v1 in v2 and v2.split(v1)[-1] == '':
                        equal_dict[n1] = n2
                    elif v1 != v2 and v2 in v1 and v1.split(v2)[-1] == '':
                        equal_dict[n2] = n1
        #print("全部节点的映射关系：")
        #print(equal_dict)
        #for k,v in equal_dict.items():
            #print(k, v)

        #print("_______________________")

        #这里是把value的名字统一,就是将边的名字都变为带路径的
        for value in self.enhancedcg.values():
            for key in equal_dict.keys():
                if key in value:
                    value.remove(key)
                    value.add(equal_dict[key])

        #把多余的key删掉，就是将不带路径的节点给删掉，前提是与带路径的节点的边一致
        for k,v in equal_dict.items():
            if k in self.enhancedcg.keys() and v in self.enhancedcg.keys() and self.enhancedcg[k] == self.enhancedcg[v]:
                #print(k, v)
                self.enhancedcg.pop(k)
        #print("_______________________")    
    

        #start = "examples\\miio\\integrations\\yeelight\\light\\yeelight.YeelightStatus.moonlight_mode"
        start = "..\\SDK_dataset\\pymystrom\\bulb.MyStromBulb.set_color_hsv"
        end = "socket.socket"
        #判断是否存在连通路径
        #self.judge_connection(start, end)

        reverse_cg = self.reverse_graph(self.enhancedcg)
        #全部的root节点
        temp = self.api_identification(reverse_cg, end)
        print(len(temp))   
        result1 = set([x for x in temp if "\\" in x and "._" not in x])
        print(len(result1))
        #for k,v in self.reverse_graph(self.enhancedcg).items():
        #    print(k,v)
             
        result2 = self.get_result2(self.enhancedcg, reverse_cg, result1)



        #还是得再加几个规则，不
        print("第一个启发式规则的输出: 总数" + str(len(result1)))
        for i in result1:
            print(i)

        print("第二启发式规则的输出: 总数" + str(len(result2)))
        for i in result2:
            print(i)


    #def cg_combine(self):
    #    for key in self.cg.keys():
    #        #merged_dict[key] = dict1.get(key, set()) | dict2.get(key, set())
    #        self.enhancedcg[key] = self.cg.get(key, set()) | self.datacg.get(key, set())

    def judge_connection(self, start, end, visited=None, path=None):

        if visited is None:
            visited = set()
        if path is None:
            path = []

        visited.add(start)
        path = path + [start]

        def is_equal(v1: str, v2: str):
            if v1 == v2:
                return True
            v1 = v1.replace('\\', '.')
            v2 = v2.replace('\\', '.')
            if v1 in v2 and v2.split(v1)[-1] == '':
                return True
            elif v2 in v1 and v1.split(v2)[-1] == '':
                return True
            else:
                return False

        if start == end:
            print("连通")
            print("节点之间的路径为:", path)
            return True

        for neighbor in self.enhancedcg.get(start, []):
            if neighbor not in visited:
                if self.judge_connection(neighbor, end, visited, path):
                    return True

        return False
    
    def reverse_graph(self, graph):
        reverse = {}
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                if neighbor not in reverse:
                    reverse[neighbor] = []
                reverse[neighbor].append(node)
        return reverse

    def api_identification(self, call_graph, node):
        source_nodes = []
    
        # 使用DFS进行遍历
        def dfs(current_node, visited):
            visited.add(current_node)
            if current_node not in call_graph:
                source_nodes.append(current_node)
                return
            for next_node in call_graph[current_node]:
                if next_node not in visited:
                    dfs(next_node, visited)
        
        dfs(node, set())
        #print("所有的根节点：")
        #for i in source_nodes:
        #     print(i)
        return source_nodes
    
    #核心思路是找被根节点调用，且被调用关系只为1的节点
    def get_result2(self, call_graph, reverse_cg, result1):
        result2 = []
        for root_node in result1:
            #print("根节点:")
            #print(root_node)
            #print("该根节点下的所有子节点:")
            #print(call_graph[root_node])
            for child_node in call_graph[root_node]:
                #print("孩子节点:")
                #print(child_node)
                #print("该孩子节点的所有父节点:")
                #print(reverse_cg[child_node])
                #print(len(reverse_cg[child_node]))
                if len(reverse_cg[child_node]) == 1 and "\\" in child_node and "._" not in child_node and "<" not in child_node:
                #if len(reverse_cg[child_node]) == 1 and reverse_cg[child_node][0] not in result1:
                    result2.append(child_node)
        
        return result2
    
        

class CallGraphError(Exception):
    pass
