from machinery.classes import ClassManager,ClassNode
from machinery.scopes import ScopeManager,ScopeItem
from machinery.definitions import DefinitionManager,Definition


class Dataflow:
    
    def __init__(self, class_manager: ClassManager, scope_manager: ScopeManager, definition_manager: DefinitionManager) -> None:

        #dict(ns, ClassNode)
        self._all_classes = class_manager.get_classes() 
        #dict(ns, ScopeItem)
        self._all_scopes = scope_manager.get_scopes()
        #dict(ns, Definition)
        self._all_definitions = definition_manager.get_defs()


        self._methods = set()
        #self._attributes = dict()

        #ns, set(pointer)
        #只记录变量指针，常值不在调用图中，无意义
        self._return_information = dict()

        self._class_variable_information = dict()
        self._function_parameter_variable_information = dict()

        self._assign_information = dict()

    def get_all_methods(self):
        
        for defi_key, Definition in self._all_definitions.items():
            if Definition.def_type == 'FUNCTIONDEF':
                self._methods.add(Definition.fullns)

        #print("全部的方法名")
        #for i in self._methods:
        #    print(i)
        #print("_______________________")

    '''def get_all_methods_and_attributes(self):
            
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
                #输出有单字符？原因？
                elif class_key in scope_key and class_key != scope_key and '<' not in scope_key:  
                    if class_key not in methods:
                        methods[class_key] = set()
                        methods[class_key].add(scope_key)
                    else:
                        methods[class_key].add(scope_key)
                    #if class_key == 'examples\\abode2\\state.Stateful':
                    #    print(methods[class_key])

        for class_name,set1 in methods_and_attributes.items():
            if class_name in methods:
                set2 = methods[class_name]
                set3 = set1 - set2
                attributes[class_name] = set3

        self._methods = methods
        self._attributes = attributes

        print("全部的方法名")
        for k, v in self._methods.items():
            print(k,v)
        print("_______________________")'''


        #for k, v in self._attributes.items():
        #    print(k,v)


    #参数依赖和常规赋值结合到一起，因为难以区分
    def get_assign(self):

        for class_key, classNode in self._all_classes.items():
            for scope_key, scopeItem in self._all_scopes.items():
                #处理类的变量
                if class_key == scope_key:
                    for key, Definition in scopeItem.defs.items():
                        if len(Definition.points_to['name'].values) != 0:
                            #print(Definition.fullns)
                            self._class_variable_information[Definition.fullns] = Definition.points_to['name'].values
                #处理方法变量（参数和一般变量）
                elif class_key in scope_key and class_key != scope_key and '<' not in scope_key:
                    for key, Definition in scopeItem.defs.items():
                        if len(Definition.points_to['name'].values) != 0:
                            #print(Definition.fullns)
                            self._function_parameter_variable_information[Definition.fullns] = Definition.points_to['name'].values

        #需要翻转过来，key为赋值的变量，value为被赋值的变量
        for key, sets in self._class_variable_information.items():
            #print(key, sets)
            for value in sets:
                if value not in self._assign_information:
                    self._assign_information[value.split(".<RETURN>")[0]] = set()
                self._assign_information[value.split(".<RETURN>")[0]].add(key.split(".<RETURN>")[0])
        #print("_______________________")
        for key, sets in self._function_parameter_variable_information.items():
            #print(key, sets)
            for value in sets:
                if value not in self._assign_information:
                    self._assign_information[value.split(".<RETURN>")[0]] = set()
                self._assign_information[value.split(".<RETURN>")[0]].add(key.split(".<RETURN>")[0])
        #print("_______________________")

        #print("赋值和参数依赖：")
        #for k,v in self._assign_information.items():
        #    print(k,v)
        #print("_______________________")

    def get_parameter(self):
        pass


    def get_return(self):
        
        temp_dict = dict()

        for defi_key, Definition in self._all_definitions.items():
            #保证不为空 
            if "<RETURN>" in defi_key and len(Definition.points_to['name'].values) != 0:
                temp_dict[defi_key] = Definition.points_to['name'].values

        #for k,v in temp_dict.items():
        #    print(k,v)
        #print("_______________________")

        for key, sets in temp_dict.items():
            for value in sets:
                if value not in self._return_information:
                    self._return_information[value.split(".<RETURN>")[0]] = set()
                self._return_information[value.split(".<RETURN>")[0]].add(key.split(".<RETURN>")[0])
                #self._return_information[value].add(key)
        
        #print("返回值依赖：")
        #key是方法中return后面跟着的变量名，value是方法名
        '''..\SDK_dataset\pymystrom\bulb.MyStromBulb._firmware {'..\\SDK_dataset\\pymystrom\\bulb.MyStromBulb.firmware'}
        ..\SDK_dataset\pymystrom\bulb.MyStromBulb._mac {'..\\SDK_dataset\\pymystrom\\bulb.MyStromBulb.mac'}
        ..\SDK_dataset\pymystrom\bulb.MyStromBulb.__init__.mac {'..\\SDK_dataset\\pymystrom\\bulb.MyStromBulb.mac'}
        ..\SDK_dataset\pymystrom\bulb.MyStromBulb._consumption {'..\\SDK_dataset\\pymystrom\\bulb.MyStromBulb.consumption'}
        ..\SDK_dataset\pymystrom\bulb.MyStromBulb._color {'..\\SDK_dataset\\pymystrom\\bulb.MyStromBulb.color'}'''
        #for k,v in self._return_information.items():
        #    print(k,v)
        #print("_______________________")





