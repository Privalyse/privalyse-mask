import unittest
from unittest.mock import MagicMock, patch
from privalyse_mask.core import PrivalyseMasker
from presidio_analyzer import RecognizerResult

class TestPrivalyseMasker(unittest.TestCase):
    
    @patch('privalyse_mask.core.AnalyzerEngine')
    def test_mask_person(self, MockAnalyzer):
        # Setup mock
        mock_instance = MockAnalyzer.return_value
        # Mock results for "Peter"
        mock_instance.analyze.return_value = [
            RecognizerResult(entity_type="PERSON", start=11, end=16, score=0.85)
        ]
        
        masker = PrivalyseMasker()
        text = "My name is Peter."
        
        masked_text, mapping = masker.mask(text)
        
        # Check masked text format
        self.assertTrue(masked_text.startswith("My name is {Name_"))
        self.assertTrue(masked_text.endswith("}."))
        
        # Check mapping
        surrogate = masked_text[11:-1] # Extract {Name_...}
        self.assertIn(surrogate, mapping)
        self.assertEqual(mapping[surrogate], "Peter")
        
        # Check unmask
        unmasked = masker.unmask(masked_text, mapping)
        self.assertEqual(unmasked, text)

    @patch('privalyse_mask.core.AnalyzerEngine')
    def test_mask_date(self, MockAnalyzer):
        mock_instance = MockAnalyzer.return_value
        # "12.10.2000" -> start 0, end 10
        mock_instance.analyze.return_value = [
            RecognizerResult(entity_type="DATE_TIME", start=0, end=10, score=0.85)
        ]
        
        masker = PrivalyseMasker()
        text = "12.10.2000 is my birthday."
        
        masked_text, mapping = masker.mask(text)
        
        # Expected: {Date_October_2000} is my birthday.
        self.assertIn("{Date_October_2000}", masked_text)
        self.assertEqual(mapping["{Date_October_2000}"], "12.10.2000")
        
        unmasked = masker.unmask(masked_text, mapping)
        self.assertEqual(unmasked, text)

    @patch('privalyse_mask.core.AnalyzerEngine')
    def test_mask_iban(self, MockAnalyzer):
        mock_instance = MockAnalyzer.return_value
        iban = "DE93 3432 2346 4355"
        mock_instance.analyze.return_value = [
            RecognizerResult(entity_type="IBAN_CODE", start=0, end=len(iban), score=1.0)
        ]
        
        masker = PrivalyseMasker()
        text = f"{iban} is my IBAN."
        
        masked_text, mapping = masker.mask(text)
        
        self.assertIn("{German_IBAN}", masked_text)
        self.assertEqual(mapping["{German_IBAN}"], iban)

    @patch('privalyse_mask.core.AnalyzerEngine')
    def test_mask_german_id(self, MockAnalyzer):
        mock_instance = MockAnalyzer.return_value
        id_card = "T220001293"
        prefix = "My ID is "
        start_index = len(prefix)
        end_index = start_index + len(id_card)
        
        mock_instance.analyze.return_value = [
            RecognizerResult(entity_type="DE_ID_CARD", start=start_index, end=end_index, score=0.6)
        ]
        
        masker = PrivalyseMasker()
        text = f"{prefix}{id_card}"
        
        masked_text, mapping = masker.mask(text)
        
        self.assertIn("{German_ID}", masked_text)
        self.assertEqual(mapping["{German_ID}"], id_card)

if __name__ == '__main__':
    unittest.main()
