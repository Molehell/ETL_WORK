#
# Copyright (c) 2012-2017 The ANTLR Project. All rights reserved.
# Use of this file is governed by the BSD 3-clause license that
# can be found in the LICENSE.txt file in the project root.
#


# A set of utility routines useful for all kinds of ANTLR trees.#
from io import StringIO
import antlr4
from antlr4.atn.ATN import ATN
from antlr4.Token import Token
from antlr4.Utils import escapeWhitespace
from antlr4.tree.Tree import RuleNode, ErrorNode, TerminalNode

class Trees(object):

    # Print out a whole tree in LISP form. {@link #getNodeText} is used on the
    #  node payloads to get the text for the nodes.  Detect
    #  parse trees and extract data appropriately.
    @classmethod
    def toStringTree(cls, t, ruleNames=None, recog=None):
        __string_list = []
        if recog is not None:
            ruleNames = recog.ruleNames
        s = escapeWhitespace(cls.getNodeText(t, ruleNames), False)
        if t.getChildCount()==0:
            return s
        with StringIO() as buf:
            
            if s not in __string_list :
                buf.write(u"<")
                buf.write(s)
                buf.write(u'>')
            for i in range(0, t.getChildCount()):
                if i > 0:
                    buf.write(u' ')
                buf.write(cls.toStringTree(t.getChild(i), ruleNames))
            if s not in __string_list:
                buf.write(u"</")
                buf.write(s)
                buf.write(u">")

            with open('/workhome/sql_python/original.xml','w') as file:
                file.write(buf.getvalue())
            #return buf.getvalue()
