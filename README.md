# qemu-scanout-diff

Capture, analyze, and compare raw framebuffer scanouts from QEMU or other emulators.

The tool reports deterministic regression metrics:

- SHA-256
- non-black pixel count
- changed byte count
- changed pixel count
- changed bounding box
- PNG previews
- high-contrast diff images

It can also send QEMU HMP pmemsave commands over a TCP monitor.

## Install

~~~bash
pip install .
~~~

## Analyze a frame

~~~bash
qemu-scanout analyze frame.rgba --width 1280 --height 720 --png frame.png
~~~

## Compare two frames

~~~bash
qemu-scanout compare before.rgba after.rgba \
  --width 1280 --height 720 --output-dir comparison
~~~

The output directory contains before.png, after.png, diff.png, and result.json.

## Capture through a QEMU TCP monitor

Start QEMU with an HMP monitor:

~~~bash
-monitor tcp:127.0.0.1:4444,server=on,wait=off
~~~

Then capture a known physical framebuffer range:

~~~bash
qemu-scanout capture frame.rgba \
  --address 0x70000000 \
  --width 1280 --height 720 --channels 4 \
  --host 127.0.0.1 --port 4444
~~~

The address and dimensions are examples only. Use values appropriate for your guest.

## Metric semantics

- **non-black pixels**: pixels whose RGB channels are not all zero; alpha alone does not count.
- **changed bytes**: individual channel bytes that differ.
- **changed pixels**: pixels with at least one changed channel.
- **changed bounding box**: inclusive min_x/min_y/max_x/max_y coordinates.

## Development

~~~bash
python -m unittest discover -s tests -v
~~~

## Data safety

Do not publish proprietary framebuffer captures, firmware memory dumps, credentials, or private assets in issues or test fixtures.

## License

MIT
