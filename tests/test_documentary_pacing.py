import unittest
from tools.documentary_pacing import add_pauses, pause_centers


class DocumentaryPacingTests(unittest.TestCase):
    def test_silence_not_in_intro(self):
        text = (
            "silence_start: 0\nsilence_end: 0.20 | silence_duration: 0.20\n"
            "silence_start: 2.6\nsilence_end: 2.95 | silence_duration: 0.35\n"
            "silence_start: 4\nsilence_end: 4.18 | silence_duration: 0.18\n")
        self.assertEqual([round(x, 3) for x in pause_centers(text)], [2.775])

    def test_only_pauses_are_added(self):
        pcm = b"abcdef"
        self.assertEqual(add_pauses(pcm, 10, 1, [.3], .2),
                         b"abc" + bytes(2) + b"def")
        self.assertEqual(add_pauses(pcm, 10, 1, [], .2), pcm)
