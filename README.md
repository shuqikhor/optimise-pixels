This script assumes that you're feeding in an svg with a bunch of `<rect />` such as this:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Adobe Illustrator 26.4.1, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
<svg version="1.1" baseProfile="basic" id="Layer_1"
	 xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 9 9"
	 xml:space="preserve">
<rect x="3" y="6" fill="#F92F3C" width="1" height="1"/>
<rect x="4" y="5" fill="#F92F3C" width="1" height="1"/>
<rect x="3" y="4" fill="#00AF3E" width="1" height="1"/>
<rect x="2" y="3" fill="#00AF3E" width="1" height="1"/>
<rect x="1" y="2" fill="#00AF3E" width="1" height="1"/>
<rect x="2" y="4" fill="#00AF3E" width="1" height="1"/>
<rect x="1" y="3" fill="#00AF3E" width="1" height="1"/>
<rect x="7" y="3" fill="#00AF3E" width="1" height="1"/>
<rect x="6" y="3" fill="#00AF3E" width="1" height="1"/>
<rect x="2" y="2" fill="#00AF3E" width="1" height="1"/>
<rect x="6" y="2" fill="#00AF3E" width="1" height="1"/>
<rect x="6" y="4" fill="#00AF3E" width="1" height="1"/>
<rect x="5" y="4" fill="#00AF3E" width="1" height="1"/>
<rect x="3" y="3" fill="#00AF3E" width="1" height="1"/>
<rect x="5" y="3" fill="#00AF3E" width="1" height="1"/>
<rect x="7" y="2" fill="#00AF3E" width="1" height="1"/>
<rect x="5" y="6" fill="#F92F3C" width="1" height="1"/>
</svg>
```

It will then optimise it to:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9">
	<rect fill="#F92F3C" x="4" y="5" width="1" height="1"/>
	<rect fill="#F92F3C" x="3" y="6" width="1" height="1"/>
	<rect fill="#F92F3C" x="5" y="6" width="1" height="1"/>
	<path fill="#00AF3E" d="M1,2V4H2V5H4V3H3V2z"/>
	<path fill="#00AF3E" d="M5,5H7V4H8V2H6V3H5z"/>
</svg>
```

To use it, simply run: `python optimise-pixels.py path-to-file.svg`
