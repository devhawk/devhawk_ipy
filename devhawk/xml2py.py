#####################################################################################
#
#  Copyright (c) Harry Pierson. All rights reserved.
#
# This source code is subject to terms and conditions of the Microsoft Public License. 
# A  copy of the license can be found at http://opensource.org/licenses/ms-pl.html
# By using this source code in any fashion, you are agreeing to be bound 
# by the terms of the Microsoft Public License.
#
# You must not remove this notice, or any other, from this software.
#
#####################################################################################

import ipypulldom
  
class xmlnode_type_factory(object):
  '''xmlnode_type_factory creates types based on xmlnodes, but it caches them so they only get created once'''
  class _node_proxy(object):
    '''when generating types based on previously generated types, we use a node proxy to emulate a node so the find_type code below doesn't change.''' 
    def __init__(self, node):
      ty = type(node)
      self.name = ty.__name__
      self.namespace = ty.xmlns
    
  def __init__(self):
    self.types = {}

  def find_type(self, node, parent):
    '''find_type will look in the types cache for a type to represent the provided node with the provided parent,
    if no type has already exists, find_type will create and cache one.'''

    #top level of types cache keyed off parent type
    if parent not in self.types:
      self.types[parent] = {}
    tp = self.types[parent]
    
    #next, level of types cached keyed off node name
    if node.name not in tp:
      tp[node.name] = {}
    tpn = tp[node.name]

    #final level of types cache keyed of node namespace
    if node.namespace not in tpn:
      tpn[node.namespace] = type(node.name, (parent,), {'xmlns':node.namespace})
    return tpn[node.namespace]
  
  def __call__(self, node, parent=object ):
    #if node is an XmlNode, then use it's name & namespace directly
    if isinstance(node, ipypulldom.XmlNode):
      return self.find_type(node, parent) 
    
    #if we're creating a new object from an already created object, 
    #create a _node_proxy based on node's type
    return self.find_type(self._node_proxy(node), parent)


xtype = xmlnode_type_factory()

  
def xml2py(nodelist):
  '''translate a stream of XmlNodes into a tree of python objects'''
  from System.Xml import XmlNodeType
  
  def children(nodelist):
    '''generate the child iterator by recursively calling xmlpy'''
    while True:
      child = xml2py(nodelist)
      if child is None:
        break
      yield child
  
  def set_attribute(parent, child):
    '''dynamically add the child to the parent attributes by child name.
    Automatically promote parent attribute to a list if there are multiple children with the same name'''
    name = type(child).__name__
    if not hasattr(parent, name):
      setattr(parent, name, child)
    else:
      val = getattr(parent, name)
      if isinstance(val, list):
        val.append(child)
      else:
        setattr(parent, name, [val, child])
      
  node = nodelist.next()
  if node.nodeType == XmlNodeType.EndElement:
    return None
    
  elif node.nodeType == XmlNodeType.Text or node.nodeType == XmlNodeType.CDATA:
    return node.value
    
  elif node.nodeType == XmlNodeType.Element:
    #create a new object type named for the element name
    cur = xtype(node)()
    cur._nodetype = XmlNodeType.Element
   
    #collect all the attributes and children in lists
    attributes = [xtype(attr, str)(attr.value) for attr in node.attributes]
    children = [child for child in children(nodelist)]
    
    if len(children) == 1 and isinstance(children[0], str):
      #fold up elements with a single text node
      cur = xtype(cur, str)(children[0])
      cur._nodetype = XmlNodeType.Element
    else:
      #otherwise, add child elements as properties on the current node
      for child in children:
        set_attribute(cur, child)

    #add attributes as properties on the current node as well
    for attr in attributes:
      attr._nodetype = XmlNodeType.Attribute
      set_attribute(cur, attr)
             
    return cur


def load(xml):
  return xml2py(ipypulldom.load(xml))
  
def parse(xml):
  return xml2py(ipypulldom.parse(xml))
  

if __name__ == '__main__':  
  rss = parse('Devhawk.rss.xml')
  for item in rss.channel.item:
    print item.title
  