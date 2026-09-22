import socket
import threading
import unittest

from qemu_scanout_diff.hmp import run_hmp_command


class HmpTests(unittest.TestCase):
    def test_waits_for_command_response_not_initial_prompt(self):
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        received = []

        def server():
            connection, _ = listener.accept()
            with connection:
                connection.sendall(b"QEMU monitor\r\n(qemu) ")
                received.append(connection.recv(1024))
                connection.sendall(b"command complete\r\n(qemu) ")
            listener.close()

        thread = threading.Thread(target=server, daemon=True)
        thread.start()
        response = run_hmp_command("info status", port=port, timeout=2.0)
        thread.join(timeout=2.0)

        self.assertEqual(received, [b"info status\n"])
        self.assertIn("command complete", response)


if __name__ == "__main__":
    unittest.main()
