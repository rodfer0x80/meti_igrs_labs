import sys
import KSR as KSR


# Mandatory function - module initiation
def mod_init():
    KSR.info("===== from Python mod init\n")
    return kamailio()

class kamailio:
    # Mandatory function - Kamailio class initiation
    def __init__(self):
        KSR.info('===== kamailio.__init__\n')

    # Mandatory function - Kamailio subprocesses
    def child_init(self, rank):
        KSR.info('===== kamailio.child_init(%d)\n' % rank)
        return 0

    # Mandatory function - Kamailio subprocesses
    def ksr_request_route(self, msg):
        # Working as a Registrar server
        if  (msg.Method == "REGISTER"):
            # Obtaining values via Pseudo-variables (pv)
            KSR.info("REGISTER R-URI: " + KSR.pv.get("$ru") + "\n")
            KSR.info("            To: " + KSR.pv.get("$tu") +
            # Obtaining values via message header fields
                           " Contact: " + KSR.hdr.get("Contact") +"\n")
            # Calling Kamailio "registrar" module
            KSR.registrar.save('location', 0)                            
            return 1

        # Working as a Redirect server
        if (msg.Method == "INVITE"):                      
            KSR.info("INVITE R-URI: " + KSR.pv.get("$ru") + "\n")
            KSR.info("        From: " + KSR.pv.get("$fu") +
                              " To: " + KSR.pv.get("$tu") +"\n")
    
            # Check if To domain is not sipnet.a
            if (KSR.pv.get("$td") != "sipnet.a"):
                KSR.sl.send_reply(403, "Cannot route beyond sipnet.a")
                return 1

            # Check if To domain is sipnet.a (unnecessary duplicate)
            if (KSR.pv.get("$td") == "sipnet.a"):
                # Check if registered
                if (KSR.registrar.lookup("location") == 1):
                    KSR.info("  lookup changed R-URI to : " + KSR.pv.get("$ru") +"\n")
                    # Remove existing Contact header if any
                    KSR.hdr.remove("Contact")
                    # Add new Contact header
                    new_contact = "Contact:" + KSR.pv.get("$ru") + "\r\n"
                    KSR.hdr.insert(new_contact)
                    KSR.sl.send_reply(300, "Redirect")
                    return 1
                else:
                    KSR.sl.send_reply(404, "Not found")
                    return 1

        # If this part is reached then Method is not allowed
        KSR.info("A non-supported method: " + msg.Method + "\n")
        KSR.sl.send_reply(403, "Forbiden method")
        return 1

    # Mandatory function - Kamailio subprocesses
    def ksr_reply_route(self, msg):
        KSR.info("===== response - from kamailio python script\n")
        KSR.info("      Status is:"+ str(KSR.pv.get("$rs")) + "\n")
        return 1

    def ksr_onsend_route(self, msg):
        KSR.info("===== onsend route - from kamailio python script\n")
        KSR.info("      %s\n" %(msg.Type))
        return 1
