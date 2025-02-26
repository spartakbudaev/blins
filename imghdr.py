"""Recognize image file formats based on their first few bytes."""

__all__ = ["what"]

def what(file, h=None):
    """Recognize image file formats based on their first few bytes."""
    if h is None:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            location = file.tell()
            h = file.read(32)
            file.seek(location)
    for tf in tests:
        res = tf(h, file)
        if res:
            return res

tests = []

def test_jpeg(h, f):
    """JPEG data in JFIF or Exif format"""
    if h[0:2] == b'\xff\xd8':
        return 'jpeg'

tests.append(test_jpeg)

def test_png(h, f):
    """PNG data"""
    if h[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'

tests.append(test_png)

def test_gif(h, f):
    """GIF ('87 and '89 variants)"""
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

tests.append(test_gif)

def test_tiff(h, f):
    """TIFF (can be in Motorola or Intel byte order)"""
    if h[:2] in (b'MM', b'II'):
        return 'tiff'

tests.append(test_tiff)

def test_webp(h, f):
    """WebP image data"""
    if h[:4] == b'RIFF' and h[8:12] == b'WEBP':
        return 'webp'

tests.append(test_webp)

def test_bmp(h, f):
    """BMP image data"""
    if h[:2] == b'BM':
        return 'bmp'

tests.append(test_bmp) 