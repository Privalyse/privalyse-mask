import unittest
from privalyse_mask import PrivalyseMasker

class TestConsistency(unittest.TestCase):
    def test_consistency_across_instances(self):
        masker1 = PrivalyseMasker(languages=["en"])
        masker2 = PrivalyseMasker(languages=["en"])
        
        text = "Peter Parker"
        
        # Mask with first instance
        masked1, _ = masker1.mask(text)
        
        # Mask with second instance
        masked2, _ = masker2.mask(text)
        
        print(f"Masked 1: {masked1}")
        print(f"Masked 2: {masked2}")
        
        self.assertEqual(masked1, masked2)
        self.assertTrue(masked1.startswith("{Name_"))

    def test_consistency_within_text(self):
        masker = PrivalyseMasker(languages=["en"])
        text = "Peter Parker met Peter Parker."
        
        masked, mapping = masker.mask(text)
        print(f"Masked Text: {masked}")
        
        # Should look like "{Name_X} met {Name_X}."
        parts = masked.split(" met ")
        self.assertEqual(parts[0], parts[1][:-1]) # remove dot

    def test_seed_impact(self):
        text = "Peter Parker"
        
        # Seed A
        maskerA = PrivalyseMasker(languages=["en"], seed="ProjectA")
        maskedA, _ = maskerA.mask(text)
        
        # Seed B
        maskerB = PrivalyseMasker(languages=["en"], seed="ProjectB")
        maskedB, _ = maskerB.mask(text)
        
        print(f"Seed A: {maskedA}")
        print(f"Seed B: {maskedB}")
        
        # Should be different
        self.assertNotEqual(maskedA, maskedB)
        
        # Same seed should be same
        maskerA2 = PrivalyseMasker(languages=["en"], seed="ProjectA")
        maskedA2, _ = maskerA2.mask(text)
        self.assertEqual(maskedA, maskedA2)

if __name__ == '__main__':
    unittest.main()
