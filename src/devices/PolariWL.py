# coding=utf-8
__author__ = 'nico'

from wx import PostEvent

from devices.IDevice import BTAbstractDevice
from Utils import run_in_thread
from Utils import ResultEvent


class PolariWL(BTAbstractDevice):
    def __init__(self, mac):
        BTAbstractDevice.__init__(self, mac)
        self.socket = None
        self.end_test = False
        self.ended_test = False
        self.end_adquisition = False
        self.ended_adquisition = False
        self.correct_data = False
        self.error = False
        self.min_rr = 550

    @run_in_thread
    def run_test(self, notify_window):
        self.end_test = False
        self.ended_test = False
        self.error = False
        test_dict = {}
        while not self.end_test:
            try:
                data1 = self.receive(1)
                data2 = self.receive(1)
                ll = int(data2, 16)
                data3 = self.receive(ll - 2)

                chk = int(data3[0:2], 16)
                if chk + ll != 255:
                    print "*** ERROR: Package not Ok ***"

                test_dict['hr'] = int(data3[6:8], 16)
                # print "Heart rate:", hr, "bpm"
                nextbit = 8

                for i in range((ll - 6) / 2):  # No. de valores RR por paquete
                    rr1 = int(data3[nextbit:nextbit + 2], 16)
                    rr2 = int(data3[nextbit + 2:nextbit + 4], 16)
                    test_dict['rr'] = (rr1 << 8) | rr2
                    if self.end_test:
                        return
                    PostEvent(notify_window, ResultEvent(test_dict))

                    nextbit = nextbit + 4


            except ValueError as e:
                if not self.end_test:  # Exception only works if BT is still connected
                    print "*** Exception ValueError raised: data not Ok ***"
                    import traceback, os.path

                    top = traceback.extract_stack()[-1]
                    print "Program:", os.path.basename(top[0]), " -  Line:", str(top[1])
                    print "Data:"
                    print data1
                    print data2
                    print data3
                    self.error = True
                else:
                    print "*** Warning: ValueError raised at the end of the adquisition"


            # except Exception as e:
            #     print e.message
            #     import traceback, os.path
            #
            #     top = traceback.extract_stack()[-1]
            #     print "*** Exception:", type(e).__name__, " -  Program:", os.path.basename(top[0]), " -  Line:", str(
            #         top[1]), "***"
            #     self.error = True

            if self.end_test:
                self.ended_test = True
                break

    def finish_test(self):
        self.end_test = True

    @run_in_thread
    def begin_adquisition(self, writer):
        self.end_adquisition = False
        self.ended_adquisition = False
        self.error = False
        while not self.end_adquisition:
            try:
                data1 = self.receive(1)
                data2 = self.receive(1)
                ll = int(data2, 16)
                data3 = self.receive(ll - 2)
                chk = int(data3[0:2], 16)
                if chk + ll != 255:
                    print "*** ERROR: Package not Ok ***"

                seq = int(data3[2:4], 16)
                print "Package seq:", seq

                status = int(data3[4:6], 16)
                print "Package status:", status

                hr = int(data3[6:8], 16)
                print "Heart rate:", hr, "bpm"
                nextbit = 8

                print "Package contains", (ll - 6) / 2, "beats"

                for i in range((ll - 6) / 2):  # No. de valores RR por paquete
                    rr1 = int(data3[nextbit:nextbit + 2], 16)
                    rr2 = int(data3[nextbit + 2:nextbit + 4], 16)
                    rr = (rr1 << 8) | rr2

                    print "    RR:", rr, "mseg."

                    if rr > self.min_rr and not self.correct_data:
                        self.correct_data = True

                    writer.write_rr_value(rr)

                    nextbit = nextbit + 4


            except ValueError as e:
                if not self.end_adquisition:  # Exception only works if BT is still connected
                    print "*** Exception ValueError raised: data not Ok ***"
                    import traceback
                    import os.path

                    top = traceback.extract_stack()[-1]
                    print "Program:", os.path.basename(top[0]), " -  Line:", str(top[1])
                    print "Data:"
                    print data1
                    print data2
                    print data3
                    self.error = True
                else:
                    print "*** Warning: ValueError raised at the end of the adquisition"


            except Exception as e:
                import traceback
                import os.path

                top = traceback.extract_stack()[-1]
                print "*** Exception:", type(e).__name__, " -  Program:", os.path.basename(top[0]), " -  Line:", str(
                    top[1]), "***"
                self.error = True

            if self.end_adquisition:
                self.ended_adquisition = True
                writer.close_writer()
                break

    def finish_adquisition(self):
        self.end_adquisition = True








