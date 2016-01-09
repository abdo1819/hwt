from vhdl_toolkit.synthetisator.interfaceLevel.synthetizator import Unit
from vhdl_toolkit.synthetisator.interfaceLevel.stdInterfaces import Axi4, Ap_clk, \
    Ap_rst_n
from vhdl_toolkit.formater import formatVhdl
from vhdl_toolkit.synthetisator.param import Param, inheritAllParams

class AxiLiteBasicSlave(Unit):
    _origin = "vhdl/axiLite_basic_slave.vhd"
    
    
@inheritAllParams
class AxiLiteSlaveContainer(Unit):
    ADDR_WIDTH = Param(32)
    DATA_WIDTH = Param(32)
    slv = AxiLiteBasicSlave()
    clk = Ap_clk(slv.S_AXI_ACLK, isExtern=True)
    rst_n = Ap_rst_n(slv.S_AXI_ARESETN, isExtern=True)
    axi = Axi4(slv.S_AXI, isExtern=True)


if __name__ == "__main__":
    u = AxiLiteSlaveContainer()
    s = [ formatVhdl(str(x)) for x in u._synthesise()]
    print("\n".join(s))
