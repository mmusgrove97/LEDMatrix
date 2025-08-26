import os
import time
import logging
from datetime import datetime
import pytz
from typing import Dict, Any, Optional
from src.config_manager import ConfigManager
from src.display_manager import DisplayManager
from PIL import Image, ImageDraw

# Get logger without configuring
logger = logging.getLogger(__name__)

class Clock:
    def __init__(self, display_manager: DisplayManager = None):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

        self.clock_dir = "/home/piscreen/LED_Matrix/assets/clock"
        self.display_width = 128
        self.display_height = 32

        # Use the provided display_manager or create a new one if none provided
        self.display_manager = display_manager or DisplayManager(self.config.get('display', {}))
        logger.info("Clock initialized with display_manager: %s", id(self.display_manager))
        self.location = self.config.get('location', {})
        self.clock_config = self.config.get('clock', {})
        # Use configured timezone if available, otherwise try to determine it
        self.timezone = self._get_timezone()
        self.last_time = None
        self.last_date = None

        self._digit_cache = {}

        # Colors for different elements - using super bright colors
        self.COLORS = {
            'time': (255, 255, 255),    # Pure white for time
            'ampm': (255, 255, 128),    # Bright warm yellow for AM/PM
            'date': (255, 100, 0)      # Bright orange for date
        }

        self.NUMBER_IMAGES = [
            "digit0.png",
            "digit1.png",
            "digit2.png",
            "digit3.png",
            "digit4.png",
            "digit5.png",
            "digit6.png",
            "digit7.png",
            "digit8.png",
            "digit9.png",
            "digit10s.png"
        ]

        self.BLANK_NUMS = [
            "blank1s.png",
            "blank10s.png"
        ]

        # have one easy reference for offsets, width of each digit picture is static
        self.X_OFFSET_TIME = 1
        self.Y_OFFSET_TIME = 0
        self.X_OFFSET_TEN_HR = 8 
        self.X_OFFSET_FULL_DIGITS = 25
        self.X_OFFSET_DECIMAL_SEPARATOR = 14

        # set up slots for each digit picture to be displayed in
        self.HOUR_TENS_X = self.X_OFFSET_TIME
        self.HOUR_TENS_Y = self.Y_OFFSET_TIME
        self.HOUR_ONES_X = self.HOUR_TENS_X + self.X_OFFSET_TEN_HR
        self.HOUR_ONES_Y = self.Y_OFFSET_TIME
        self.TIME_SEPARATOR_X = self.HOUR_ONES_X + self.X_OFFSET_FULL_DIGITS
        self.TIME_SEPARATOR_Y = self.Y_OFFSET_TIME
        self.MINUTE_TENS_X = self.TIME_SEPARATOR_X + self.X_OFFSET_DECIMAL_SEPARATOR
        self.MINUTE_TENS_Y = self.Y_OFFSET_TIME
        self.MINUTE_ONES_X = self.MINUTE_TENS_X + self.X_OFFSET_FULL_DIGITS
        self.MINUTE_ONES_Y = self.Y_OFFSET_TIME
        self.AM_PM_X = self.MINUTE_ONES_X + self.X_OFFSET_FULL_DIGITS
        self.AM_PM_Y = self.Y_OFFSET_TIME

    def _get_timezone(self) -> pytz.timezone:
        """Get timezone from the config file."""
        config_timezone = self.config_manager.get_timezone()
        try:
            return pytz.timezone(config_timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(
                f"Invalid timezone '{config_timezone}' in config. "
                "Falling back to UTC. Please check your config.json file. "
                "A list of valid timezones can be found at "
                "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
            )
            return pytz.utc

    def _get_ordinal_suffix(self, day: int) -> str:
        """Get the ordinal suffix for a day number (1st, 2nd, 3rd, etc.)."""
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return suffix

    def get_current_time(self) -> tuple:
        """Get the current time and date in the configured timezone."""
        current = datetime.now(self.timezone)
        
        # Format time in 12-hour format with AM/PM
        time_str = current.strftime('%-I:%M') 
        
        # Get AM/PM
        ampm = current.strftime('%p')
        
        # # Format date with ordinal suffix - split into two lines
        # day_suffix = self._get_ordinal_suffix(current.day)
        # Full weekday on first line, full month and day on second line
        weekday = current.strftime('%A')
        date_str = current.strftime(f'%b %-d')
        
        return time_str, ampm, weekday, date_str

    def display_time_text(self, force_clear: bool = False) -> None:
        """Display the current time and date."""
        time_str, ampm, weekday, date_str = self.get_current_time()
        
        # Only update if something has changed
        if time_str != self.last_time or date_str != self.last_date or force_clear:
            # Clear the display
            self.display_manager.clear()
            
            # Calculate positions
            display_width = self.display_manager.matrix.width
            display_height = self.display_manager.matrix.height
            
            # Draw time (large, centered, near top)
            self.display_manager.draw_text(
                time_str,
                y=4,  # Move up slightly to make room for two lines of date
                color=self.COLORS['time'],
                small_font=True
            )
            
            # Draw AM/PM (small, next to time)
            time_width = self.display_manager.font.getlength(time_str)
            ampm_x = (display_width + time_width) // 2 + 4
            self.display_manager.draw_text(
                ampm,
                x=ampm_x,
                y=4,  # Align with time
                color=self.COLORS['ampm'],
                small_font=True
            )
            
            # Draw weekday on first line (small font)
            self.display_manager.draw_text(
                weekday,
                y=display_height - 18,  # First line of date
                color=self.COLORS['date'],
                small_font=True
            )
            
            # Draw month and day on second line (small font)
            self.display_manager.draw_text(
                date_str,
                y=display_height - 9,  # Second line of date
                color=self.COLORS['date'],
                small_font=True
            )
            
            # Update the display after drawing everything
            self.display_manager.update_display()
            
            # Update cache
            self.last_time = time_str
            self.last_date = date_str

    def time_str_to_decimal(self, time_str) -> tuple:
        if time_str is None:
            return -1, -1, -1, -1 # return default value if initial time check

        fields = time_str.split(":")
        hour = int(fields[0]) if len(fields) > 0 else 0
        minute = int(fields[1]) if len(fields) > 1 else 0

        # return 10s and 1s place for hours and minutes
        hour_tens = hour // 10
        hour_ones = hour % 10
        minute_tens = minute // 10
        minute_ones = minute % 10
        return hour_tens, hour_ones, minute_tens, minute_ones
    
    def _load_clock_image(self, digit_str: str) -> Optional[Image.Image]:
        if digit_str in self._digit_cache:
            return self._digit_cache[digit_str]

        digit_path = os.path.join(self.clock_dir, f"{digit_str}")

        print(f"Digit Path: {digit_path}")

        try:
            digit = Image.open(digit_path)
            if digit.mode != 'RGBA':
                digit = digit.convert('RGBA')

            max_width = int(self.display_width)
            max_height = int(self.display_height)
            digit.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            self._digit_cache[digit_str] = digit

        except Exception as e:
            self.logger.error(f"Error loading digit {digit_str}: {e}", exc_info=True)
            return None

    def display_time_enhanced(self, force_clear: bool = False) -> None:
        """Display the current time and date."""
        time_str, ampm, weekday, date_str = self.get_current_time()

        # Only update if something has changed
        if time_str != self.last_time or date_str != self.last_date or force_clear:
            main_img = Image.new('RGBA', (self.display_width, self.display_height), (0, 0, 0, 255))
            overlay = Image.new('RGBA', (self.display_width, self.display_height), (0, 0, 0, 0))

            time_separator = self._load_clock_image("timeseparator.png")
            overlay.paste(time_separator, (self.TIME_SEPARATOR_X, self.TIME_SEPARATOR_Y), time_separator)

            if ampm.upper() == "AM":
                ampm_img = self._load_clock_image("am.png")
            else:
                ampm_img = self._load_clock_image("pm.png")
            
            overlay.paste(ampm_img, (self.AM_PM_X, self.AM_PM_Y), ampm_img)

            # Calculate positions
            display_width = self.display_manager.matrix.width
            display_height = self.display_manager.matrix.height
            print(f"\nDisplay Height: {display_height}, Display Width: {display_width}")

            # Break down time_str into hours and minutes to get correct images
            new_hour_tens, new_hour_ones, new_minute_tens, new_minute_ones = self.time_str_to_decimal(time_str)
            print(f"\nCurrent Time: {time_str}, Hour: {new_hour_tens*10 + new_hour_ones}, Minute: {new_minute_tens*10 + new_minute_ones}")

            # Break down last_time into hours and minutes to see what needs to be updated
            old_hour_tens, old_hour_ones, old_minute_tens, old_minute_ones = self.time_str_to_decimal(self.last_time)

            hour_tens_updated = (new_hour_tens != old_hour_tens)
            hour_ones_updated = (new_hour_ones != old_hour_ones)
            minute_tens_updated = (new_minute_tens != old_minute_tens)
            minute_ones_updated = (new_minute_ones != old_minute_ones)

            # Clear any updated values
            if hour_tens_updated:
                blank_tens = self._load_clock_image(self.BLANK_NUMS[1])
                main_img.paste(blank_tens, (self.HOUR_TENS_X, self.HOUR_TENS_Y), blank_tens)
            if hour_ones_updated:
                blank_ones = self._load_clock_image(self.BLANK_NUMS[0])
                main_img.paste(blank_ones, (self.HOUR_ONES_X, self.HOUR_ONES_Y), blank_ones)   
            if minute_tens_updated:
                blank_ones = self._load_clock_image(self.BLANK_NUMS[0])
                main_img.paste(blank_ones, (self.MINUTE_TENS_X, self.MINUTE_TENS_Y), blank_ones)     
            if minute_ones_updated:
                blank_ones = self._load_clock_image(self.BLANK_NUMS[0])
                main_img.paste(blank_ones, (self.MINUTE_ONES_X, self.MINUTE_ONES_Y), blank_ones)  

            # Composite and display
            main_img = Image.alpha_composite(main_img, overlay)
            main_img = main_img.convert('RGB')

            # Update image to clear any updated compontents
            self.display_manager.image.paste(main_img, (0, 0))
            self.display_manager.update_display()

            # Update digit image if necessary
            if hour_tens_updated and new_hour_tens > 0:
                hour_tens = self._load_clock_image(self.NUMBER_IMAGES[10])
                main_img.paste(hour_tens, (self.HOUR_TENS_X, self.HOUR_TENS_Y), hour_tens)
            elif new_hour_tens > 0:
                hour_tens = self._load_clock_image(self.NUMBER_IMAGES[10])
                main_img.paste(hour_tens, (self.HOUR_TENS_X, self.HOUR_TENS_Y), hour_tens)      
          
            if hour_ones_updated:
                hour_ones = self._load_clock_image(self.NUMBER_IMAGES[new_hour_ones])
                main_img.paste(hour_ones, (self.HOUR_ONES_X, self.HOUR_ONES_Y), hour_ones)
            else:
                hour_ones = self._load_clock_image(self.NUMBER_IMAGES[old_hour_ones])
                main_img.paste(hour_ones, (self.HOUR_ONES_X, self.HOUR_ONES_Y), hour_ones)

            if minute_tens_updated:
                minute_tens = self._load_clock_image(self.NUMBER_IMAGES[new_minute_tens])
                main_img.paste(minute_tens, (self.MINUTE_TENS_X, self.MINUTE_TENS_Y), minute_tens)
            else:
                minute_tens = self._load_clock_image(self.NUMBER_IMAGES[old_minute_tens])
                main_img.paste(minute_tens, (self.MINUTE_TENS_X, self.MINUTE_TENS_Y), minute_tens) 

            if minute_ones_updated:
                minute_ones = self._load_clock_image(self.NUMBER_IMAGES[new_minute_ones])
                main_img.paste(minute_ones, (self.MINUTE_ONES_X, self.MINUTE_ONES_Y), minute_ones)
            else:
                minute_ones = self._load_clock_image(self.NUMBER_IMAGES[old_minute_ones])
                main_img.paste(minute_ones, (self.MINUTE_ONES_X, self.MINUTE_ONES_Y), minute_ones)

            main_img = main_img.convert('RGB') # Convert for display
            
            # Update image to clear any updated compontents
            self.display_manager.image.paste(main_img, (0, 0))
            self.display_manager.update_display()

            # Update cache
            self.last_time = time_str
            self.last_date = date_str

if __name__ == "__main__":
    clock = Clock()
    try:
        while True:
            clock.display_time_enhanced()
            time.sleep(clock.clock_config.get('update_interval', 1))
    except KeyboardInterrupt:
        print("\nClock stopped by user")
    finally:
        clock.display_manager.cleanup() 