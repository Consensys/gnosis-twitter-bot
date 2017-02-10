import unittest


class TestTrader(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTrader, self).__init__(*args, **kwargs)


    def test_bot_commands(self):

        HIGHER_TRADE = 1
        LOWER_TRADE = -1

        def get_number_of_tokens_from_string(tweet_text):
            use_default_number_tokens = False
            number_of_tokens = None
            default_number_of_tokens = str(1)
            trading_type = None
            upper_text = tweet_text.upper()

            # Detect trading type
            # Check if text contains HIGHER or LOWER keyword
            upperText = upper_text.replace('@GNOSISMARKETBOT', '')
            if 'HIGHER' in upperText:
                trading_type = HIGHER_TRADE
                upperText = upperText.replace('HIGHER', '').strip()
            elif 'LOWER' in upperText:
                trading_type = LOWER_TRADE
                upperText = upperText.replace('LOWER', '').strip()
            else:
                # No valid input keyword found
                return False

            # Decode the amount of tokens invested
            # If the user doesn't provide the ETH amount
            # we consider it to be 1 ETH by default
            if trading_type == HIGHER_TRADE:
                upper_text = upper_text.replace('HIGHER', '').strip()
                if len(upper_text) == 0:
                    use_default_number_tokens = True
            else:
                upper_text = upper_text.replace('LOWER', '').strip()
                if len(upper_text) == 0:
                    use_default_number_tokens = True

            if not use_default_number_tokens:
                if 'ETH' in upper_text:
                    number_of_tokens = ''.join(upper_text.replace('ETH', '').strip().split(' '))
                else:
                    # Detect numbers
                    _numbers = [char for char in upper_text.split(' ') if char.isdigit()]

                    if len(_numbers) > 1:
                        # Adopt the default number of token value in
                        # case the user provided not valid words
                        number_of_tokens = default_number_of_tokens
                    elif len(_numbers) == 1:
                        number_of_tokens = str(_numbers[0])
                    else:
                        number_of_tokens = default_number_of_tokens
                        #''.join(upper_text.split(' '))
            else:
                number_of_tokens = default_number_of_tokens

            return [trading_type, number_of_tokens]


        commands = [
            ["higher 2eth", "2"],
            ["higher 2 eth", "2"],
            ["higher", "1"],
            ["higher hte", "1"],
            ["higher 1 hte", "1"],
            ["lower", "1"],
            ["lower 2", "2"],
            ["lower 2eth", "2"],
            ["lower", "1"],
            ["lower hte", "1"],
            ["lower 2hte", "1"],
            ["lower 1 hte", "1"]
        ]

        [self.assertEquals(get_number_of_tokens_from_string(cmd[0].upper())[1], cmd[1]) for cmd in commands]

    def test_discrete_event(self):
        pass

    def test_ranged_event(self):
        pass

if __name__=='__main__':
    unittest.main()
