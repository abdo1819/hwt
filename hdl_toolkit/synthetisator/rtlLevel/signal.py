from hdl_toolkit.hdlObjects.assignment import Assignment
from hdl_toolkit.hdlObjects.types import HdlType
from hdl_toolkit.hdlObjects.variables import SignalItem
from hdl_toolkit.hdlObjects.operator import Operator, InvalidOperandExc
from hdl_toolkit.hdlObjects.operatorDefs import AllOps
from hdl_toolkit.hdlObjects.value import Value
from hdl_toolkit.simulator.exceptions import SimNotInitialized
from hdl_toolkit.hdlObjects.typeDefs import BOOL

def checkOperands(ops):
    for op in ops:
        checkOperand(op)

def checkOperand(op):
    if isinstance(op, Value) or isinstance(op, Signal):
        return
    else:
        raise InvalidOperandExc("Operands in hdl expressions can be only instance of Value or Signal,"
                                + "\ngot instance of %s" % (op.__class__))

# [TODO] move to Operator, problem with reference Signal/Operator -> signal and operators have to be separated
class SignalNode():

    @staticmethod
    def resForOp(op):
        t = op.getReturnType() 
        out = Signal(None, t)
        out.drivers.add(op)
        out.origin = op
        op.result = out
        return out

class SignalOps():
    def unaryOp(self, operator):
        try:
            o = self._usedOps[operator]
            return o.result
        except KeyError:
            o = Operator(operator, [self])
            self._usedOps[operator] = o
        
            return SignalNode.resForOp(o)
    
    def naryOp(self, operator, operands):
        checkOperands(operands)
        operands = list(operands)
        operands.insert(0, self)
        o = Operator(operator, operands)
        
        return SignalNode.resForOp(o)
    
    
    def opNot(self):
        return self.unaryOp(AllOps.NOT)
        
    def opOnRisigEdge(self):
        return self.unaryOp(AllOps.RISING_EDGE)
    
    def opAnd(self, *operands):
        return self.naryOp(AllOps.AND_LOG, operands)
    
    def opMul(self, *operands):
        return self.naryOp(AllOps.MUL, operands)
    
    def opXor(self, *operands):
        return self.naryOp(AllOps.XOR, operands)

    def opOr(self, *operands):
        return self.naryOp(AllOps.OR_LOG, operands)

    def opIsOn(self):
        return self.dtype.convert(self, BOOL)
        
    def opEq(self, *operands):
        return self.naryOp(AllOps.EQ, operands)

    def opNEq(self, *operands):
        return self.naryOp(AllOps.NEQ, operands)
    
    def opAdd(self, *operands):
        return self.naryOp(AllOps.PLUS, operands)
    
    def opSub(self, *operands):
        return self.naryOp(AllOps.MINUS, operands)
    
    def opDiv(self, divider):
        return self.naryOp(AllOps.DIV, [divider])
    
    def opDownto(self, to):
        return self.naryOp(AllOps.DOWNTO, [to])
    
    def opSlice(self, index):
        return self.naryOp(AllOps.INDEX, [index])
    
    def opConcat(self, *operands):
        return self.naryOp(AllOps.CONCAT, operands)
    
    def assignFrom(self, source):
        checkOperand(source)
        a = Assignment(source, self)
        a.cond = set()
        try:
            d = self.singleDriver()
            if isinstance(d, Operator) and d.operator == AllOps.INDEX:
                self.drivers.remove(d) # data direction is to indexed element
                self.endpoints.add(d)
        except AssertionError:
            pass
        
        self.drivers.add(a)
        if not isinstance(source, Value):
            source.endpoints.add(a)
        return a
    
    
class Signal(SignalItem, SignalOps):
    """
    more like net
    @ivar _usedOps: dictionary of used operators which can be reused
    """
    def __init__(self, name, dtype, defaultVal=None):
        if name is None:
            name = "sig_" + str(id(self))
            self.hasGenericName = True 
       
        assert(isinstance(dtype, HdlType))  # == can be range, downto, to etc.
        super(Signal, self).__init__(name, dtype, defaultVal)
        self.endpoints = set()
        self.drivers = set()
        self._usedOps = {}
        self.negated = False
    
    def simPropagateChanges(self):
        if self._oldVal != self._val or self._oldVal.eventMask != self._val.eventMask:
            conf = self._simulator.config
            env = self._simulator.env
            self._oldVal = self._val
            for e in self.endpoints:
                if conf.log:
                    conf.logger("%d: Signal.simPropagateChanges %s -> %s" % (env.now, self.name, str(e)))
                yield env.process(e.simPropagateChanges())
        
    def staticEval(self):
        # operator writes in self._val new value
        if self.drivers:
            for d in self.drivers:
                d.staticEval()
        else:
                if isinstance(self.defaultVal, Signal):
                        self._val = self.defaultVal._val
                else:
                    if not self._val.vldMask: # [TODO] find better way how to find out if was initialized
                        self._val = self.defaultVal
        return self._val
    
    def simUpdateVal(self, newVal):
        assert(isinstance(newVal, Value))
        self._val = newVal
        try:
            env = self._simulator.env
        except AttributeError:
            raise SimNotInitialized("Singal %s does not contains reference to its simulator" % (str(self)))
        c = self._simulator.config
        if  c.log:
            c.logger("%d: %s <= %s" % (env.now, self.name, str(newVal)))
        
        yield env.process(self.simPropagateChanges())
     
    def singleDriver(self):
        assert(len(self.drivers) == 1)
        return list(self.drivers)[0]
            
class SyncSignal(Signal):
    def __init__(self, name, var_type, defaultVal=None):
        super().__init__(name, var_type, defaultVal)
        self.next = Signal(name + "_next", var_type, defaultVal)
        
    def assignFrom(self, source):
        a = Assignment(source, self.next)
        a.cond = set()
        self.next.drivers.add(a)
        if not isinstance(source, Value):
            self.endpoints.add(source)
             
        return a


def areSameSignals(a, b):
    if a is b:
        return True
    if type(a) != type(b):
        return False 
    if len(a.drivers) != 1 or len(b.drivers) != 1:
        return False
    da = list(a.drivers)[0]
    db = list(b.drivers)[0]
    return da == db