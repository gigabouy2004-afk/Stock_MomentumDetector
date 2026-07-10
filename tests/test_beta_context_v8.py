import tempfile
import unittest
from pathlib import Path

import pandas as pd

import Beta_Context_V8 as beta_context


class BetaContextV8Tests(unittest.TestCase):
    def make_prices(self, beta, periods=320, noise_scale=0.0):
        index = pd.bdate_range("2024-01-02", periods=periods)
        market_returns = pd.Series(
            [0.001 + ((i % 11) - 5) * 0.0004 for i in range(periods)],
            index=index,
        )
        noise = pd.Series(
            [((i % 7) - 3) * noise_scale for i in range(periods)],
            index=index,
        )
        stock_returns = beta * market_returns + noise
        market_close = 100 * (1 + market_returns).cumprod()
        stock_close = 50 * (1 + stock_returns).cumprod()
        return pd.DataFrame({"Close": stock_close}), pd.DataFrame({"Close": market_close})

    def test_estimates_known_beta(self):
        stock, market = self.make_prices(beta=1.5, noise_scale=0.00005)
        result = beta_context.calculate_beta_context(stock, market, "SPY")
        self.assertEqual(result["Beta_Status"], "OK")
        self.assertAlmostEqual(result["Beta_252D"], 1.5, delta=0.05)
        self.assertGreater(result["Beta_R2_252D"], 0.95)

    def test_insufficient_history(self):
        stock, market = self.make_prices(beta=1.0, periods=100)
        result = beta_context.calculate_beta_context(stock, market, "SPY")
        self.assertEqual(result["Beta_Status"], "INSUFFICIENT_HISTORY")

    def test_regular_session_close_excludes_live_override(self):
        stock, market = self.make_prices(beta=1.0)
        stock["Regular_Session_Close"] = stock["Close"]
        baseline = beta_context.calculate_beta_context(stock, market, "SPY")
        stock.loc[stock.index[-1], "Close"] *= 2
        live_adjusted = beta_context.calculate_beta_context(stock, market, "SPY")
        self.assertAlmostEqual(baseline["Beta_252D"], live_adjusted["Beta_252D"], places=10)

    def test_semantic_active_trigger_is_independent_of_cli(self):
        self.assertTrue(
            beta_context.is_beta_postprocessor_eligible(
                {"Final_Decision": "MOMENTUM_ACTIVE", "Score": 85},
                85,
            )
        )
        self.assertFalse(
            beta_context.is_beta_postprocessor_eligible(
                {"Final_Decision": "MOMENTUM_PRESENT_WAIT_CONFIRMATION", "Score": 85},
                85,
            )
        )
        self.assertFalse(
            beta_context.is_beta_postprocessor_eligible(
                {"Final_Decision": "REJECT", "Score": 100},
                85,
            )
        )

    def test_message_lookup(self):
        stock, market = self.make_prices(beta=0.6, noise_scale=0.00005)
        result = beta_context.calculate_beta_context(stock, market, "SPY")
        message = beta_context.build_beta_message(result)
        self.assertIn("Active momentum confirmed", message)
        self.assertIn("Beta", message)

    def test_postprocessor_writes_message_without_changing_score(self):
        stock, market = self.make_prices(beta=1.4, noise_scale=0.00005)
        output = {"Final_Decision": "MOMENTUM_ACTIVE", "Score": 85}
        beta_context.apply_beta_postprocessor(output, stock, market, "SPY", active_threshold=85)
        self.assertEqual(output["Score"], 85)
        self.assertTrue(output["Score_Message"])

        waiting = {"Final_Decision": "MOMENTUM_PRESENT_WAIT_CONFIRMATION", "Score": 84}
        result = beta_context.apply_beta_postprocessor(waiting, stock, market, "SPY", active_threshold=85)
        self.assertIsNone(result)
        self.assertNotIn("Score_Message", waiting)


if __name__ == "__main__":
    unittest.main()
