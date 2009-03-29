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

"""ipypulldom is a pythonic wrapper around XmlReader, inspired by python's standard pulldom class """

from __future__ import with_statement
import clr
clr.AddReference('System.Xml')

from System.Xml import XmlNodeType, XmlReader

class XmlNode(object):
  """ XmlNode represents a single node in the XML stream"""
  def __init__(self, xr, endElement=False):
    """initalize an XmlNode from an XmlReader instance"""

    self.name = xr.LocalName
    self.namespace = xr.NamespaceURI
    self.prefix = xr.Prefix
    self.value = xr.Value
    if xr.IsEmptyElement and endElement:
      self.nodeType = XmlNodeType.EndElement
    else:
      self.nodeType = xr.NodeType

      if xr.NodeType == XmlNodeType.Element:
        self.attributes = []
        while xr.MoveToNextAttribute():
          if xr.NamespaceURI == 'http://www.w3.org/2000/xmlns/':
            continue
          self.attributes.append(XmlNode(xr))
        xr.MoveToElement()
    
  @property
  def xname(self):
    """the xname property returns the combined namespace uri and local name of the node, similar to how LINQ to XML's does"""
    from System.String import IsNullOrEmpty as IsEmptyStr
    if IsEmptyStr(self.namespace):
      return self.name
    
    return "{%(namespace)s}%(name)s" % self.__dict__

def _process(xr):
  while xr.Read():
    xr.MoveToContent()
    node = XmlNode(xr)
    yield node
    if xr.IsEmptyElement:
      node = XmlNode(xr, endElement=True)
      yield node

def load(xml):
  """generates an iterator over the XmlNodes in the stream of XML represented by the xml argument"""
  if isinstance(xml, XmlReader):
    for n in _process(xml): yield n
  else:
    with XmlReader.Create(xml) as xr:
      for n in _process(xr): yield n
    
def parse(xml):
  """generates an iterator over the XmlNodes in the raw XML string provided"""
  from System.IO import StringReader
  return load(StringReader(xml))

if __name__ == "__main__":
  nodes = load('http://feeds2.feedburner.com/Devhawk')      
  for node in nodes:
    print node.xname, node.nodeType