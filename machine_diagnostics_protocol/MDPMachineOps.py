import psutil
from os.path import dirname, basename, isfile, join
import glob
from importlib import import_module

class MDPMachineOps:
    def do_op(self, op_name: str):
        op_func_name = "subfunc_" + op_name
        op_func = getattr(self, op_func_name)
        return op_func()
    
    def subfunc_get_cpu_percent(self):
        """Returns current CPU usage"""
        return psutil.cpu_percent()

    def subfunc_get_machine_memory(self):
        """Returns the RAM of machine consumed"""
        return psutil.virtual_memory()

    def subfunc_get_available_methods(self):
        method_list = [func for func in dir(MDPMachineOps) if callable(getattr(MDPMachineOps, func)) and func.startswith("subfunc")]
        method_list.remove(self.subfunc_get_available_methods.__name__)
        method_docs = { 
            k.replace("subfunc_", ""): getattr(MDPMachineOps, k).__doc__ for k in method_list
        }
        
        return method_docs

additional_functions = glob.glob("mdp_operations/*.py")
for function_file in additional_functions:
    module_name = function_file.replace("/", ".").replace(".py", "")
    dynamic_module = import_module(module_name)
    functions = [func for func in dir(dynamic_module) if func.startswith("subfunc")]
    for module_func in functions:
        setattr(MDPMachineOps, module_func, getattr(dynamic_module, module_func))
    del dynamic_module