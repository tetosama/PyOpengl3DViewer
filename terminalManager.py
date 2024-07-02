"""
This file contains the TerminalManager class, which is responsible for managing the terminal interface.
"""

from instances import Instances
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import print_formatted_text
from queue import Queue
from threading import Thread
import time
import asyncio

class TerminalManager:
    def __init__(self):
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.loop = asyncio.new_event_loop()

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.start_routine())
        self.loop.run_forever()


    async def start_routine(self):
        with patch_stdout():
            background_task = self.loop.create_task(self.print_output())
            try:
                await self.interactive_shell()
            finally:
                self.loop.stop()

    def tprint(self, s):
        self.output_queue.put(s)

    async def interactive_shell(self):
        session = PromptSession("Command: ")

        # Run echo loop. Read text from stdin, and reply it back.
        while True:
            try:
                result = await session.prompt_async()
                Instances.input_handler_instance.command(result)
            except (EOFError, KeyboardInterrupt):
                return

    async def print_output(self):
        """
        Coroutine that prints counters.
        """
        try:
            while True:
                if not self.output_queue.empty():
                    message = self.output_queue.get()
                    print_formatted_text(message)
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            print("Background task cancelled.")