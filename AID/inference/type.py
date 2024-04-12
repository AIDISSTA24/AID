from machinery.classes import ClassManager,ClassNode
from machinery.scopes import ScopeManager,ScopeItem
from machinery.definitions import DefinitionManager,Definition


class TypeInference:

    def __init__(self, class_manager: ClassManager, scope_manager: ScopeManager, definition_manager: DefinitionManager) -> None:

        #dict(ns, ClassNode)
        self._all_classes = class_manager.get_classes() 
        #dict(ns, ScopeItem)
        self._all_scopes = scope_manager.get_scopes()
        #dict(ns, Definition)
        self._all_definitions = definition_manager.get_defs()

        #记录不同属性都调用过哪些方法
        #例如examples\abode2\state.Stateful._client调用了{'send_request', 'default_mode'}
        #例如examples\abode2\state.Stateful._state调用了{'get'}
        self._called_methods = dict()

        #记录不同属性匹配到的类的类型
        #例如examples\abode2\state.Stateful._client对应client.Client
        self._attribute_matching_to_class = dict()

        self._methods = dict()
        self._attributes = dict()
        self._methods_with_no_path = dict()
        self._attributes_with_no_path = dict()
    

    def get_all_methods_and_attributes(self):
            
        methods_and_attributes = dict()
        methods = dict()
        attributes = dict()
        
        #('examples\\abode2\\state.Stateful' , ClassNode)
        for class_key, classNode in self._all_classes.items():
            #('examples\\abode2\\state.Stateful.update' , ScopeItem)
            for scope_key, scopeItem in self._all_scopes.items():
                #二者一致的话，ScopeItem下的所有Definition既包含方法，也包含类的属性
                if class_key == scope_key:
                    temp = set()
                    defs: dict = scopeItem.defs
                    #defi: Definition
                    for name, defi in defs.items():
                        temp.add(defi.fullns)                    
                    methods_and_attributes[class_key] = temp
                #ScopeItem的名称包含的情况，那么ScopeItem的名称就是方法的namespace
                # <的意思是防止出现类似<dict1>这种情况
                #scope_key.split(class_key)[1][0] == '.': 是保证不会出现重名的情况
                #class_key.count('.') + 1 == scope_key.count('.')是保证只会多一个.
                elif class_key in scope_key and class_key != scope_key and '<' not in scope_key and class_key.count('.') + 1 == scope_key.count('.'): 
                    if class_key not in methods:
                        methods[class_key] = set()
                        methods[class_key].add(scope_key)
                    else:
                        methods[class_key].add(scope_key)
                        #methods_with_no_path[class_key].add(scope_key.split('.')[-1])
                    #if class_key == 'examples\\abode2\\state.Stateful':
                    #    print(methods[class_key])

        '''print("methods_and_attributes:")
        for k,v in methods_and_attributes.items():
            print(k,v)
        print("__________________________________________")
        print("methods:")
        for k,v in methods.items():
            print(k,v)
        print("__________________________________________")'''



        for class_name,set1 in methods_and_attributes.items():
            if class_name in methods:
                set2 = methods[class_name]
                set3 = set1 - set2
                attributes[class_name] = set3

        self._methods = methods
        self._attributes = attributes

        for key,sets in methods.items():
            #加这个的逻辑是因为有存在路径和没有路径两种Definition，为了保证推断的时候不重复，直接删掉没有的那一种
            #session.HiveSession.updateTokens
            #..\SDK_dataset\apyhiveapi\session.HiveSession.updateTokens
            if '\\' in key:
                temp = set()
                for v in sets:
                    temp.add(v.split('.')[-1])
                if temp:
                    self._methods_with_no_path[key] = temp
        
        for key,sets in attributes.items():
            if '\\' in key:
                temp = set()
                for v in sets:
                    temp.add(v.split('.')[-1])
                if temp:
                    self._attributes_with_no_path[key] = temp


        #print("self._methods:", self._methods_with_no_path)
        '''print("self._methods:")
        for k,v in self._methods_with_no_path.items():
            print(k,v)
        print("__________________________________________")'''
        #print("self._attributes:", self._attributes)
        #print("self._attributes:", self._attributes_with_no_path)
        '''print("self._attributes:")
        for k,v in self._attributes_with_no_path.items():
            print(k,v)
        print("__________________________________________")'''



        #print(methods_and_attributes['examples\\abode2\\state.Stateful'])
        #print(self._methods['examples\\abode2\\state.Stateful'])
        #print(self._attributes['examples\\abode2\\state.Stateful'])
        #print("_______________________________")

        #{'examples\\abode2\\state.Stateful.refresh', 'examples\\abode2\\state.Stateful._client', 'examples\\abode2\\state.Stateful._state', 'examples\\abode2\\state.Stateful.update', 'examples\\abode2\\state.Stateful._validate', 'examples\\abode2\\state.Stateful.desc', 'examples\\abode2\\state.Stateful.__getattr__', 'examples\\abode2\\state.Stateful.__init__'}
        #{'examples\\abode2\\state.Stateful.refresh', 'examples\\abode2\\state.Stateful.update', 'examples\\abode2\\state.Stateful._validate', 'examples\\abode2\\state.Stateful.desc', 'examples\\abode2\\state.Stateful.__getattr__', 'examples\\abode2\\state.Stateful.__init__'}
        #{'examples\\abode2\\state.Stateful._client', 'examples\\abode2\\state.Stateful._state'}


        #注意问题！！！！！！！！！！！！！！！！！！！！！！！
        #把路径全都删掉，否则可能会出现不匹配

    def collect_called_methods(self):
        
        called_methods = dict()
        #'examples\\abode2\\state.Stateful'
        #{'examples\\abode2\\state.Stateful._client', 'examples\\abode2\\state.Stateful._state'}
        for class_key, attributes_set in self._attributes.items():
            #if class_key == 'examples\\abode2\\state.Stateful':
            #{'examples\\abode2\\state.Stateful._client'
            for attribute in attributes_set:
                #print("attribute:" + attribute)
                #state.Stateful._client'
                attribute_no_path = attribute.split("\\")[-1]
                #print("attribute_no_path:" + attribute_no_path)
                for defi_key, Definition in self._all_definitions.items():
                    values_set = Definition.points_to['name'].values
                    #print(values_set)
                    #value: state.Stateful._client.send_request或state.Stateful._client.send_request.json
                    for value in values_set:
                        #这里可能有问题
                        #if attribute_no_path in value and attribute_no_path != value and attribute != value:
                        if attribute_no_path in value and attribute != value:
                        #if attribute_no_path in value:
                            #print("value:" + value)
                            #print("attribute_no_path:" + attribute_no_path)
                            #if value.split(attribute_no_path)[-1] != '':
                            called_method = value.split(attribute_no_path + '.')[-1].split(".")[0]
                            #print("called_method:" + called_method)
                            if attribute not in called_methods:
                                called_methods[attribute] = set()
                                called_methods[attribute].add(called_method)
                            else:
                                called_methods[attribute].add(called_method)
                            #print("_______________________________")


        self._called_methods = called_methods

        #print(self._called_methods['examples\\abode2\\state.Stateful._client'])
        #print(self._called_methods['examples\\abode2\\state.Stateful._state'])
        #print("_______________________________")

        #for k,v in self._called_methods.items():
        #    print(k,v)
        #print("_______________________________")

       

    def match(self):

        #print(self._methods['examples\\abode2\\state.Stateful'])
        #print(self._attributes['examples\\abode2\\state.Stateful'])

        
        attribute_matching_to_class = dict()

        #for class_name, methods in self._methods.items():
        #    for method in methods:
        #        method = method.split('.')[-1]
            #print(class_name, methods)
            

        #先遍历待匹配的方法，
        #examples\abode2\state.Stateful._client {'send_request', 'default_mode'}
        for attribute_name, called_methods in self._called_methods.items():
            #print(attribute_name, called_methods)
            # examples\abode2\client.Client {'examples\\abode2\\client.Client._send_request', 'examples\\abode2\\client.Client._load_devices.<dict1>'
            for class_name, methods in self._methods.items():
                # 判断一个set里的字符串对象都是另一个set字符串对象的子字符串
                #这是错误的，可能会出现方法覆盖
                #all_substrings = all(any(substring in s2 for s2 in methods) for substring in called_methods)
                #这才是正确的，方法名完全匹配
                all_substrings = all(any(substring == s2.split('.')[-1] for s2 in methods) for substring in called_methods)
                if all_substrings:
                    #可能出现多个对应的情况
                    if attribute_name not in attribute_matching_to_class:
                        attribute_matching_to_class[attribute_name] = set()
                        attribute_matching_to_class[attribute_name].add(class_name)
                    else:
                        attribute_matching_to_class[attribute_name].add(class_name)
                    #出现对应多个的情况就放弃，只保留一一对应

        self._attribute_matching_to_class = attribute_matching_to_class


        #for k,v in self._attribute_matching_to_class.items():
            #print(k,v)
        #examples\abode2\state.Stateful._client {'examples\\abode2\\client.Client'}
        #错误结果
        #examples\abode2\state.Stateful._state {'state.Stateful', 'base.Device', 'examples\\abode2\\client.Client', 'examples\\abode2\\state.Stateful', 'devices.base.Device', 'sensor.Sensor'}



    def generate(self):

        self.get_all_methods_and_attributes()
        self.collect_called_methods()
        self.match()
        
       


