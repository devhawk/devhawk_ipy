import clr

def compile(prov, file, references):
  from System.CodeDom.Compiler import CompilerParameters 
  from System.Reflection.Assembly import LoadWithPartialName 
  cp = CompilerParameters()
  cp.GenerateInMemory = True
  for ref in references:
    a = LoadWithPartialName(ref)
    cp.ReferencedAssemblies.Add(a.Location)
  cr = prov.CompileAssemblyFromFile(cp, file)
  if cr.Errors.Count > 0:
    raise Exception(cr.Errors)
  return cr.CompiledAssembly
    
def add_reference_cs_file(file, references):
  from Microsoft.CSharp import CSharpCodeProvider
  clr.AddReference(compile(CSharpCodeProvider(), file, references))
  
def add_reference_vb_file(file, references):
  from Microsoft.VisualBasic import VBCodeProvider
  clr.AddReference(compile(VBCodeProvider(), file, references))
  