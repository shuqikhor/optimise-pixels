This script assumes that you're feeding in an svg with a bunch of 1x1 `<rect />` that represent the pixels, such as this:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Adobe Illustrator 26.4.1, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
<svg version="1.1" baseProfile="basic" id="Layer_1"
	 xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 9 9"
	 xml:space="preserve">
<g>
	<rect x="1" y="4" fill="#F92F3C" width="1" height="1"/>
	<rect x="1" y="5" fill="#F92F3C" width="1" height="1"/>
	<rect x="2" y="4" fill="#F92F3C" width="1" height="1"/>
	<rect x="3" y="4" fill="#F92F3C" width="1" height="1"/>
	<rect x="2" y="5" fill="#F92F3C" width="1" height="1"/>
	<rect x="3" y="5" fill="#DA2934" width="1" height="1"/>
	<rect x="4" y="4" fill="#F92F3C" width="1" height="1"/>
	<rect x="5" y="4" fill="#F92F3C" width="1" height="1"/>
	<rect x="4" y="5" fill="#F92F3C" width="1" height="1"/>
	<rect x="5" y="5" fill="#DA2934" width="1" height="1"/>
	<rect x="6" y="4" fill="#F92F3C" width="1" height="1"/>
	<rect x="7" y="4" fill="#F92F3C" width="1" height="1"/>
	<rect x="6" y="5" fill="#F92F3C" width="1" height="1"/>
	<rect x="2" y="6" fill="#F92F3C" width="1" height="1"/>
	<rect x="3" y="6" fill="#DA2934" width="1" height="1"/>
	<rect x="2" y="7" fill="#F92F3C" width="1" height="1"/>
	<rect x="3" y="7" fill="#F92F3C" width="1" height="1"/>
	<rect x="4" y="6" fill="#F92F3C" width="1" height="1"/>
	<rect x="5" y="6" fill="#DA2934" width="1" height="1"/>
	<rect x="4" y="7" fill="#F92F3C" width="1" height="1"/>
	<rect x="5" y="7" fill="#F92F3C" width="1" height="1"/>
	<rect x="6" y="6" fill="#F92F3C" width="1" height="1"/>
	<rect x="6" y="7" fill="#F92F3C" width="1" height="1"/>
	<rect x="7" y="5" fill="#F92F3C" width="1" height="1"/>
	<rect x="2" y="3" fill="#9C5F00" width="1" height="1"/>
	<rect x="3" y="2" fill="#9C5F00" width="1" height="1"/>
	<rect x="5" y="2" fill="#9C5F00" width="1" height="1"/>
	<rect x="6" y="3" fill="#9C5F00" width="1" height="1"/>
</g>
</svg>
```

It will then optimise it to:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9">
	<path fill="#F92F3C" d="M1,4V6H2V8H7V6H8V4z M3,5H4V7H3z M5,5H6V7H5z"/>
	<rect fill="#DA2934" x="3" y="5" width="1" height="2"/>
	<rect fill="#DA2934" x="5" y="5" width="1" height="2"/>
	<rect fill="#9C5F00" x="3" y="2" width="1" height="1"/>
	<rect fill="#9C5F00" x="5" y="2" width="1" height="1"/>
	<rect fill="#9C5F00" x="2" y="3" width="1" height="1"/>
	<rect fill="#9C5F00" x="6" y="3" width="1" height="1"/>
</svg>
```

To use it, simply run: `python optimise-pixels.py path-to-file.svg`

Here's a [demo](https://sqkhor.com/pixel-icons/optimise/) of the PHP port. You could drag and drop `example/before.svg` to get an idea.
