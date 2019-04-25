from xdapp.xdappAgent import XDAppServiceAgent
from xdapp.context import Context, getCurrentContext
from xdapp.common import HproseResultMode, HproseException
from xdapp.io import HproseTags, HproseClassManager, HproseRawReader, HproseReader, HproseWriter, HproseFormatter
from xdapp.server import HproseService

ServiceAgent = XDAppServiceAgent
Context = Context
getCurrentContext = getCurrentContext

ResultMode = HproseResultMode
Tags = HproseTags
ClassManager = HproseClassManager
RawReader = HproseRawReader
Reader = HproseReader
Writer = HproseWriter
Formatter = HproseFormatter
serialize = Formatter.serialize
unserialize = Formatter.unserialize
Service = HproseService