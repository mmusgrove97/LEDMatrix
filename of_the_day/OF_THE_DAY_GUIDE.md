# "Of The Day" Display System Guide

## Overview

The "Of The Day" display system allows you to create multiple daily displays that show different types of content each day. This system is perfect for educational content, inspirational messages, language learning, and more.

## Features

- **Multiple Categories**: Enable multiple "of the day" displays simultaneously
- **Daily Rotation**: Each day shows a different item based on the day of the year
- **Customizable Content**: Create your own categories and content
- **Configurable Display**: Control display duration, update intervals, and more
- **AI-Ready**: Designed to work with LLM AI models for content generation

## Configuration

### Basic Setup

Add the following configuration to your `config/config.json`:

```json
{
    "of_the_day": {
        "enabled": true,
        "update_interval": 3600,
        "subtitle_rotate_interval": 10,         // Seconds to rotate subtitle/description
        "display_rotate_interval": 30,          // Seconds to rotate between categories
        "category_order": ["word_of_the_day", "bible_verse", "spanish_word"],
        "categories": {
            "word_of_the_day": {
                "enabled": true,
                "data_file": "data/word_of_the_day.json",
                "display_name": "Word of the Day"
            },
            "bible_verse": {
                "enabled": true,
                "data_file": "data/bible_verse_of_the_day.json",
                "display_name": "Bible Verse of the Day"
            },
            "spanish_word": {
                "enabled": true,
                "data_file": "data/spanish_word_of_the_day.json",
                "display_name": "Spanish Word of the Day"
            }
        }
    }
}
```

### Configuration Options

- **enabled**: Enable/disable the entire "of the day" system
- **update_interval**: How often to check for updates (in seconds)
- **category_order**: The order in which categories will be displayed
- **categories**: Individual category configurations

### Category Configuration

Each category has these options:

- **enabled**: Enable/disable this specific category
- **data_file**: Path to the JSON data file (relative to project root)
- **display_name**: Human-readable name for the category

### Display Duration

Add the display duration to the `display_durations` section:

```json
"display_durations": {
    "of_the_day": 20
}
```

## Data File Format

Each category uses a JSON file with the following structure:

```json
{
    "1": {
        "title": "SERENDIPITY",
        "subtitle": "A pleasant surprise",
        "description": "The occurrence and development of events by chance in a happy or beneficial way"
    },
    "2": {
        "title": "EPHEMERAL",
        "subtitle": "Short-lived",
        "description": "Lasting for a very short time; transitory"
    }
}
```

### Data File Structure

- **Key**: Day of the year (1-366 for leap years)
- **title**: Main text displayed in bold white font
- **subtitle**: Secondary text displayed in smaller font
- **description**: Longer description (optional, used if subtitle is empty)

## Creating Custom Categories

### Step 1: Create a Data File

Create a new JSON file in the `of_the_day/` directory:

```bash
touch of_the_day/my_custom_category.json
```

### Step 2: Add Content

Add entries for each day of the year (1-366):

```json
{
    "1": {
        "title": "FIRST ITEM",
        "subtitle": "Brief description",
        "description": "Longer explanation if needed"
    },
    "2": {
        "title": "SECOND ITEM",
        "subtitle": "Another description",
        "description": "More details here"
    }
}
```

### Step 3: Update Configuration

Add your category to the config:

```json
{
    "of_the_day": {
        "categories": {
            "my_custom_category": {
                "enabled": true,
                "data_file": "data/my_custom_category.json",
                "display_name": "My Custom Category"
            }
        },
        "category_order": ["word_of_the_day", "my_custom_category"]
    }
}
```

## Using AI to Generate Content

### Example: Word of the Day Generator

You can use an LLM to generate a full year of content. Here's a script example:


    """Generate a full year of word of the day entries using AI."""
    
    words = {}
    
    for day in range(1, 367):
        prompt = f"""
        Generate a word of the day for day {day} of the year.
        Include:
        1. An interesting word (all caps)
        2. A brief subtitle (2-3 words)
        3. A clear definition (1-2 sentences)
        
        Format as JSON:
        {{
            "title": "WORD",
            "subtitle": "Brief description",
            "description": "Full definition"
        }}
        """


## Category Ideas

Here are some ideas for custom categories:

### Educational
- **Vocabulary Word of the Day**: Expand your vocabulary
- **Math Problem of the Day**: Daily math challenges
- **Science Fact of the Day**: Interesting scientific facts
- **History Event of the Day**: Historical events that happened on this date

### Language Learning
- **Spanish Word of the Day**: Learn Spanish vocabulary
- **French Word of the Day**: Learn French vocabulary
- **German Word of the Day**: Learn German vocabulary
- **Japanese Word of the Day**: Learn Japanese vocabulary

### Inspirational
- **Bible Verse of the Day**: Daily scripture
- **Quote of the Day**: Inspirational quotes
- **Affirmation of the Day**: Positive affirmations
- **Meditation of the Day**: Daily meditation prompts

### Professional
- **Programming Tip of the Day**: Daily coding tips
- **Business Quote of the Day**: Business wisdom
- **Leadership Lesson of the Day**: Leadership insights
- **Productivity Tip of the Day**: Daily productivity advice

### Entertainment
- **Movie Quote of the Day**: Famous movie quotes
- **Song Lyric of the Day**: Inspirational song lyrics
- **Joke of the Day**: Daily humor
- **Trivia Question of the Day**: Daily trivia

## Display Layout

The display uses a layout similar to the calendar manager:

- **Title**: Bold white text at the top
- **Subtitle**: Smaller gray text below the title
- **Description**: Wrapped text if subtitle is empty

## Rotation Logic (Subtitle/Description and Category)

There are two types of rotation in the Of The Day display system:

### 1. Subtitle/Description Rotation
- **What:** Within a single "Of The Day" category, the display always shows the Title at the top. Below the title, it alternates between showing the Subtitle and the Description.
- **How:** The Subtitle and Description rotate every `subtitle_rotate_interval` seconds (default: 10 seconds).
- **Example:**
  - 10s: Title + Subtitle
  - 10s: Title + Description
  - 10s: Title + Subtitle
  - ...

### 2. Category Rotation
- **What:** The display can show multiple "Of The Day" categories (e.g., Word of the Day, Slovenian Word of the Day). It rotates between these categories.
- **How:** The currently displayed category switches every `display_rotate_interval` seconds (default: 30 seconds).
- **Example:**
  - 30s: Word of the Day (with subtitle/description alternating every 10s)
  - 30s: Slovenian Word of the Day (with subtitle/description alternating every 10s)
  - ...

### Configuration Example
Add these settings to your `of_the_day` section in `config/config.json`:

```json
"of_the_day": {
  "enabled": true,
  "update_interval": 3600,
  "subtitle_rotate_interval": 10,         // Seconds to rotate subtitle/description
  "display_rotate_interval": 30,          // Seconds to rotate between categories
  "category_order": ["word_of_the_day", "slovenian_word_of_the_day"],
  "categories": {
    "word_of_the_day": {
      "enabled": true,
      "data_file": "word_of_the_day.json"
    },
    "slovenian_word_of_the_day": {
      "enabled": true,
      "data_file": "slovenian_word_of_the_day.json"
    }
  }
}
```

- **subtitle_rotate_interval**: How often (in seconds) to switch between subtitle and description for the current category.
- **display_rotate_interval**: How often (in seconds) to switch to the next category in `category_order`.

#### Example Display Flow
```
[0-10s]   Word of the Day: Title + Subtitle
[10-20s]  Word of the Day: Title + Description
[20-30s]  Word of the Day: Title + Subtitle
[30-40s]  Slovenian Word of the Day: Title + Subtitle
[40-50s]  Slovenian Word of the Day: Title + Description
[50-60s]  Slovenian Word of the Day: Title + Subtitle
...
```

## Troubleshooting

### Common Issues

1. **No content displayed**: Check that your data file exists and has entries for the current day
2. **File not found**: Ensure the data file path is correct relative to the project root
3. **Display not showing**: Verify the category is enabled in the configuration
4. **Wrong day content**: The system uses day of year (1-366), not calendar date

### Debugging

Check the logs for error messages:

```bash
tail -f /var/log/ledmatrix.log
```

Common log messages:
- `"OfTheDayManager initialized: Object"` - Manager loaded successfully
- `"Loaded data file for category_name: X items"` - Data file loaded
- `"Displaying category_name: title"` - Content being displayed

## Advanced Configuration

### Custom Display Colors

You can modify the colors in the `OfTheDayManager` class:

```python
self.title_color = (255, 255, 255)  # White
self.subtitle_color = (200, 200, 200)  # Light gray
self.background_color = (0, 0, 0)  # Black
```

### Custom Fonts

The system uses the same fonts as other displays:
- **Title**: `regular_font` (Press Start 2P)
- **Subtitle/Description**: `small_font` (Press Start 2P)

## Integration with Other Systems

The "Of The Day" system integrates seamlessly with:
- **Display Controller**: Automatic rotation with other displays
- **Schedule System**: Respects display schedule settings
- **Music Manager**: Properly handles music display transitions
- **Live Sports**: Prioritized over regular displays when games are live

## Performance Considerations

- Data files are loaded once at startup
- Daily content is cached and only reloaded when the date changes
- Display updates are minimal to maintain smooth performance
- Text wrapping is optimized for the LED matrix display

## Future Enhancements

Potential improvements:
- **API Integration**: Pull content from external APIs
- **User Interface**: Web interface for content management
- **Analytics**: Track which content is most engaging
- **Scheduling**: Custom schedules for different categories
- **Multi-language**: Support for different languages in the interface 