#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite for the response handling.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
import inspect
from obspy.signal.invsim import evalresp
from obspy.station import read_inventory
from obspy.xseed import Parser
import os
import unittest


import numpy as np


class ResponseTest(unittest.TestCase):
    """
    Tests the for :class:`~obspy.station.inventory.Inventory` class.
    """
    def setUp(self):
        # Most generic way to get the actual data directory.
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe()))), "data")

    def test_evalresp_with_output_from_seed(self):
        """
        The StationXML file has been converted to SEED with the help of a tool
        provided by IRIS:

        https://seiscode.iris.washington.edu/projects/stationxml-converter
        """
        t_samp = 0.05
        nfft = 16384
        # Test for different output units.
        units = ["DISP", "VEL", "ACC"]
        filenames = ["IRIS_single_channel_with_response", "XM.05"]

        for filename in filenames:
            xml_filename = os.path.join(self.data_dir,
                                        filename + os.path.extsep + "xml")
            seed_filename = os.path.join(self.data_dir,
                                         filename + os.path.extsep + "seed")

            p = Parser(seed_filename)
            resp_filename = p.getRESP()[0][-1]
            inv = read_inventory(xml_filename)

            network = inv[0].code
            station = inv[0][0].code
            location = inv[0][0][0].location_code
            channel = inv[0][0][0].code
            date = inv[0][0][0].start_date

            for unit in units:
                resp_filename.seek(0, 0)

                seed_response, seed_freq = evalresp(
                    t_samp, nfft, resp_filename, date=date, station=station,
                    channel=channel, network=network, locid=location,
                    units=unit, freq=True)

                xml_response, xml_freq = \
                    inv[0][0][0].response.get_evalresp_response(t_samp, nfft,
                                                                output=unit)

                np.testing.assert_allclose(seed_freq, xml_freq, rtol=1E-5)
                np.testing.assert_allclose(seed_response, xml_response,
                                           rtol=1E-5)


def suite():
    return unittest.makeSuite(ResponseTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
