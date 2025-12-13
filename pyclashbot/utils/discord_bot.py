"""Discord bot integration for py-clash-bot with slash commands and embeds.

Note: For optional opening of ports, you can honestly open up a port like this:
    # Actually, Discord bots connect outbound to Discord's servers via WebSocket.
    # No port forwarding, firewall rules, or "setting up all this stuff" needed.
    # Discord.py handles the connection automatically. But hey, if you want to check
    # what ports are listening, you could run: netstat -an | findstr LISTENING
    # ¯\\_(ツ)_/¯
"""

from __future__ import annotations

import asyncio
import io
import threading
from typing import TYPE_CHECKING, Any

import cv2
import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from pyclashbot.bot.worker import WorkerProcess
    from pyclashbot.utils.logger import Logger


class DiscordBotManager:
    """Manages Discord bot lifecycle and commands."""

    def __init__(self, logger: Logger | None = None) -> None:
        self.bot: commands.Bot | None = None
        self.logger = logger
        self.worker_process: WorkerProcess | None = None
        self.emulator_controller: Any = None
        self.emulator_type: str | None = None
        self.emulator_serial: str | None = None
        self.stats: dict[str, Any] = {}
        self.is_running = False
        self.bot_thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self.live_tasks: dict[int, asyncio.Task] = {}  # channel_id -> task
        self.last_trophies: int | None = None
        self.last_crowns: tuple[int, int] | None = None  # (friendly, enemy)

    def start_bot(self, token: str, logger: Logger | None = None) -> bool:
        """Start the Discord bot in a separate thread."""
        if self.is_running:
            return False

        if logger:
            self.logger = logger

        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)

        # Register slash commands
        self._register_commands()

        # Start bot in a new thread
        def run_bot():
            asyncio.set_event_loop(asyncio.new_event_loop())
            self._loop = asyncio.get_event_loop()
            try:
                self._loop.run_until_complete(self.bot.start(token))
            except Exception as e:
                if self.logger:
                    self.logger.log(f"Discord bot error: {e}")

        self.bot_thread = threading.Thread(target=run_bot, daemon=True)
        self.bot_thread.start()
        self.is_running = True
        return True

    def stop_bot(self) -> None:
        """Stop the Discord bot."""
        if not self.is_running or not self.bot:
            return

        async def close_bot():
            if self.bot:
                await self.bot.close()

        if self._loop and not self._loop.is_closed():
            asyncio.run_coroutine_threadsafe(close_bot(), self._loop)

        self.is_running = False
        self.bot = None

    def update_stats(self, stats: dict[str, Any]) -> None:
        """Update the current bot statistics."""
        self.stats = stats.copy()

    def set_worker_process(self, process: WorkerProcess | None) -> None:
        """Set the worker process reference."""
        self.worker_process = process

    def set_emulator_controller(self, controller: Any) -> None:
        """Set the emulator controller reference."""
        self.emulator_controller = controller

    def set_emulator_info(self, emulator_type: str | None, serial: str | None = None) -> None:
        """Set emulator type and serial for screenshot access."""
        self.emulator_type = emulator_type
        self.emulator_serial = serial

    def _get_screenshot_controller(self) -> Any:
        """Get or create an emulator controller for screenshots."""
        if self.emulator_controller:
            return self.emulator_controller

        # Try to create a temporary controller for screenshots
        if not self.emulator_type:
            return None

        try:
            from pyclashbot.emulators import EmulatorType, get_emulator_registry

            registry = get_emulator_registry()
            if self.emulator_type not in registry:
                return None

            controller_class = registry[self.emulator_type]

            # Create a minimal logger if none exists
            if not self.logger:
                from pyclashbot.utils.logger import Logger

                temp_logger = Logger(timed=False)
            else:
                temp_logger = self.logger

            if self.emulator_type == EmulatorType.ADB:
                return controller_class(logger=temp_logger, device_serial=self.emulator_serial)
            elif self.emulator_type == EmulatorType.GOOGLE_PLAY:
                return controller_class(logger=temp_logger)
            elif self.emulator_type == EmulatorType.BLUESTACKS:
                return controller_class(logger=temp_logger)
            elif self.emulator_type == EmulatorType.MEMU:
                return controller_class(temp_logger, "opengl")

        except Exception as e:
            if self.logger:
                self.logger.log(f"Failed to create screenshot controller: {e}")
            return None

        return None

    def _register_commands(self) -> None:
        """Register all slash commands."""

        @self.bot.event
        async def on_ready():
            if self.logger:
                self.logger.log(f"Discord bot logged in as {self.bot.user}")

            # Sync commands
            try:
                synced = await self.bot.tree.sync()
                if self.logger:
                    self.logger.log(f"Synced {len(synced)} command(s)")
            except Exception as e:
                if self.logger:
                    self.logger.log(f"Failed to sync commands: {e}")

        @self.bot.event
        async def on_error(event: str, *args: Any, **kwargs: Any) -> None:
            if self.logger:
                import traceback

                self.logger.log(f"Discord bot error in {event}: {traceback.format_exc()}")

        @self.bot.tree.command(name="stats", description="check bot stats")
        async def stats_command(interaction: discord.Interaction):
            """show bot stats"""
            embed = self._create_stats_embed()
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="screenshot", description="grab a screenshot")
        async def screenshot_command(interaction: discord.Interaction):
            """take a screenshot"""
            await interaction.response.defer()

            controller = self._get_screenshot_controller()
            if not controller:
                await interaction.followup.send("no emulator connected, start the bot first", ephemeral=True)
                return

            try:
                screenshot = controller.screenshot()
                if screenshot is None or screenshot.size == 0:
                    raise ValueError("screenshot is empty")

                # Convert numpy array to PNG bytes
                _, buffer = cv2.imencode(".png", screenshot)
                image_bytes = io.BytesIO(buffer.tobytes())

                embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
                embed.set_image(url="attachment://screenshot.png")

                file = discord.File(image_bytes, filename="screenshot.png")
                await interaction.followup.send(embed=embed, file=file)

                # Clean up temporary controller if we created one
                if controller != self.emulator_controller:
                    try:
                        controller.stop()
                    except Exception:
                        pass

            except Exception as e:
                await interaction.followup.send(f"failed to take screenshot: {e!s}", ephemeral=True)

        @self.bot.tree.command(name="status", description="check bot status")
        async def status_command(interaction: discord.Interaction):
            """show bot status"""
            is_running = self.worker_process and self.worker_process.is_alive()
            status_text = "running" if is_running else "idle"
            current_status = self.stats.get("current_status", "idle")

            embed = discord.Embed(
                color=discord.Color.green() if is_running else discord.Color.red(),
                timestamp=discord.utils.utcnow(),
            )
            embed.add_field(name="status", value=status_text, inline=True)
            embed.add_field(name="activity", value=current_status, inline=True)
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="help", description="show commands")
        async def help_command(interaction: discord.Interaction):
            """show help"""
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name="/stats", value="bot stats (wins, losses, etc)", inline=False)
            embed.add_field(name="/screenshot", value="grab a screenshot", inline=False)
            embed.add_field(name="/status", value="check if bot is running", inline=False)
            embed.add_field(
                name="/live",
                value="start live feed (screenshots every 5s). optional: channel id",
                inline=False,
            )
            embed.add_field(name="/stop", value="stop live feed", inline=False)
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="live", description="start live feed")
        @app_commands.describe(channel="optional channel id to send to")
        async def live_command(interaction: discord.Interaction, channel: discord.TextChannel | None = None):
            """start live screenshot feed"""
            channel_id = channel.id if channel else interaction.channel_id
            if channel_id is None:
                await interaction.response.send_message("couldn't get channel id", ephemeral=True)
                return

            # Check if already running
            if channel_id in self.live_tasks:
                await interaction.response.send_message("live feed already running in this channel", ephemeral=True)
                return

            controller = self._get_screenshot_controller()
            if not controller:
                await interaction.response.send_message("no emulator connected, start the bot first", ephemeral=True)
                return

            await interaction.response.send_message(f"starting live feed in <#{channel_id}>")

            # Start live task
            task = asyncio.create_task(self._live_feed_loop(channel_id, controller))
            self.live_tasks[channel_id] = task

        @self.bot.tree.command(name="stop", description="stop live feed")
        async def stop_command(interaction: discord.Interaction):
            """stop live feed"""
            channel_id = interaction.channel_id
            if channel_id not in self.live_tasks:
                await interaction.response.send_message("no live feed running here", ephemeral=True)
                return

            task = self.live_tasks.pop(channel_id)
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await interaction.response.send_message("stopped live feed")

    async def _live_feed_loop(self, channel_id: int, controller: Any) -> None:
        """Background task that sends screenshots every 5 seconds."""
        channel = self.bot.get_channel(channel_id) if self.bot else None
        if not channel:
            return

        temp_controller = controller != self.emulator_controller
        last_trophies = None
        last_crowns = None

        try:
            while True:
                await asyncio.sleep(5)

                try:
                    screenshot = controller.screenshot()
                    if screenshot is None or screenshot.size == 0:
                        continue

                    # Detect trophies and crowns
                    trophies = self._detect_trophies(screenshot)
                    crowns = self._detect_crowns(screenshot)

                    # Convert to PNG
                    _, buffer = cv2.imencode(".png", screenshot)
                    image_bytes = io.BytesIO(buffer.tobytes())

                    # Build message
                    message_parts = []
                    if trophies is not None and trophies != last_trophies:
                        message_parts.append(f"🏆 trophies: {trophies}")
                        last_trophies = trophies

                    if crowns is not None and crowns != last_crowns:
                        friendly, enemy = crowns
                        message_parts.append(f"👑 crowns: {friendly} - {enemy}")
                        last_crowns = crowns

                    # Send screenshot
                    embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
                    if message_parts:
                        embed.description = "\n".join(message_parts)
                    embed.set_image(url="attachment://screenshot.png")

                    file = discord.File(image_bytes, filename="screenshot.png")
                    await channel.send(embed=embed, file=file)

                except Exception as e:
                    if self.logger:
                        self.logger.log(f"live feed error: {e}")
                    await asyncio.sleep(5)

        except asyncio.CancelledError:
            pass
        finally:
            if temp_controller:
                try:
                    controller.stop()
                except Exception:
                    pass
            self.live_tasks.pop(channel_id, None)

    def _detect_trophies(self, screenshot: Any) -> int | None:
        """Try to detect trophy count from screenshot."""
        try:
            # Trophy count is usually displayed in top-left area around (100, 50) region
            # Look for bright yellow/gold numbers on dark background
            # This is a simplified detection - checks for trophy-like colors in the region
            h, w = screenshot.shape[:2]
            if h < 100 or w < 200:
                return None

            # Check trophy area (top-left where trophy count shows)
            # For now return None - actual OCR would be needed for accurate detection
            # This is a placeholder that can be enhanced with pytesseract or template matching
            return None
        except Exception:
            return None

    def _detect_crowns(self, screenshot: Any) -> tuple[int, int] | None:
        """Try to detect crown counts from screenshot."""
        try:
            # Crowns are shown on end-battle screen
            # Usually displayed around center-bottom area
            h, w = screenshot.shape[:2]
            if h < 400 or w < 300:
                return None

            # Check if we're on end-battle screen by looking for crown-like colors
            # For now return None - actual detection would need template matching or OCR
            # This is a placeholder
            return None
        except Exception:
            return None

    def _create_stats_embed(self) -> discord.Embed:
        """Create a stats embed from current statistics."""
        wins = int(self.stats.get("wins", 0) or 0)
        losses = int(self.stats.get("losses", 0) or 0)
        winrate = str(self.stats.get("winrate", "0%") or "0%")
        current_status = str(self.stats.get("current_status", "idle") or "idle")

        total_battles = wins + losses
        winrate_value = float(winrate.rstrip("%")) if winrate.endswith("%") else 0.0

        embed = discord.Embed(
            color=discord.Color.green() if winrate_value >= 50 else discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )

        embed.add_field(name="wins", value=str(wins), inline=True)
        embed.add_field(name="losses", value=str(losses), inline=True)
        embed.add_field(name="winrate", value=winrate, inline=True)
        embed.add_field(name="total battles", value=str(total_battles), inline=True)

        cards_collected = self.stats.get("cards_collected", 0)
        gold_collected = self.stats.get("gold_collected", 0)
        if cards_collected:
            embed.add_field(name="cards", value=str(cards_collected), inline=True)
        if gold_collected:
            embed.add_field(name="gold", value=str(gold_collected), inline=True)

        restarts = self.stats.get("restarts_after_failure", 0)
        time_since_start = self.stats.get("time_since_start", "00:00:00")
        embed.add_field(name="restarts", value=str(restarts), inline=True)
        embed.add_field(name="runtime", value=str(time_since_start), inline=True)
        embed.add_field(name="status", value=current_status, inline=False)

        return embed
