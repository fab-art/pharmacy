import unittest
from unittest.mock import MagicMock
from backend.logic.referral_manager import create_referral, initialize_case
from backend.logic.schema import COLLECTIONS

class TestReferralManager(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()

    def test_create_referral(self):
        referral_data = {'pharmacy_id': 'PHR-001', 'submitted_by': 'test@rssb.rw'}
        # Mock add() to return (timestamp, document_reference)
        mock_doc = MagicMock()
        mock_doc.id = 'REF123'
        self.db.collection().add.return_value = (None, mock_doc)

        ref_id = create_referral(self.db, referral_data)
        self.assertEqual(ref_id, 'REF123')
        self.db.collection.assert_called_with(COLLECTIONS['REFERRALS'])

if __name__ == '__main__':
    unittest.main()
