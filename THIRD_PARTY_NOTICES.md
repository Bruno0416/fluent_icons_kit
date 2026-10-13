# Third-Party Notices

## Microsoft Fluent UI System Icons

The icon artwork used in Fluent Icons Kit is derived from Microsoft's **Fluent UI System Icons**:

- Source: <https://github.com/microsoft/fluentui-system-icons>
- Original copyright: Copyright (c) 2020 Microsoft Corporation
- License: MIT

The following is the MIT license notice for the upstream artwork:

> MIT License
>
> Copyright (c) 2020 Microsoft Corporation
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

## Modifications

The upstream SVG artwork has been normalized to one design size per icon and
variant, converted into monochrome TrueType glyphs, and exposed through two
native Flutter `IconData` catalogs (`line` and `filled`). Because the selected
design size may vary between icons, results can differ slightly from other
Fluent icon libraries. Transparency, gradients, and multicolor styles are not
preserved in these two fonts.

The package's own source code is licensed separately under the MIT license in
[LICENSE](LICENSE).
