"""Identity transport with unique, idempotent private diagnostic logging."""
import uuid
import custodian as original
import transport1
import register as r


class Source(original.Source):
    def __init__(self,item):
        super().__init__(item);self.http.close();self.diagnostics=[]
        self.http=transport1.TraceSession(self)
        self.diagnostic_id=uuid.uuid4().hex
        self.diagnostic_written=False
    def close(self):
        if hasattr(self,'diagnostics') and not self.diagnostic_written:
            root=r.HERE/'.private/transport_diagnostics4'
            root.mkdir(parents=True,exist_ok=True);original.protect(root)
            path=root/(self.diagnostic_id+'.json')
            r.save(path,self.diagnostics,True);original.protect(path)
            self.diagnostic_written=True
        super().close()
