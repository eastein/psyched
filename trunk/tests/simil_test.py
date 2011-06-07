import unittest

import psyched_backend as pb

class SimilarityTests(unittest.TestCase) :
	def assertSim(self, a, b) :
		self.assertEquals(True, pb.considered_similar(a, b))

	def assertNotSim(self, a, b) :
		self.assertEquals(False, pb.considered_similar(a, b))

	def test_empties(self) :
		self.assertSim("", "")

	def test_same_short(self) :
		self.assertSim("a", "a")
		self.assertSim("aa", "aa")
		self.assertSim("abc", "abc")
		self.assertSim("ayep", "ayep")

	def test_appended(self) :
		self.assertSim("call jim", "call jim now")
		self.assertSim("clear out trash", "clear out trash, throw away empties")
		self.assertSim("Call jim up", "Call jim on phone")

	def test_long_append(self) :
		self.assertSim("clear out trash", "clear out trash, throw away empties, sweep")

	def test_short_edits(self) :
		self.assertSim("cancel netflix", "canc netflix")
		self.assertSim("wake up", "wakeup")
		self.assertSim("WAKEUP", "wakeup")

	def test_no_total_rewrite(self) :
		self.assertNotSim("Not this.", "Bananas!!")

	def test_not_same(self) :
		self.assertNotSim("Good omens", "Fix backups")
		self.assertNotSim("Register car", "dodgeball league")
		self.assertNotSim("la bamba", "haircut today")
		self.assertNotSim("finish keepassx setup", "check MMSes somehow")
		self.assertNotSim("fix ubuntu install", "test kevin's library")
