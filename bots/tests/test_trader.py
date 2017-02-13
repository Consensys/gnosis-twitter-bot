import unittest
from subprocess import Popen, PIPE


class TestTrader(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTrader, self).__init__(*args, **kwargs)


    def test_bot_commands(self):

        HIGHER_TRADE = 1
        LOWER_TRADE = -1

        def get_trading_and_token_number_from_string(tweet_text):
            use_default_number_tokens = False
            number_of_tokens = None
            default_number_of_tokens = str(1)
            trading_type = None
            upper_text = tweet_text.upper()

            # Detect trading type
            # Check if text contains HIGHER or LOWER keyword
            upper_text = upper_text.replace('@GNOSISMARKETBOT', '')
            if 'HIGHER' in upper_text:
                trading_type = HIGHER_TRADE
                upper_text = upper_text.replace('HIGHER', '').strip()
            elif 'LOWER' in upper_text:
                trading_type = LOWER_TRADE
                upper_text = upper_text.replace('LOWER', '').strip()
            else:
                # No valid input keyword found
                return [False, False]

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
            ["lower 1 hte", "1"],
            ["1 hte", False]
        ]

        [self.assertEquals(get_trading_and_token_number_from_string(cmd[0].upper())[1], cmd[1]) for cmd in commands]


    def test_discrete_event(self):
        pass


    def test_ranged_event(self):
        pass


    def test_node_errors(self):
        MARKET_MANAGER_DIR = '../market-manager/'
        GET_MARKETS_FILE = 'getMarkets.js'
        GET_QR_FILE = 'getQR.js'

        market_hash = "fake_market_hash"
        outcome_index = 1
        market_address = "0x9b40645cbc6142cdfd5441a9ad4afde8da8ed199"
        number_of_tokens = 1

        process = Popen(["node", MARKET_MANAGER_DIR + GET_QR_FILE, market_hash, str(outcome_index), market_address, str(number_of_tokens)], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()

        self.assertTrue(exit_code==1) # code 1 means the program terminated with errors


if __name__=='__main__':
    unittest.main()
