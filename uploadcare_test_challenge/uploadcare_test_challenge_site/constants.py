import emoji


SOURCE_HOST = 'lifehacker.ru'
EMOJIES = [*map(
    emoji.emojize,
    [':thumbs_up:', ":red_heart:", ":star:", ":fire:"]
)]
WORD_DELIMITER_PATTERN = '([,. ])'
WORD_LENGTH = 6
