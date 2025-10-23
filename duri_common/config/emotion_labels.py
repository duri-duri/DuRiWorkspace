"""
Emotion Labels Configuration for DuRi System

This module defines the hierarchical emotion labels used throughout the system.
Emotions are organized into three levels based on complexity and specificity.
"""

from enum import IntEnum
from typing import Dict, List, Set


class EmotionLevel(IntEnum):
    """감정 레벨 열거형"""

    LEVEL_1 = 1  # Basic emotions (primary emotions)
    LEVEL_2 = 2  # Secondary emotions (more complex, often combinations of basic emotions)
    LEVEL_3 = 3  # Tertiary emotions (most complex, often context-dependent)
    UNKNOWN = 0  # Unknown or invalid emotions


# Emotion definitions by level
EMOTION_LEVELS: Dict[EmotionLevel, List[str]] = {
    EmotionLevel.LEVEL_1: [
        "happy",
        "sad",
        "angry",
        "fear",
        "surprise",
        "disgust",
        "shame",
        "curiosity",
    ],
    EmotionLevel.LEVEL_2: ["frustration", "relief", "envy", "boredom", "pride"],
    EmotionLevel.LEVEL_3: ["regret", "guilt", "empathy", "nostalgia", "awe"],
}

# Individual level exports for backward compatibility
LEVEL_1_EMOTIONS = EMOTION_LEVELS[EmotionLevel.LEVEL_1]
LEVEL_2_EMOTIONS = EMOTION_LEVELS[EmotionLevel.LEVEL_2]
LEVEL_3_EMOTIONS = EMOTION_LEVELS[EmotionLevel.LEVEL_3]

# All emotions combined
ALL_EMOTIONS: List[str] = []
for level_emotions in EMOTION_LEVELS.values():
    ALL_EMOTIONS.extend(level_emotions)

# Create a set for faster lookups (case-insensitive)
_EMOTION_SET: Set[str] = {emotion.lower() for emotion in ALL_EMOTIONS}

# Emotion aliases for backward compatibility and user-friendly input
EMOTION_ALIASES: Dict[str, str] = {
    "joy": "happy",
    "happiness": "happy",
    "glad": "happy",
    "cheerful": "happy",
    "sadness": "sad",
    "sorrow": "sad",
    "grief": "sad",
    "anger": "angry",
    "mad": "angry",
    "furious": "angry",
    "scared": "fear",
    "afraid": "fear",
    "terrified": "fear",
    "shocked": "surprise",
    "amazed": "surprise",
    "disgusted": "disgust",
    "revolted": "disgust",
    "embarrassed": "shame",
    "ashamed": "shame",
    "curious": "curiosity",
    "wondering": "curiosity",
    "frustrated": "frustration",
    "annoyed": "frustration",
    "relieved": "relief",
    "jealous": "envy",
    "envious": "envy",
    "bored": "boredom",
    "proud": "pride",
    "regretful": "regret",
    "guilty": "guilt",
    "empathetic": "empathy",
    "nostalgic": "nostalgia",
    "awed": "awe",
    "amazed": "awe",  # noqa: F601
}


def normalize_emotion(emotion: str) -> str:
    """
    Normalize emotion input to standard emotion label.

    Args:
        emotion (str): Input emotion string

    Returns:
        str: Normalized emotion label
    """
    if not isinstance(emotion, str):
        return emotion

    emotion_lower = emotion.strip().lower()

    # Check if it's already a valid emotion
    if emotion_lower in _EMOTION_SET:
        return emotion_lower

    # Check aliases
    normalized = EMOTION_ALIASES.get(emotion_lower)
    if normalized:
        return normalized

    # Return original if no alias found
    return emotion_lower


# Create a mapping for emotion to level (case-insensitive)
_EMOTION_TO_LEVEL: Dict[str, EmotionLevel] = {}
for level, emotions in EMOTION_LEVELS.items():
    for emotion in emotions:
        _EMOTION_TO_LEVEL[emotion.lower()] = level


def is_valid_emotion(emotion: str) -> bool:
    """
    Check if the given emotion is a valid emotion label.

    Args:
        emotion (str): The emotion to validate

    Returns:
        bool: True if the emotion is valid, False otherwise
    """
    return emotion.lower() in _EMOTION_SET


def get_emotion_level(emotion: str) -> EmotionLevel:
    """
    Get the level of the given emotion.

    Args:
        emotion (str): The emotion to check

    Returns:
        EmotionLevel: The emotion level or UNKNOWN if not found
    """
    return _EMOTION_TO_LEVEL.get(emotion.lower(), EmotionLevel.UNKNOWN)


def get_emotions_by_level(level: EmotionLevel) -> List[str]:
    """
    Get all emotions for a specific level.

    Args:
        level (EmotionLevel): The level to get emotions for

    Returns:
        List[str]: List of emotions for the specified level
    """
    return EMOTION_LEVELS.get(level, []).copy()


def get_all_emotions() -> List[str]:
    """
    Get all valid emotions.

    Returns:
        List[str]: List of all valid emotions
    """
    return ALL_EMOTIONS.copy()


def get_emotion_count_by_level() -> Dict[EmotionLevel, int]:
    """
    Get the count of emotions for each level.

    Returns:
        Dict[EmotionLevel, int]: Dictionary mapping levels to emotion counts
    """
    return {level: len(emotions) for level, emotions in EMOTION_LEVELS.items()}


def get_emotion_levels() -> Dict[EmotionLevel, List[str]]:
    """
    Get all emotion levels and their emotions.

    Returns:
        Dict[EmotionLevel, List[str]]: Dictionary mapping levels to emotion lists
    """
    return {level: emotions.copy() for level, emotions in EMOTION_LEVELS.items()}


def add_emotion(emotion: str, level: EmotionLevel) -> bool:
    """
    Add a new emotion to the specified level.

    Args:
        emotion (str): The emotion to add
        level (EmotionLevel): The level to add it to

    Returns:
        bool: True if added successfully, False if emotion already exists
    """
    if is_valid_emotion(emotion):
        return False  # Emotion already exists

    EMOTION_LEVELS[level].append(emotion)
    ALL_EMOTIONS.append(emotion)
    _EMOTION_SET.add(emotion.lower())
    _EMOTION_TO_LEVEL[emotion.lower()] = level

    return True


def remove_emotion(emotion: str) -> bool:
    """
    Remove an emotion from all levels.

    Args:
        emotion (str): The emotion to remove

    Returns:
        bool: True if removed successfully, False if emotion doesn't exist
    """
    if not is_valid_emotion(emotion):
        return False  # Emotion doesn't exist

    emotion_lower = emotion.lower()
    level = _EMOTION_TO_LEVEL[emotion_lower]

    # Remove from level list
    EMOTION_LEVELS[level].remove(emotion)

    # Remove from all emotions list
    ALL_EMOTIONS.remove(emotion)

    # Remove from sets
    _EMOTION_SET.remove(emotion_lower)
    del _EMOTION_TO_LEVEL[emotion_lower]

    return True


def get_emotion_statistics() -> Dict:
    """
    Get statistics about the emotion configuration.

    Returns:
        Dict: Statistics about emotions
    """
    total_emotions = len(ALL_EMOTIONS)
    level_counts = get_emotion_count_by_level()

    return {
        "total_emotions": total_emotions,
        "level_counts": level_counts,
        "levels": {
            f"level_{level.value}": {"count": count, "emotions": EMOTION_LEVELS[level]}
            for level, count in level_counts.items()
        },
    }


# Backward compatibility functions
def get_emotion_level_int(emotion: str) -> int:
    """
    Get the level of the given emotion as an integer (for backward compatibility).

    Args:
        emotion (str): The emotion to check

    Returns:
        int: The level (1, 2, or 3) or 0 if not found
    """
    return get_emotion_level(emotion).value


def get_emotions_by_level_int(level: int) -> List[str]:
    """
    Get all emotions for a specific level by integer (for backward compatibility).

    Args:
        level (int): The level (1, 2, or 3)

    Returns:
        List[str]: List of emotions for the specified level
    """
    try:
        emotion_level = EmotionLevel(level)
        return get_emotions_by_level(emotion_level)
    except ValueError:
        return []
