# Source: https://github.com/HumanCellAtlas/status-api/blob/37af34c6b35d6c280a80df25507cbadd7ec3234e/svgs.py
# Author: Matt Weiden
#
# MIT License
#
# Copyright (c) 2018 Human Cell Atlas
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import datetime

SERVICE_OK = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="72" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="72" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h49v20H0z"/><path fill="#4c1" d="M49 0h23v20H49z"/><path fill="url(#b)" d="M0 0h72v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="255" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="390">service</text><text x="255" y="140" transform="scale(.1)" textLength="390">service</text><text x="595" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="130">ok</text><text x="595" y="140" transform="scale(.1)" textLength="130">ok</text></g> </svg>
"""

SERVICE_ERROR = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="86" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="86" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h49v20H0z"/><path fill="#e05d44" d="M49 0h37v20H49z"/><path fill="url(#b)" d="M0 0h86v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="255" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="390">service</text><text x="255" y="140" transform="scale(.1)" textLength="390">service</text><text x="665" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="270">error</text><text x="665" y="140" transform="scale(.1)" textLength="270">error</text></g> </svg>
"""

SERVICE_UNKNOWN = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="110" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="110" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h49v20H0z"/><path fill="#9f9f9f" d="M49 0h61v20H49z"/><path fill="url(#b)" d="M0 0h110v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="255" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="390">service</text><text x="255" y="140" transform="scale(.1)" textLength="390">service</text><text x="785" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">unknown</text><text x="785" y="140" transform="scale(.1)" textLength="510">unknown</text></g> </svg>
"""

PIPELINE_UNKNOWN = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="114" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="114" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h53v20H0z"/><path fill="#9f9f9f" d="M53 0h61v20H53z"/><path fill="url(#b)" d="M0 0h114v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="275" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="430">pipeline</text><text x="275" y="140" transform="scale(.1)" textLength="430">pipeline</text><text x="825" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">unknown</text><text x="825" y="140" transform="scale(.1)" textLength="510">unknown</text></g> </svg>
"""

AVAILABILITY_TEMPLATE = """<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="132" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="132" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h69v20H0z"/>
    <path fill="{}" d="M69 0h63v20H69z"/>
    <path fill="url(#b)" d="M0 0h132v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
    <text x="355" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="590">availability</text>
    <text x="355" y="140" transform="scale(.1)" textLength="590">availability</text>
    <text x="995" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">{}</text>
    <text x="995" y="140" transform="scale(.1)" textLength="530">{}</text>
  </g>
</svg>"""

LAST_UPDATED_TEMPLATE = """<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="230" height="20">
  <linearGradient id="b" x2="230" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="250" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h69v20H0z"/>
    <path fill="{}" d="M69 0h161v20H69z"/>
    <path fill="url(#b)" d="M0 0h132v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
    <text x="355" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="590">last updated</text>
    <text x="355" y="140" transform="scale(.1)" textLength="590">last updated</text>
    <text x="1500" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="1530">{}</text>
    <text x="1500" y="140" transform="scale(.1)" textLength="1530">{}</text>
  </g>
</svg>"""


def make_availability_svg(color_name, availability=None):
    text = 'unknown'
    if availability:
        text = "%0.04f" % availability
    color = {
        'lightgrey': '#9f9f9f',
        'brightgreen': '#4c1',
        'yellow': '#dfb317',
        'red': '#e05d44'
    }[color_name]
    return AVAILABILITY_TEMPLATE.format(color, text, text)


def make_last_updated_svg():
    text = datetime.datetime.now().strftime("%c %Z")
    return LAST_UPDATED_TEMPLATE.format('#9f9f9f', text, text)
