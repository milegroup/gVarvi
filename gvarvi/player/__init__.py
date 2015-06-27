# coding=utf-8

# --- General imports for all Players ---

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO