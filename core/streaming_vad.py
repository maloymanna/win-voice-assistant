# Version: v1.0.0
# Minimal ctypes wrapper for parakeet.cpp streaming VAD C API.
# Falls back gracefully if the shared library or symbols are missing.

import ctypes
import ctypes.util
import os


class StreamingVAD:

    def __init__(self, lib_path, vad_model_path):
        self._lib = None
        self._ctx = None
        self._speaking = False
        self._silence_frames = 0
        self._frame_sec = 0.032
        self._min_pause_frames = 3  # will be set by set_min_pause

        if not os.path.isfile(lib_path):
            print(f"VAD LIB NOT FOUND: {lib_path}")
            return

        try:
            self._lib = ctypes.CDLL(lib_path)
        except OSError as e:
            print(f"VAD LIB LOAD FAILED: {e}")
            return

        # The exact symbol names depend on the built DLL.
        # Common pattern from parakeet.cpp C API:
        #   parakeet_capi_vad_stream_create(model, ctx*)
        #   parakeet_capi_vad_stream_feed(ctx, pcm*, n, event_out*)
        #   parakeet_capi_vad_stream_free(ctx)
        # Adjust below if your DLL exports different names.
        try:
            self._create = self._lib.parakeet_capi_vad_stream_create
            self._create.restype = ctypes.c_void_p
            self._create.argtypes = [ctypes.c_char_p, ctypes.c_void_p]

            self._feed = self._lib.parakeet_capi_vad_stream_feed
            self._feed.restype = ctypes.c_int
            self._feed.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                   ctypes.c_size_t, ctypes.POINTER(ctypes.c_int)]

            self._free = self._lib.parakeet_capi_vad_stream_free
            self._free.restype = None
            self._free.argtypes = [ctypes.c_void_p]
        except AttributeError as e:
            print(f"VAD SYMBOL MISSING: {e}")
            self._lib = None
            return

        model_bytes = vad_model_path.encode("utf-8")
        self._ctx = self._create(model_bytes, None)

        if not self._ctx:
            print(f"VAD CREATE FAILED for {vad_model_path}")
            self._lib = None

    def available(self):
        return self._ctx is not None

    def set_min_pause(self, seconds):
        # 32 ms frame -> frames needed for the configured pause
        self._min_pause_frames = max(1, int(seconds / self._frame_sec))

    def feed(self, pcm_bytes):
        # Returns (speech_started, speech_ended)
        if not self.available():
            return False, False

        buf = ctypes.create_string_buffer(pcm_bytes)
        event = ctypes.c_int(0)

        self._feed(
            self._ctx,
            buf,
            len(pcm_bytes),
            ctypes.byref(event)
        )

        # Event bitmask is implementation-specific.
        # Convention used here:
        #   bit 0 = speech start, bit 1 = speech end
        started = bool(event.value & 1)
        ended = bool(event.value & 2)

        return started, ended

    def close(self):
        if self._ctx and self._lib:
            self._free(self._ctx)
            self._ctx = None