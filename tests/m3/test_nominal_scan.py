"""
Nominal scan sequence.
"""


def test_scan(recording_pkg):
    """Test nominal scan sequence."""
    recording_pkg.alobserver.observe_true(True)


def test_scan_2(recording_pkg):
    """Test nominal scan sequence."""
    recording_pkg.alobserver.observe_true(False)
