import unittest
from hdl_toolkit.tests.synthetisator.interfaceLevel.baseSynthetisatorTC import BaseSynthetisatorTC
from hdl_toolkit.synthetisator.interfaceLevel.unitFromHdl import UnitFromHdl
from hdl_toolkit.hdlObjects.typeShortcuts import hInt

ILVL_V = '../../../samples/verilogCodesign/verilog/'

class VerilogCodesignTC(BaseSynthetisatorTC):
    def test_TernOpInModul(self):
        class TernOpInModulSample(UnitFromHdl):
            _hdlSources = ILVL_V + "ternOpInModul.v"
            _debugParser=True
                    
        u = TernOpInModulSample()
        u._loadDeclarations()
        
        self.assertEquals(u.a._dtype.getBitCnt(), 8)
        self.assertEquals(u.b._dtype.getBitCnt(), 1)
        
        u.CONDP.set(hInt(1))
        self.assertEquals(u.a._dtype.getBitCnt(), 4)
        self.assertEquals(u.b._dtype.getBitCnt(), 2)
        
    def test_SizeExpressions(self):
        class SizeExpressionsSample(UnitFromHdl):
            _hdlSources = ILVL_V + "sizeExpressions.v"        
        u = SizeExpressionsSample()
        u._loadDeclarations()
        
        A = u.paramA.get()
        B = u.paramB.get()
        self.assertEqual(u.portA._dtype.getBitCnt(), A.val)
        self.assertEqual(u.portB._dtype.getBitCnt(), A.val)
        self.assertEqual(u.portC._dtype.getBitCnt(), A.val // 8)
        self.assertEqual(u.portD._dtype.getBitCnt(), (A.val // 8) * 13)
        self.assertEqual(u.portE._dtype.getBitCnt(), B.val * (A.val // 8))
        self.assertEqual(u.portF._dtype.getBitCnt(), B.val * A.val)
        self.assertEqual(u.portG._dtype.getBitCnt(), B.val * (A.val - 4))
    
    def test_InterfaceArray(self):
        class InterfaceArraySample(UnitFromHdl):
            _hdlSources = ILVL_V + "interfaceArrayAxiStream.v"        
        u = InterfaceArraySample()
        u._loadDeclarations()
        
        self.assertEqual(u.input_axis.DATA_WIDTH.get().val, 32)
        self.assertEqual(u.input_axis._multipliedBy, u.LEN)
    
    
    def test_InterfaceArray2(self):
        class InterfaceArraySample(UnitFromHdl):
            _hdlSources = ILVL_V + "interfaceArrayAxi4.v"        
        u = InterfaceArraySample()
        u._loadDeclarations()
        
        self.assertEqual(u.s_axi._multipliedBy, u.C_NUM_SLAVE_SLOTS)
        self.assertEqual(u.m_axi._multipliedBy, u.C_NUM_MASTER_SLOTS)
    
    def test_paramSpecifiedByParam(self):
        class U(UnitFromHdl):
            _hdlSources = ILVL_V + "parameterSizeFromParameter.v"        
        u = U()
        u._loadDeclarations()
        
        self.assertEqual(u.A.get(), hInt(1))
        self.assertEqual(u.B.get(), hInt(2))
        
        
        self.assertEqual(u.aMultBMult64._dtype.getBitCnt(), 1*2*64)
        self.assertEqual(u.aMult32._dtype.getBitCnt(), 1*32)
        
    
    def test_axiCrossbar(self):
        class U(UnitFromHdl):
            _hdlSources = ILVL_V + "axiCrossbar.v"
        u = U()
        u._loadDeclarations()
        
        self.assertEqual(u.s_axi._multipliedBy, u.C_NUM_SLAVE_SLOTS)
        self.assertEqual(u.m_axi._multipliedBy, u.C_NUM_MASTER_SLOTS)
        
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    #suite.addTest(VerilogCodesignTC('test_TernOpInModul'))
    suite.addTest(unittest.makeSuite(VerilogCodesignTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
